"""
wa_inbound.py — Webhook receiver de Evolution API + sender hacia Evolution.

Endpoints expuestos (registrados en main.py):
  POST /wa/evolution/webhook   — Evolution llama aquí con cada evento
  POST /wa/evolution/webhook/  — alias con slash
  GET  /wa/health              — quick health para debugging

Filosofía:
- Responder 200 lo más rápido posible (Evolution timeout es corto).
- Persistir el evento crudo siempre (auditoría).
- Procesamiento IA en thread separado (no bloquea el webhook).
- Idempotente por evolution_message_id (Evolution puede reintentar).
"""

from __future__ import annotations

import json
import os
import random
import threading
import time
import urllib.parse
import urllib.request
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Request, HTTPException

try:
    from app import db as db_mod
    from app import wa_brain
    from app import wa_mode
except ImportError:
    import db as db_mod  # type: ignore
    import wa_brain      # type: ignore
    import wa_mode       # type: ignore


router = APIRouter(prefix="/wa", tags=["whatsapp"])


# ── Config Evolution (env vars) ──────────────────────────────────────────────

def _evo_url() -> str:
    return (os.environ.get("EVOLUTION_API_URL", "http://2.24.212.56:8080").rstrip("/"))


def _evo_key() -> str:
    return os.environ.get("EVOLUTION_API_KEY", "").strip()


def _evo_instance() -> str:
    return (
        os.environ.get("EVOLUTION_INSTANCE")
        or db_mod.wa_config_get("evolution_instance", "abogados-hseq")
    )


# ── Sender: enviar texto a un número vía Evolution API ──────────────────────

def _http_post_json(url: str, body: dict, timeout: int = 15) -> dict:
    """Wrapper HTTP POST con apikey. Devuelve {ok, status, response|error}."""
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "apikey": _evo_key(),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return {"ok": True, "status": resp.status, "response": raw[:1500]}
    except Exception as e:
        return {"ok": False, "error": str(e)[:300]}


def enviar_presence(phone: str, presence: str = "composing",
                    delay_ms: int = 3000, *, instance: Optional[str] = None) -> dict:
    """Envía indicador de presencia ('composing' = 'escribiendo...', 'paused', 'available')."""
    inst = instance or _evo_instance()
    url = f"{_evo_url()}/chat/sendPresence/{inst}"
    body = {
        "number": db_mod._norm_phone(phone),
        "delay": int(delay_ms),
        "presence": presence,
    }
    return _http_post_json(url, body, timeout=8)


def marcar_leido(remote_jid: str, message_id: str,
                 *, instance: Optional[str] = None) -> dict:
    """Marca un mensaje como leído (doble check azul). Mejora naturalidad."""
    inst = instance or _evo_instance()
    url = f"{_evo_url()}/chat/markMessageAsRead/{inst}"
    body = {
        "readMessages": [
            {"remoteJid": remote_jid, "fromMe": False, "id": message_id}
        ],
    }
    return _http_post_json(url, body, timeout=8)


def _calcular_delay_typing_ms(text: str) -> int:
    """Tiempo realista de tipeo humano + variación (~30-40 wpm).

    Base 1.4s + 230ms/palabra, capped en 11s, ±20% jitter.
    """
    words = max(1, len(text.split()))
    base = 1400 + words * 230
    base = min(base, 11000)
    return int(base * (0.85 + 0.3 * random.random()))


def enviar_texto(phone: str, text: str, *, instance: Optional[str] = None,
                 humanizar: bool = True) -> dict:
    """Envía texto con presencia 'composing' previa para parecer humano.

    Si humanizar=False, envía directo (útil para tests/admin/notificaciones internas).
    """
    if not text:
        return {"ok": False, "error": "empty_text"}
    inst = instance or _evo_instance()
    phone_n = db_mod._norm_phone(phone)

    if humanizar:
        # 1) "escribiendo..." durante delay calculado
        delay_ms = _calcular_delay_typing_ms(text)
        try:
            enviar_presence(phone_n, "composing", delay_ms, instance=inst)
        except Exception:
            pass  # presence falla → seguir igual
        # 2) Esperar (bloqueante en el thread async, no en el webhook)
        time.sleep(delay_ms / 1000.0)

    # 3) Enviar el texto
    url = f"{_evo_url()}/message/sendText/{inst}"
    body = {"number": phone_n, "text": text}
    return _http_post_json(url, body, timeout=15)


def enviar_segmentos(phone: str, segmentos: list[str],
                     *, instance: Optional[str] = None) -> list[dict]:
    """Envía varios mensajes cortos como una persona real, con pausa entre cada uno."""
    out = []
    for i, seg in enumerate(segmentos):
        if not seg or not seg.strip():
            continue
        if i > 0:
            # Pausa corta natural entre mensajes consecutivos (0.6 - 1.6s)
            time.sleep(0.6 + random.random() * 1.0)
        out.append(enviar_texto(phone, seg.strip(), instance=instance, humanizar=True))
    return out


# ── Parseo de eventos Evolution ──────────────────────────────────────────────

