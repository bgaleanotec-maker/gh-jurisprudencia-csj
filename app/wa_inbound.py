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
import logging
import os
import random
import threading
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime
from typing import Any, Optional

# Logger con prefijo claro para trazar el pipeline en Render
log = logging.getLogger("wa")
if not log.handlers:
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter("[wa %(levelname)s %(asctime)s] %(message)s",
                                     datefmt="%H:%M:%S"))
    log.addHandler(h)
    log.setLevel(logging.INFO)


# ── Lock por phone para serializar mensajes consecutivos del mismo cliente ──
# Cuando un cliente manda 3 mensajes seguidos, evita que 3 threads concurrentes
# pisen la BD y se generen respuestas duplicadas/desordenadas.
_PHONE_LOCKS: dict[str, threading.Lock] = defaultdict(threading.Lock)
_PHONE_LOCKS_GUARD = threading.Lock()


def _get_phone_lock(phone: str) -> threading.Lock:
    with _PHONE_LOCKS_GUARD:
        return _PHONE_LOCKS[phone]

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
    """Corre en thread separado: clasifica con IA y responde como humano.

    Garantías:
    - Serializado por phone (lock): mensajes consecutivos del mismo cliente
      se procesan en orden, no en paralelo.
    - Cada paso loggea y captura excepciones por separado.
    - Outbound se persiste en BD ANTES de mandarlo a Evolution (optimista),
      para que el contexto exista incluso si el envío falla o el thread crashea.
    """
    msg = None
    try:
        msg = _extract_message(payload)
    except Exception as e:
        log.error("extract_message falló: %s | payload=%s", e, str(payload)[:300])
        return
    if not msg:
        log.info("evento ignorado (no es msg procesable): event=%s",
                 (payload.get("event") or "?"))
        return

    phone = msg["phone"]
    evo_id = msg.get("evolution_message_id") or ""
    log.info("INBOUND phone=%s id=%s kind=%s text=%r",
             phone, evo_id[:20], msg["kind"], (msg["text"] or "")[:80])

    # Idempotencia rápida fuera del lock (dedup por ID)
    try:
        if evo_id and db_mod.wa_msg_exists(evo_id):
            log.info("DEDUP id=%s ya existía, salgo", evo_id[:20])
            return
    except Exception as e:
        log.error("wa_msg_exists falló: %s", e)

    # ─── Lock por phone ─── serializa procesamiento del mismo cliente
    with _get_phone_lock(phone):
        try:
            _procesar_locked(payload, msg)
        except Exception as e:
            log.exception("error procesando phone=%s: %s", phone, e)


