#!/usr/bin/env python3
"""
============================================================
MOTOR RAG JURISPRUDENCIA CSJ — v2 (Galeano Herrera | Abogados)
============================================================
RAG híbrido para jurisprudencia colombiana:

  • Embeddings: Google text-embedding-004 (768 dim)
  • Vector store: FAISS local (Inner Product = coseno)
  • Generación: gemini-2.0-flash con prompts especializados
  • Búsqueda híbrida: BM25 (léxico) + dense (semántico) + RRF
  • MMR para diversidad de fichas recuperadas
  • Query expansion con sinónimos jurídicos colombianos
  • Re-ranking opcional con LLM (juez)
  • Filtros por sala, año, área
  • Cache de embeddings de queries

FLUJO:
  1. Indexar (1 vez): python rag_motor.py --indexar
  2. Consultar:        python rag_motor.py "EPS niega medicamento"
  3. Caso completo:    python rag_motor.py --caso "..."
  4. Generar tutela:   python rag_motor.py --tutela "..."

USO COMO MÓDULO:
  from rag_motor import MotorRAG
  motor = MotorRAG(api_key="AIza...")
  res = motor.consultar("EPS negó cirugía prescrita")
============================================================
"""

from __future__ import annotations

import argparse
import json
import math
import os
import pickle
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Optional

# ── Dependencias opcionales ────────────────────────────────────────────────────
try:
    import numpy as np
    NP_OK = True
except ImportError:
    NP_OK = False

try:
    import faiss
    FAISS_OK = True
except ImportError:
    FAISS_OK = False

try:
    from google import genai
    from google.genai import types as genai_types
    GENAI_OK = True
    GENAI_NEW = True
except ImportError:
    try:
        import google.generativeai as genai  # legacy SDK
        genai_types = None
        GENAI_OK = True
        GENAI_NEW = False
    except ImportError:
        GENAI_OK = False
        GENAI_NEW = False

# ── Rutas ──────────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent.parent
INDEX_FILE  = BASE_DIR / "indices" / "fichas_index.jsonl"
FAISS_INDEX = BASE_DIR / "indices" / "faiss.index"
FICHAS_META = BASE_DIR / "indices" / "faiss_meta.pkl"
BM25_FILE   = BASE_DIR / "indices" / "bm25.pkl"
CONFIG_FILE = BASE_DIR / "config.json"
INVALID_FLG = BASE_DIR / "indices" / "faiss_invalido.flag"

# ── Modelos / parámetros ───────────────────────────────────────────────────────
EMBED_MODEL  = "gemini-embedding-001"
GEN_MODEL    = "gemini-2.0-flash"
RERANK_MODEL = "gemini-2.0-flash"

EMBED_DIM     = 768           # gemini-embedding-001 acepta MRL: 3072/1536/768
TOP_K         = 6           # fichas finales en el contexto
TOP_K_DENSE   = 25          # candidatos densos
TOP_K_BM25    = 25          # candidatos BM25
MMR_LAMBDA    = 0.65        # 1.0 = solo relevancia, 0.0 = solo diversidad
RRF_K         = 60          # constante de Reciprocal Rank Fusion
BATCH_SIZE    = 100
MAX_OUT_TOK   = 1100