def _extract_message(payload: dict) -> Optional[dict]:
    """Convierte el payload bruto de Evolution en un dict mínimo del mensaje.

    Devuelve None si el evento no es procesable como mensaje entrante.
    """
    event = (payload.get("event") or "").lower()
    data = payload.get("data") or {}

    if event != "messages.upsert" and event.replace(".", "_") != "messages_upsert":
        return None

    key = data.get("key") or {}
    remote_jid = key.get("remoteJid") or ""
    from_me = bool(key.get("fromMe"))

    # Filtramos los que enviamos NOSOTROS y los grupos por ahora
    if from_me or remote_jid.endswith("@g.us"):
        return None

    msg_id = key.get("id") or ""
    msg_obj = data.get("message") or {}

    # Extraer contenido por tipo
    text = None
    kind = "unknown"
    media_url = None
    mime_type = None
    filename = None

    if msg_obj.get("conversation"):
        kind = "text"
        text = msg_obj["conversation"]
    elif msg_obj.get("extendedTextMessage", {}).get("text"):
        kind = "text"
        text = msg_obj["extendedTextMessage"]["text"]
    elif msg_obj.get("imageMessage"):
        kind = "image"
        text = msg_obj["imageMessage"].get("caption") or ""
        mime_type = msg_obj["imageMessage"].get("mimetype")
        media_url = msg_obj["imageMessage"].get("url")
    elif msg_obj.get("documentMessage"):
        kind = "document"
        text = msg_obj["documentMessage"].get("caption") or ""
        mime_type = msg_obj["documentMessage"].get("mimetype")
        filename = msg_obj["documentMessage"].get("fileName")
        media_url = msg_obj["documentMessage"].get("url")
    elif msg_obj.get("audioMessage"):
        kind = "audio"
        mime_type = msg_obj["audioMessage"].get("mimetype")
        media_url = msg_obj["audioMessage"].get("url")
    elif msg_obj.get("videoMessage"):
        kind = "video"
        text = msg_obj["videoMessage"].get("caption") or ""
        mime_type = msg_obj["videoMessage"].get("mimetype")
        media_url = msg_obj["videoMessage"].get("url")
    elif msg_obj.get("stickerMessage"):
        kind = "sticker"
    elif msg_obj.get("locationMessage"):
        kind = "location"
        loc = msg_obj["locationMessage"]
        text = f"lat={loc.get('degreesLatitude')},lng={loc.get('degreesLongitude')}"
    else:
        return None  # tipo no soportado

    ts = data.get("messageTimestamp") or 0
    if isinstance(ts, (int, float)):
        ts_iso = datetime.fromtimestamp(ts).isoformat(timespec="seconds")
    else:
        ts_iso = str(ts)

    return {
        "evolution_message_id": msg_id,
        "phone": remote_jid,
        "kind": kind,
        "text": text,
        "mime_type": mime_type,
        "filename": filename,
        "media_url": media_url,
        "ts": ts_iso,
        "push_name": data.get("pushName"),
    }


# ── Procesamiento (en background) ────────────────────────────────────────────