def _procesar_locked(payload: dict, msg: dict) -> None:
    """Cuerpo del procesamiento — corre con el lock del phone tomado."""
    phone = msg["phone"]
    evo_id = msg.get("evolution_message_id") or ""

    # Re-check idempotencia DENTRO del lock (otro thread pudo haberlo guardado)
    if evo_id and db_mod.wa_msg_exists(evo_id):
        log.info("DEDUP-IN-LOCK id=%s, salgo", evo_id[:20])
        return

    # 1) Conv
    try:
        conv = db_mod.wa_conv_get_or_create(phone)
    except Exception as e:
        log.error("wa_conv_get_or_create falló: %s", e)
        return

    # 2) Capturar push_name
    push_name = (msg.get("push_name") or "").strip()
    datos_actuales = conv.get("datos_capturados") or {}
    if push_name and not datos_actuales.get("nombre") and not datos_actuales.get("nombre_wa"):
        try:
            db_mod.wa_conv_update(conv["id"], datos_capturados={"nombre_wa": push_name})
            log.info("push_name capturado: %s", push_name)
        except Exception as e:
            log.error("update push_name falló: %s", e)

    # 3) Persistir entrante
    try:
        msg_id_db = db_mod.wa_msg_save(
            evolution_message_id=evo_id or None,
            conversation_id=conv["id"],
            phone=phone,
            direction="in",
            kind=msg["kind"],
            text=msg["text"],
            media_url=msg["media_url"],
            mime_type=msg["mime_type"],
            filename=msg["filename"],
            raw_event=payload,
            ts=msg["ts"],
        )
    except Exception as e:
        log.exception("wa_msg_save IN falló: %s", e)
        return
    if msg_id_db is None:
        log.info("INBOUND duplicado al guardar, salgo")
        return
    try:
        db_mod.wa_conv_inc_msg_count(conv["id"])
    except Exception as e:
        log.error("inc_msg_count falló: %s", e)

    # 4) Marcar leído (best-effort)
    try:
        remote_jid = (payload.get("data") or {}).get("key", {}).get("remoteJid", "")
        if remote_jid and evo_id:
            marcar_leido(remote_jid, evo_id)
    except Exception as e:
        log.warning("marcar_leido falló (no crítico): %s", e)

    # 5) Pausa pre-pensar
    time.sleep(1.0 + random.random() * 1.5)

    # 6) Releer conv con datos frescos
    try:
        conv = db_mod.wa_conv_get_by_phone(phone) or conv
    except Exception as e:
        log.error("wa_conv_get_by_phone falló: %s", e)

    # 7) Brain (puede tardar 3-7s con Gemini)
    log.info("BRAIN-IN conv=%s estado=%s datos=%s",
             conv["id"], conv["estado"], list((conv.get("datos_capturados") or {}).keys()))
    try:
        decision = wa_brain.procesar_mensaje_entrante(
            conv, msg_id_db, msg["text"] or "", kind=msg["kind"]
        )
    except Exception as e:
        log.exception("brain falló: %s", e)
        return
    log.info("BRAIN-OUT intencion=%s modo=%s segs=%d transicion=%s escalar=%s fb=%s",
             decision.get("intencion"), decision.get("modo_aplicado"),
             len(decision.get("respuestas") or []),
             decision.get("transicion_estado"), decision.get("escalar"),
             decision.get("usado_fallback"))

    # 8) Actualizar datos / intención / transición
    updates: dict[str, Any] = {}
    if decision.get("datos_extraidos"):
        updates["datos_capturados"] = decision["datos_extraidos"]
    if decision.get("intencion"):
        updates["ultima_intencion"] = decision["intencion"]
    if decision.get("transicion_estado"):
        updates["estado"] = decision["transicion_estado"]
    if updates:
        try:
            db_mod.wa_conv_update(conv["id"], **updates)
        except Exception as e:
            log.error("wa_conv_update falló: %s", e)

    try:
        db_mod.wa_msg_set_ai(msg_id_db, decision.get("intencion") or "INSEGURO")
    except Exception:
        pass

    # 9) Escalar si aplica
    if decision.get("escalar") or decision.get("modo_aplicado") == "humano":
        try:
            db_mod.wa_escalate(
                conversation_id=conv["id"],
                lawyer_id=conv.get("assigned_lawyer_id"),
                reason=decision.get("razon_escalada") or decision.get("modo_aplicado"),
            )
            log.info("ESCALADO razon=%s", decision.get("razon_escalada") or decision.get("modo_aplicado"))
        except Exception as e:
            log.error("escalate falló: %s", e)

    # 10) Enviar respuesta(s) — OPTIMISTA: persistir antes de enviar
    segs = decision.get("respuestas") or []
    if not segs and decision.get("respuesta"):
        segs = [decision["respuesta"]]
    if not segs:
        log.info("SIN-RESPUESTA (modo=%s)", decision.get("modo_aplicado"))
        return

    log.info("ENVIANDO %d segmento(s) a %s", len(segs), phone)
    for i, seg in enumerate(segs):
        seg = (seg or "").strip()
        if not seg:
            continue
        # 10a) Persistir OUTBOUND ANTES de enviar (contexto garantizado)
        out_msg_id = None
        try:
            out_msg_id = db_mod.wa_msg_save(
                evolution_message_id=None,  # se actualizaría después si quisiéramos
                conversation_id=conv["id"],
                phone=phone,
                direction="out",
                kind="text",
                text=seg,
                raw_event={"sent_via": "evolution", "segment": i, "pending_send": True},
                ts=datetime.now().isoformat(timespec="seconds"),
            )
        except Exception as e:
            log.error("wa_msg_save OUT (preview) falló seg %d: %s", i, e)

        # 10b) Pausa entre segmentos consecutivos (no antes del primero)
        if i > 0:
            time.sleep(0.6 + random.random() * 1.0)

        # 10c) Enviar via Evolution con typing humano
        res = enviar_texto(phone, seg, humanizar=True)
        if res.get("ok"):
            log.info("OUT seg %d/%d enviado OK", i + 1, len(segs))
        else:
            log.error("OUT seg %d/%d FALLÓ: %s", i + 1, len(segs), res.get("error"))

    # 11) Marcar timestamp de última respuesta
    try:
        db_mod.wa_conv_update(
            conv["id"],
            ultima_respuesta_at=datetime.now().isoformat(timespec="seconds"),
        )
    except Exception as e:
        log.error("update ultima_respuesta_at falló: %s", e)
    log.info("DONE phone=%s", phone)


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