# ── Sinónimos jurídicos colombianos para expansión de query ───────────────────
SINONIMOS = {
    "eps": ["entidad promotora de salud", "asegurador", "régimen contributivo"],
    "ips": ["institución prestadora de salud", "clínica", "hospital"],
    "tutela": ["acción de tutela", "amparo", "acción constitucional"],
    "pension": ["pensión", "prestación", "mesada", "auxilio"],
    "colpensiones": ["administradora de pensiones", "afp", "régimen prima media"],
    "despido": ["terminación", "desvinculación", "ruptura del contrato"],
    "embarazo": ["maternidad", "fuero materno", "estado de gestación", "lactancia"],
    "minimo vital": ["mínimo vital", "subsistencia", "ingreso de subsistencia"],
    "fotomulta": ["comparendo", "infracción de tránsito", "sanción de tránsito"],
    "cobro coactivo": ["jurisdicción coactiva", "ejecución fiscal", "embargo"],
    "soat": ["seguro obligatorio", "póliza de tránsito"],
    "insolvencia": ["régimen de insolvencia", "ley 1564", "persona natural no comerciante"],
    "mora": ["dilación", "demora", "plazo razonable"],
    "incapacidad": ["incapacidad médica", "subsidio por incapacidad"],
    "salario": ["remuneración", "ingreso laboral"],
    "discapacidad": ["estabilidad laboral reforzada", "fuero de salud"],
}

# Palabras vacías frecuentes en español jurídico (stopwords compactas)
STOPWORDS = {
    "a","ante","bajo","cabe","con","contra","de","desde","durante","en","entre","hacia","hasta",
    "mediante","para","por","según","sin","so","sobre","tras","versus","via","vía",
    "el","la","los","las","un","una","unos","unas","lo",
    "y","e","o","u","ni","que","como","cuando","donde","si","no",
    "del","al","es","son","fue","ser","sea","ha","han","hay","muy","más","menos",
    "se","su","sus","le","les","me","mi","tu","te","yo","él","ella","ellos","ellas","nos",
    "este","esta","estos","estas","ese","esa","esos","esas","aquel","aquella",
}


# ── Configuración ─────────────────────────────────────────────────────────────

def cargar_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}


def guardar_config(datos: dict) -> None:
    cfg = cargar_config()
    cfg.update(datos)
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")


def obtener_api_key() -> Optional[str]:
    """Prioridad: variable de entorno → config.json."""
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if key:
        return key.strip()
    cfg = cargar_config()
    val = cfg.get("gemini_api_key")
    return val.strip() if val else None


# ── Tokenización + BM25 ───────────────────────────────────────────────────────

_TOKEN_RE = re.compile(r"[a-záéíóúüñ0-9]+", re.IGNORECASE)


def _normalizar(texto: str) -> str:
    if not texto:
        return ""
    texto = texto.lower()
    # Quitar acentos sólo para la tokenización del índice (mantenemos en display)
    repl = (("á","a"),("é","e"),("í","i"),("ó","o"),("ú","u"),("ü","u"),("ñ","n"))
    for a,b in repl:
        texto = texto.replace(a,b)
    return texto


def tokenizar(texto: str) -> list[str]:
    norm = _normalizar(texto)
    return [t for t in _TOKEN_RE.findall(norm) if t not in STOPWORDS and len(t) > 2]