def _procesar_async(payload: dict) -> None:
    """Corre en thread separado: clasifica con IA y responde como humano."""
    try:
        msg = _extract_message(payload)
        if not msg:
            return  # evento no procesable

        # Idempotencia
        if msg["evolution_message_id"] and db_mod.wa_msg_exists(msg["evolution_message_id"]):
            return

        # Conversación (crear si no existe)
        conv = db_mod.wa_conv_get_or_create(msg["phone"])

        # Capturar push_name si no tenemos nombre aún
        push_name = (msg.get("push_name") or "").strip()
        datos_actuales = conv.get("datos_capturados") or {}
        if push_name and not datos_actuales.get("nombre"):
            db_mod.wa_conv_update(
                conv["id"],
                datos_capturados={"nombre_wa": push_name},
            )

        # Persistir mensaje entrante
        msg_id_db = db_mod.wa_msg_save(
            evolution_message_id=msg["evolution_message_id"],
            conversation_id=conv["id"],
            phone=msg["phone"],
            direction="in",
            kind=msg["kind"],
            text=msg["text"],
            media_url=msg["media_url"],
            mime_type=msg["mime_type"],
            filename=msg["filename"],
            raw_event=payload,
            ts=msg["ts"],
        )
        if msg_id_db is None:
            return  # duplicado

        db_mod.wa_conv_inc_msg_count(conv["id"])

        # Marcar mensaje como leído (doble check azul) — naturalidad humana
        try:
            remote_jid = (payload.get("data") or {}).get("key", {}).get("remoteJid", "")
            if remote_jid and msg["evolution_message_id"]:
                marcar_leido(remote_jid, msg["evolution_message_id"])
        except Exception:
            pass

        # Pequeña pausa antes de "leer y procesar" (humano: ve el mensaje, piensa)
        time.sleep(1.0 + random.random() * 1.5)  # 1.0-2.5s

        # Releer la conversación con datos_capturados frescos
        conv = db_mod.wa_conv_get_by_phone(msg["phone"]) or conv

        # Orquestar (Gemini decide qué responder y cómo)
        decision = wa_brain.procesar_mensaje_entrante(
            conv, msg_id_db, msg["text"] or "", kind=msg["kind"]
        )

        # Actualizar datos capturados + intención + transición
        updates: dict[str, Any] = {}
        if decision.get("datos_extraidos"):
            updates["datos_capturados"] = decision["datos_extraidos"]
        if decision.get("intencion"):
            updates["ultima_intencion"] = decision["intencion"]
        if decision.get("transicion_estado"):
            updates["estado"] = decision["transicion_estado"]
        if updates:
            db_mod.wa_conv_update(conv["id"], **updates)

        db_mod.wa_msg_set_ai(msg_id_db, decision.get("intencion") or "INSEGURO")

        # Escalar si la IA lo pide o modo=humano
        if decision.get("escalar") or decision.get("modo_aplicado") == "humano":
            db_mod.wa_escalate(
                conversation_id=conv["id"],
                lawyer_id=conv.get("assigned_lawyer_id"),
                reason=decision.get("razon_escalada") or decision.get("modo_aplicado"),
            )

        # Enviar respuesta(s)
        # wa_brain devuelve `respuesta` (str) o `respuestas` (list[str] = segmentos cortos)
        segs = decision.get("respuestas") or []
        if not segs and decision.get("respuesta"):
            segs = [decision["respuesta"]]

        if segs:
            results = enviar_segmentos(msg["phone"], segs)
            for i, (seg, res) in enumerate(zip(segs, results)):
                if not res.get("ok"):
                    print(f"[wa_inbound] error enviando seg {i}: {res.get('error')}")
                    continue
                evo_resp_id = None
                try:
                    parsed = json.loads(res.get("response") or "{}")
                    evo_resp_id = (parsed.get("key") or {}).get("id")
                except Exception:
                    pass
                db_mod.wa_msg_save(
                    evolution_message_id=evo_resp_id,
                    conversation_id=conv["id"],
                    phone=msg["phone"],
                    direction="out",
                    kind="text",
                    text=seg,
                    raw_event={"sent_via": "evolution", "segment": i},
                    ts=datetime.now().isoformat(timespec="seconds"),
                )
            db_mod.wa_conv_update(
                conv["id"],
                ultima_respuesta_at=datetime.now().isoformat(timespec="seconds"),
            )

    except Exception as e:
        print(f"[wa_inbound] error procesando webhook: {e}")
        import traceback
        traceback.print_exc()


# ── Endpoints HTTP ───────────────────────────────────────────────────────────

@router.post("/evolution/webhook")
@router.post("/evolution/webhook/")
async def evolution_webhook(request: Request):
    """Webhook que registra Evolution API. Responde 200 rápido."""
    try:
        payload = await request.json()
    except Exception:
        # Evolution a veces manda body vacío en eventos de control
        return {"ok": True, "skipped": "empty_or_invalid_body"}

    # Filtrar eventos que no nos interesan rápido
    event = (payload.get("event") or "").lower()
    if event in ("messages.update", "messages_update", "presence.update", "presence_update"):
        return {"ok": True, "skipped": event}

    # Solo procesamos messages.upsert (entrantes)
    if event not in ("messages.upsert", "messages_upsert", "connection.update", "connection_update"):
        return {"ok": True, "skipped": event}

    # Procesamiento async para no bloquear el webhook (Evolution tiene timeout corto)
    if event in ("messages.upsert", "messages_upsert"):
        threading.Thread(target=_procesar_async, args=(payload,), daemon=True).start()

    return {"ok": True, "event": event}


@router.get("/health")
async def wa_health():
    """Quick health: cuenta de conversaciones y último mensaje."""
    cfg = db_mod.wa_config_get_all()
    convs = db_mod.wa_conv_list(limit=1)
    return {
        "ok": True,
        "evolution_instance": _evo_instance(),
        "evolution_url": _evo_url(),
        "evolution_key_present": bool(_evo_key()),
        "gemini_key_present": bool((os.environ.get("GEMINI_API_KEY") or "").strip()),
        "mode_global": cfg.get("mode_global"),
        "ai_disabled": cfg.get("ai_disabled"),
        "office_hours": f"{cfg.get('office_hours_start')}-{cfg.get('office_hours_end')}",
        "office_days": cfg.get("office_days"),
        "last_conversation": (
            {"phone": convs[0]["phone"], "estado": convs[0]["estado"], "msgs": convs[0]["mensajes_count"]}
            if convs else None
        ),
    }


@router.post("/test-send")
async def wa_test_send(request: Request):
    """Helper para probar envío. Body: {phone, text}.

    Protegido por env var WA_TEST_TOKEN o el ADMIN_PASS si no hay token.
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(400, "json inválido")

    expected = os.environ.get("WA_TEST_TOKEN") or os.environ.get("ADMIN_PASS", "")
    auth = request.headers.get("X-Auth-Token", "")
    if not expected or auth != expected:
        raise HTTPException(401, "no autorizado")

    phone = (body.get("phone") or "").strip()
    text = (body.get("text") or "").strip()
    if not phone or not text:
        raise HTTPException(400, "phone y text requeridos")

    res = enviar_texto(phone, text)
    return res