class BM25:
    """BM25 Okapi minimalista, sin dependencias externas."""

    def __init__(self, docs_tokens: list[list[str]], k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.N = len(docs_tokens)
        self.doc_len = [len(d) for d in docs_tokens]
        self.avgdl = (sum(self.doc_len) / self.N) if self.N else 0.0
        self.tf: list[dict[str,int]] = [Counter(d) for d in docs_tokens]
        df: dict[str,int] = defaultdict(int)
        for tokens in (set(d) for d in docs_tokens):
            for t in tokens:
                df[t] += 1
        # IDF de BM25+ con suavizado
        self.idf = {
            t: math.log(1 + (self.N - n + 0.5) / (n + 0.5))
            for t, n in df.items()
        }

    def score(self, query_tokens: Iterable[str], idx: int) -> float:
        score = 0.0
        tf = self.tf[idx]
        dl = self.doc_len[idx] or 1
        for t in query_tokens:
            if t not in tf:
                continue
            idf = self.idf.get(t, 0.0)
            num = tf[t] * (self.k1 + 1)
            den = tf[t] + self.k1 * (1 - self.b + self.b * dl / (self.avgdl or 1))
            score += idf * num / den
        return score

    def topk(self, query: str, k: int = 25) -> list[tuple[int, float]]:
        qts = tokenizar(query)
        # Solo recorremos docs que contengan al menos 1 término (índice invertido on-the-fly)
        candidatos = set()
        for t in qts:
            for i, tf in enumerate(self.tf):
                if t in tf:
                    candidatos.add(i)
        scored = [(i, self.score(qts, i)) for i in candidatos]
        scored.sort(key=lambda x: -x[1])
        return scored[:k]


# ── Motor RAG ──────────────────────────────────────────────────────────────────

class MotorRAG:
    """
    RAG híbrido para jurisprudencia.

    >>> motor = MotorRAG(api_key="AIza...")
    >>> motor.consultar("EPS negó cirugía prescrita")["respuesta"]
    """

    def __init__(self,
                 api_key: Optional[str] = None,
                 top_k: int = TOP_K,
                 solo_busqueda: bool = False):
        self.api_key   = api_key or obtener_api_key()
        self.top_k     = top_k
        self.index     = None
        self.meta: list[dict] = []
        self.bm25: Optional[BM25] = None
        self._listo    = False                 # FAISS válido
        self._client   = None
        self._cache_q: dict[str, "np.ndarray"] = {}

        if not self.api_key and not solo_busqueda:
            raise ValueError(
                "API key de Gemini no configurada.\n"
                "Opciones:\n"
                "  • export GEMINI_API_KEY=AIza...\n"
                "  • python rag_motor.py --config-key AIza...\n"
            )

        if self.api_key and GENAI_OK:
            if GENAI_NEW:
                self._client = genai.Client(api_key=self.api_key)
            else:
                genai.configure(api_key=self.api_key)
                self._client = genai

        self._cargar_meta()
        self._cargar_indices()

    # ── Carga de datos ────────────────────────────────────────────────────────

    def _cargar_meta(self) -> None:
        if FICHAS_META.exists():
            try:
                with open(FICHAS_META, "rb") as f:
                    self.meta = pickle.load(f)
                return
            except Exception:
                pass
        if INDEX_FILE.exists():
            fichas = []
            with open(INDEX_FILE, encoding="utf-8") as f:
                for linea in f:
                    try:
                        fichas.append(json.loads(linea))
                    except json.JSONDecodeError:
                        continue
            self.meta = fichas

    def _cargar_indices(self) -> None:
        # Cargar BM25 (siempre disponible si hay metadatos)
        if BM25_FILE.exists():
            try:
                with open(BM25_FILE, "rb") as f:
                    self.bm25 = pickle.load(f)
            except Exception:
                self.bm25 = None
        if self.bm25 is None and self.meta:
            self.bm25 = BM25([tokenizar(f.get("texto_busqueda","")) for f in self.meta])
            try:
                BM25_FILE.parent.mkdir(parents=True, exist_ok=True)
                with open(BM25_FILE, "wb") as f:
                    pickle.dump(self.bm25, f)
            except Exception:
                pass

        # Cargar FAISS sólo si es válido
        if INVALID_FLG.exists():
            return
        if FAISS_INDEX.exists() and FAISS_OK:
            try:
                self.index = faiss.read_index(str(FAISS_INDEX))
                self._listo = True
            except Exception:
                self._listo = False

    # ── Indexación ────────────────────────────────────────────────────────────

    def indexar(self, forzar: bool = False) -> int:
        """
        Genera embeddings con text-embedding-004 y construye FAISS + BM25.
        """
        if not (FAISS_OK and GENAI_OK and NP_OK):
            print("Faltan deps: faiss-cpu, google-genai, numpy")
            return 0
        if FAISS_INDEX.exists() and not forzar and not INVALID_FLG.exists():
            print("✓ Índice FAISS ya existe. Usa --forzar para regenerar.")
            return len(self.meta)
        if not INDEX_FILE.exists():
            print(f"❌ {INDEX_FILE} no existe. Ejecuta extraer_fichas.py primero.")
            return 0

        fichas: list[dict] = []
        with open(INDEX_FILE, encoding="utf-8") as f:
            for linea in f:
                try:
                    fichas.append(json.loads(linea))
                except json.JSONDecodeError:
                    continue

        print(f"Generando embeddings para {len(fichas)} fichas con {EMBED_MODEL}…")
        embeddings: list[list[float]] = []
        for i in range(0, len(fichas), BATCH_SIZE):
            lote = fichas[i:i+BATCH_SIZE]
            textos = [f["texto_busqueda"] for f in lote]
            print(f"  Lote {i//BATCH_SIZE + 1}/{(len(fichas)-1)//BATCH_SIZE + 1}", end=" ", flush=True)
            try:
                if GENAI_NEW:
                    res = self._client.models.embed_content(
                        model=EMBED_MODEL,
                        contents=textos,
                        config=genai_types.EmbedContentConfig(
                            task_type="RETRIEVAL_DOCUMENT",
                            output_dimensionality=EMBED_DIM,
                        ),
                    )
                    embeddings.extend(e.values for e in res.embeddings)
                else:
                    for t in textos:
                        r = self._client.embed_content(
                            model=EMBED_MODEL, content=t, task_type="retrieval_document",
                            output_dimensionality=EMBED_DIM,
                        )
                        embeddings.append(r["embedding"])
                print("✓")
            except Exception as e:
                print(f"✗ {e}")
                embeddings.extend([[0.0]*EMBED_DIM]*len(lote))

        matrix = np.array(embeddings, dtype="float32")
        # Validar que no sean todos ceros (caso del proxy sandbox)
        if float(np.abs(matrix).sum()) < 1e-6:
            print("❌ Embeddings inválidos (ceros). Aborto y mantengo flag faiss_invalido.flag.")
            return 0

        faiss.normalize_L2(matrix)
        index = faiss.IndexFlatIP(EMBED_DIM)
        index.add(matrix)

        FAISS_INDEX.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(index, str(FAISS_INDEX))
        with open(FICHAS_META, "wb") as f:
            pickle.dump(fichas, f)
        # Reconstruir BM25
        self.bm25 = BM25([tokenizar(f.get("texto_busqueda","")) for f in fichas])
        with open(BM25_FILE, "wb") as f:
            pickle.dump(self.bm25, f)

        if INVALID_FLG.exists():
            INVALID_FLG.unlink()

        self.index, self.meta, self._listo = index, fichas, True
        print(f"✅ Índice listo: {len(fichas)} fichas")
        return len(fichas)

    # ── Embedding de query con cache ──────────────────────────────────────────

    def _embed_query(self, query: str) -> "np.ndarray | None":
        if not self._client or not self._listo or not NP_OK:
            return None
        if query in self._cache_q:
            return self._cache_q[query]
        try:
            if GENAI_NEW:
                res = self._client.models.embed_content(
                    model=EMBED_MODEL, contents=[query],
                    config=genai_types.EmbedContentConfig(
                        task_type="RETRIEVAL_QUERY",
                        output_dimensionality=EMBED_DIM,
                    ),
                )
                vec = np.array([res.embeddings[0].values], dtype="float32")
            else:
                r = self._client.embed_content(
                    model=EMBED_MODEL, content=query, task_type="retrieval_query",
                    output_dimensionality=EMBED_DIM,
                )
                vec = np.array([r["embedding"]], dtype="float32")
            faiss.normalize_L2(vec)
            self._cache_q[query] = vec
            return vec
        except Exception as e:
            print(f"⚠ embed query: {e}")
            return None

    # ── Expansión de query ────────────────────────────────────────────────────

    def expandir_query(self, query: str) -> list[str]:
        q = _normalizar(query)
        variantes = {query.strip()}
        for clave, sinos in SINONIMOS.items():
            if clave in q:
                for s in sinos:
                    variantes.add(query + " " + s)
        # Añadir variante "estilo pleito" para activar BM25 con términos jurídicos
        if "tutela" not in q:
            variantes.add(query + " acción de tutela")
        return list(variantes)[:4]   # cap a 4 variantes

    # ── Búsqueda híbrida (RRF) ────────────────────────────────────────────────

    def _dense_search(self, query: str, k: int) -> list[tuple[int, float]]:
        if not self._listo:
            return []
        q_emb = self._embed_query(query)
        if q_emb is None:
            return []
        scores, idxs = self.index.search(q_emb, k)
        return [(int(i), float(s)) for i, s in zip(idxs[0], scores[0]) if i >= 0]

    def _bm25_search(self, query: str, k: int) -> list[tuple[int, float]]:
        if self.bm25 is None or not self.meta:
            return []
        return self.bm25.topk(query, k)

    @staticmethod
    def _rrf(rankings: list[list[tuple[int, float]]], k: int = RRF_K) -> dict[int, float]:
        """Reciprocal Rank Fusion: combina rankings sin necesitar normalizar scores."""
        fused: dict[int, float] = defaultdict(float)
        for ranking in rankings:
            for rank, (doc_id, _) in enumerate(ranking):
                fused[doc_id] += 1.0 / (k + rank + 1)
        return fused

    def _mmr(self, query_vec, candidatos: list[int], k: int, lam: float = MMR_LAMBDA) -> list[int]:
        """Maximal Marginal Relevance para diversidad."""
        if not self._listo or query_vec is None or not candidatos:
            return candidatos[:k]
        # Reconstruir vectores desde el índice FAISS
        try:
            vecs = np.vstack([self.index.reconstruct(i) for i in candidatos])  # ya normalizados
        except Exception:
            return candidatos[:k]
        sim_q = vecs @ query_vec.T  # (n,1)
        sim_q = sim_q.flatten()
        seleccionados: list[int] = []
        restantes = list(range(len(candidatos)))
        while restantes and len(seleccionados) < k:
            if not seleccionados:
                best = max(restantes, key=lambda i: sim_q[i])
            else:
                sel_vecs = vecs[seleccionados]
                # similitud máxima a un seleccionado
                def mmr_score(i):
                    return lam * sim_q[i] - (1 - lam) * float((vecs[i] @ sel_vecs.T).max())
                best = max(restantes, key=mmr_score)
            seleccionados.append(best)
            restantes.remove(best)
        return [candidatos[i] for i in seleccionados]

    def buscar(self, query: str, k: int = None, filtro_area: str = None,
               filtro_anio: int = None, filtro_sala: str = None,
               hibrido: bool = True) -> list[dict]:
        """
        Búsqueda híbrida BM25 + dense con RRF + MMR.
        Aplica filtros estructurados (área/año/sala) tras la fusión.
        """
        k = k or self.top_k
        if not self.meta:
            return []

        # 1) Multi-query si tiene sentido
        queries = self.expandir_query(query) if hibrido else [query]

        # 2) Recuperar candidatos densos y léxicos por cada variante
        rankings: list[list[tuple[int,float]]] = []
        for q in queries:
            if self._listo:
                rankings.append(self._dense_search(q, TOP_K_DENSE))
            rankings.append(self._bm25_search(q, TOP_K_BM25))

        rankings = [r for r in rankings if r]
        if not rankings:
            # Fallback bruto: keyword count
            return self._buscar_keywords(query, k, filtro_area)

        # 3) Fusionar con RRF
        fused = self._rrf(rankings)
        ordenados = sorted(fused.items(), key=lambda x: -x[1])
        ids = [i for i, _ in ordenados]

        # 4) Aplicar filtros estructurados
        def pasa_filtros(idx: int) -> bool:
            f = self.meta[idx]
            if filtro_area and filtro_area not in f.get("areas", []):
                return False
            if filtro_anio and int(f.get("anio", 0)) != int(filtro_anio):
                return False
            if filtro_sala and filtro_sala.upper() != str(f.get("sala","")).upper():
                return False
            return True

        ids = [i for i in ids if pasa_filtros(i)]
        if not ids:
            return []

        # 5) MMR sobre candidatos densos para diversidad
        if self._listo:
            q_emb = self._embed_query(query)
            ids = self._mmr(q_emb, ids[:max(20, k*3)], k=k)

        ids = ids[:k]

        # 6) Empaquetar con scores
        out = []
        for rank, idx in enumerate(ids):
            f = dict(self.meta[idx])
            f["score"] = round(fused.get(idx, 0.0), 4)
            f["rank"]  = rank + 1
            out.append(f)
        return out

    def _buscar_keywords(self, query: str, k: int, filtro_area: str = None) -> list[dict]:
        qts = tokenizar(query)
        out = []
        for f in self.meta:
            txt = _normalizar(f.get("texto_busqueda",""))
            score = sum(txt.count(t) for t in qts)
            if score == 0:
                continue
            if filtro_area and filtro_area not in f.get("areas", []):
                continue
            ff = dict(f); ff["score"] = score / 100.0
            out.append(ff)
        return sorted(out, key=lambda x: -x["score"])[:k]

    # ── Re-ranking con LLM (opcional) ─────────────────────────────────────────

    def rerank_llm(self, query: str, fichas: list[dict], top_n: int = None) -> list[dict]:
        """Pide al LLM ordenar las fichas por relevancia jurisprudencial real."""
        if not (self._client and GENAI_NEW and fichas):
            return fichas
        top_n = top_n or len(fichas)
        items = "\n".join(
            f"[{i+1}] {f.get('id','?')} — {' / '.join(f.get('temas',[])[:2])}"
            for i, f in enumerate(fichas)
        )
        prompt = (
            f"CONSULTA: {query}\n\nFICHAS CANDIDATAS:\n{items}\n\n"
            f"Devuelve SOLO los números (separados por coma) de las {top_n} fichas más útiles "
            f"para responder la consulta, ordenadas de más a menos relevante. "
            f"Sin texto adicional. Ejemplo: 3,1,5,2"
        )
        try:
            r = self._client.models.generate_content(
                model=RERANK_MODEL, contents=prompt,
                config=genai_types.GenerateContentConfig(temperature=0.0, max_output_tokens=80),
            )
            nums = [int(n) for n in re.findall(r"\d+", r.text or "")]
            seen, ordenadas = set(), []
            for n in nums:
                if 1 <= n <= len(fichas) and n not in seen:
                    ordenadas.append(fichas[n-1]); seen.add(n)
            for i, f in enumerate(fichas, 1):
                if i not in seen:
                    ordenadas.append(f)
            return ordenadas[:top_n]
        except Exception:
            return fichas

    # ── Generación ────────────────────────────────────────────────────────────

    def consultar(self, pregunta: str, filtro_area: str = None,
                  filtro_anio: int = None, filtro_sala: str = None,
                  modo: str = "respuesta", rerank: bool = True,
                  top_k: int = None) -> dict:
        if not (GENAI_OK and self._client):
            return {"error": "google-genai no disponible o sin API key", "respuesta": ""}

        fichas = self.buscar(
            pregunta, k=top_k or self.top_k,
            filtro_area=filtro_area, filtro_anio=filtro_anio, filtro_sala=filtro_sala,
        )
        if rerank and len(fichas) > 3:
            fichas = self.rerank_llm(pregunta, fichas)

        if not fichas:
            return {
                "respuesta": ("No se encontraron precedentes en el índice para esa consulta. "
                              "Reformula con términos jurídicos (p.ej. «fuero de maternidad despido»)."),
                "fichas_usadas": [], "modo": modo, "query": pregunta,
            }

        contexto = self._construir_contexto(fichas)
        prompt   = self._construir_prompt(pregunta, contexto, modo)

        try:
            if GENAI_NEW:
                r = self._client.models.generate_content(
                    model=GEN_MODEL, contents=prompt,
                    config=genai_types.GenerateContentConfig(
                        temperature=0.2, max_output_tokens=MAX_OUT_TOK,
                    ),
                )
                texto = r.text or ""
            else:
                m = self._client.GenerativeModel(GEN_MODEL)
                r = m.generate_content(prompt, generation_config={"temperature":0.2,
                                                                  "max_output_tokens":MAX_OUT_TOK})
                texto = r.text or ""

            return {
                "respuesta"     : texto,
                "fichas_usadas" : [{"id": f["id"], "score": f.get("score",0),
                                    "areas": f.get("areas",[]),
                                    "sala": f.get("sala"), "anio": f.get("anio"),
                                    "temas": f.get("temas", [])[:3]} for f in fichas],
                "modo"          : modo,
                "query"         : pregunta,
                "tokens_aprox"  : len(prompt)//4 + len(texto)//4,
            }
        except Exception as e:
            return {"error": str(e), "respuesta": f"Error consultando Gemini: {e}"}

    # ── Construcción de prompt ────────────────────────────────────────────────

    def _construir_contexto(self, fichas: list[dict]) -> str:
        partes = []
        for i, f in enumerate(fichas, 1):
            sala  = f.get("sala","?")
            anio  = f.get("anio","?")
            id_   = f.get("id","?")
            temas = " > ".join((f.get("temas") or [])[:3])
            descs = (f.get("texto_busqueda","") or "")
            # Usamos texto_busqueda truncado (ya contiene tesis y descriptores)
            descs = descs[:900]
            partes.append(
                f"[F{i}] Radicado: {id_} | Sala {sala} | {anio}\n"
                f"Temas: {temas}\n"
                f"Contenido: {descs}"
            )
        return "\n\n".join(partes)

    def _construir_prompt(self, pregunta: str, contexto: str, modo: str) -> str:
        base = f"""Eres jurista experto en jurisprudencia de tutelas de la Corte Suprema de Justicia de Colombia (Salas Civil, Laboral, Penal y Plena), asistente del despacho Galeano Herrera | Abogados.

Reglas estrictas:
- Cita SIEMPRE el radicado real entre paréntesis, p. ej. (STC15780-2021), tomado únicamente de las fichas listadas más abajo.
- Si una afirmación no está respaldada por una ficha, di explícitamente "no hay precedente recuperado en el índice".
- Nunca inventes radicados, fechas ni magistrados.
- Responde en español jurídico claro, sin relleno.

JURISPRUDENCIA RECUPERADA (RAG):
{contexto}

CONSULTA DEL ABOGADO: {pregunta}
"""
        plantillas = {
            "respuesta": base + """
Estructura tu respuesta así (usa Markdown):

### 1. Tesis de la Corte
Síntesis jurisprudencial con citas a [F#].

### 2. Precedentes aplicables
Lista breve: radicado — regla de decisión.

### 3. Probabilidad de éxito
Alta / Media / Baja, justificada con los radicados.

### 4. Argumento listo para tutela
Párrafo redactado, con citas a los radicados.""",

            "caso": base + """
Aplica el protocolo Galeano Herrera (Markdown):

### CLASIFICACIÓN
Derecho vulnerado, accionado y área (salud / pensiones / laboral / accidentes / insolvencia / DD.FF.).

### DIAGNÓSTICO
Procedencia de la tutela. Subsidiariedad. Fuero o protección reforzada. Mínimo vital.

### ESTRATEGIA
- Acción principal y alternativa.
- Plazo estimado.
- Probabilidad de éxito (con radicados).

### PRECEDENTES
Bullets: radicado — por qué aplica.

### SIGUIENTE PASO
Documento concreto a preparar y plazo.""",

            "tutela": base + """
Genera un BORRADOR DE ACCIÓN DE TUTELA, listo para firmar, con esta estructura:

1. Encabezado y juez competente
2. Hechos numerados (1., 2., 3., …)
3. Derechos fundamentales vulnerados
4. Fundamentos jurídicos — citando los radicados como (STC...-AAAA)
5. Pretensiones (con medida provisional si aplica)
6. Pruebas
7. Juramento, notificaciones y anexos

Si falta información esencial, márcala como [COMPLETAR: ...]. No inventes datos.""",

            "linea": base + """
Resume la LÍNEA JURISPRUDENCIAL en Markdown:

### Tesis dominante
Citando radicados.

### Evolución reciente (últimos años)
Cambios o consolidación.

### Criterios que conceden el amparo
Lista accionable.

### Casos en que la Corte NIEGA
Para anticipar la defensa contraria.

### Cita estrella
1 párrafo textual de la ficha más relevante (entre comillas)."""
        }
        return plantillas.get(modo, plantillas["respuesta"])

    # ── Estadísticas ──────────────────────────────────────────────────────────

    def estadisticas(self) -> dict:
        por_area, por_anio, por_sala = Counter(), Counter(), Counter()
        for f in self.meta:
            for a in f.get("areas", []): por_area[a] += 1
            por_anio[str(f.get("anio","?"))] += 1
            por_sala[str(f.get("sala","?"))] += 1
        return {
            "total_fichas" : len(self.meta),
            "faiss_listo"  : self._listo,
            "bm25_listo"   : self.bm25 is not None,
            "por_area"     : dict(por_area.most_common()),
            "por_anio"     : dict(sorted(por_anio.items())),
            "por_sala"     : dict(por_sala.most_common()),
        }


# ── CLI ────────────────────────────────────────────────────────────────────────

def _cli() -> None:
    p = argparse.ArgumentParser(description="Motor RAG — Jurisprudencia CSJ")
    p.add_argument("query", nargs="?")
    p.add_argument("--indexar", action="store_true")
    p.add_argument("--forzar",  action="store_true")
    p.add_argument("--caso",    type=str)
    p.add_argument("--tutela",  type=str)
    p.add_argument("--linea",   type=str)
    p.add_argument("--area",    type=str)
    p.add_argument("--anio",    type=int)
    p.add_argument("--sala",    type=str)
    p.add_argument("--top-k",   type=int, default=TOP_K)
    p.add_argument("--no-rerank", action="store_true")
    p.add_argument("--config-key", type=str)
    p.add_argument("--stats",   action="store_true")
    args = p.parse_args()

    print("=" * 60)
    print("  MOTOR RAG — JURISPRUDENCIA CSJ — GALEANO HERRERA")
    print("=" * 60)

    if args.config_key:
        guardar_config({"gemini_api_key": args.config_key})
        print(f"✓ API key guardada en {CONFIG_FILE}")
        return

    if args.stats:
        m = MotorRAG(solo_busqueda=True)
        for k, v in m.estadisticas().items():
            print(f"  {k}: {v}")
        return

    motor = MotorRAG(top_k=args.top_k)

    if args.indexar:
        motor.indexar(forzar=args.forzar)
        return

    if args.caso:    modo, q = "caso",   args.caso
    elif args.tutela:modo, q = "tutela", args.tutela
    elif args.linea: modo, q = "linea",  args.linea
    elif args.query: modo, q = "respuesta", args.query
    else: p.print_help(); return

    print(f"\n🔍 [{modo}] {q[:80]}…\n")
    res = motor.consultar(q, filtro_area=args.area, filtro_anio=args.anio,
                          filtro_sala=args.sala, modo=modo, rerank=not args.no_rerank)
    if "error" in res:
        print(f"❌ {res['error']}"); return
    print(res["respuesta"])
    print("\n— Fichas usadas:", ", ".join(f["id"] for f in res["fichas_usadas"]))
    print(f"⚡ ~{res.get('tokens_aprox','?')} tokens")


if __name__ == "__main__":
    _cli()
