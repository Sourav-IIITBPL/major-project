"""
Enhancement 2 – FastAPI REST Backend
======================================
Exposes the ML-Assisted Adaptive Cryptographic Engine as a REST API.

Endpoints:
  GET  /                          Health check + API info
  POST /api/analyze               Extract features + predict strategy for given exponent
  POST /api/compute               Run full adaptive modular exponentiation
  GET  /api/benchmark             Run live 7-strategy benchmark for given bit-length
  POST /api/rsa/keygen            Generate RSA key pair
  POST /api/rsa/encrypt           RSA encrypt integer
  POST /api/rsa/decrypt           RSA decrypt integer
  POST /api/rsa/sign              RSA sign (text or integer)
  POST /api/rsa/verify            RSA verify signature
  GET  /api/backends              List available hardware backend profiles
  POST /api/backends/dispatch     Dispatch strategy for a specific hardware backend

Run:
    .venv/bin/uvicorn backend.api:app --reload --port 8000
"""

import sys
import os
import math
import secrets
import time
import traceback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Literal

# Project imports
from major.src.features.feature_extractor import extract_features
from major.src.adaptive_engine import AdaptiveCryptoEngine
from major.src.crypto_utils import generate_prime
from major.src.ml.compiled_predictor import predict_strategy
from major.src.ml.generate_dataset import generate_custom_exponent, compute_hw_cost
from crypto_pipeline.rsa_pipeline import RSAPipeline
from multi_backend.backend_configs import BACKEND_CONFIGS, compute_hw_cost_backend
from multi_backend.train_per_backend import dispatch_for_backend

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = FastAPI(
    title="ML-Assisted Adaptive Cryptographic Engine API",
    description=(
        "REST API for the ML-Assisted Adaptive Cryptographic Engine — "
        "B.Tech Major Project by Sourav Yadav & Eric Dazzle George, IIIT Bhopal."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Allow React frontend on any port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Pydantic Models
# ---------------------------------------------------------------------------

class AnalyzeRequest(BaseModel):
    exponent: int = Field(..., gt=0, description="Exponent B (positive integer)")
    w: int = Field(3, ge=2, le=6, description="wNAF window size")


class ComputeRequest(BaseModel):
    base: int = Field(..., gt=0)
    exponent: int = Field(..., gt=0)
    modulus: int = Field(..., gt=1)
    mode: Literal[
        "ml_adaptive", "fixed_binary", "fixed_naf",
        "fixed_wnaf", "fixed_vlim", "hybrid_sliced", "blinded_adaptive"
    ] = "ml_adaptive"
    phi_m: Optional[int] = None
    slice_bits: int = 256


class BenchmarkRequest(BaseModel):
    bit_length: int = Field(1024, ge=128, le=4096)
    profile: Literal["uniform", "sparse", "dense", "bursty", "alternating"] = "uniform"
    trials: int = Field(3, ge=1, le=10)


class RSAKeygenRequest(BaseModel):
    bits: int = Field(2048, ge=512, le=4096)


class RSAEncryptRequest(BaseModel):
    message: int = Field(..., gt=0)
    e: int
    n: int


class RSADecryptRequest(BaseModel):
    ciphertext: int = Field(..., gt=0)
    d: int
    n: int
    p: int
    q: int
    phi_n: int


class RSASignRequest(BaseModel):
    message: Optional[int] = None
    text: Optional[str]    = None
    d: int
    n: int
    p: int
    q: int
    phi_n: int


class RSAVerifyRequest(BaseModel):
    signature: int
    message: Optional[int] = None
    text: Optional[str]    = None
    e: int
    n: int


class BackendDispatchRequest(BaseModel):
    exponent: int = Field(..., gt=0)
    backend: str = "python_bigint"


# ---------------------------------------------------------------------------
# Helper: generate alternating exponent
# ---------------------------------------------------------------------------
def _alternating_exp(bit_length: int) -> int:
    val = 0
    for i in range(bit_length):
        if i % 2 == 0:
            val |= (1 << i)
    return val


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", tags=["Health"])
def root():
    return {
        "status": "online",
        "project": "ML-Assisted Adaptive Cryptographic Engine",
        "authors": ["Sourav Yadav (23U01074)", "Eric Dazzle George (23U01035)"],
        "institution": "IIIT Bhopal – B.Tech Major Project",
        "supervisor": "Dr. Aashish Parihar",
        "version": "1.0.0",
        "endpoints": [
            "POST /api/analyze",
            "POST /api/compute",
            "GET  /api/benchmark",
            "POST /api/rsa/keygen",
            "POST /api/rsa/encrypt",
            "POST /api/rsa/decrypt",
            "POST /api/rsa/sign",
            "POST /api/rsa/verify",
            "GET  /api/backends",
            "POST /api/backends/dispatch",
        ],
    }


@app.post("/api/analyze", tags=["Dispatch"])
def analyze(req: AnalyzeRequest):
    """
    Extract structural features from an exponent and predict the optimal strategy.
    Returns the full 10-dimensional feature vector and ML decision.
    """
    try:
        feats    = extract_features(req.exponent, w=req.w)
        strategy = predict_strategy(feats)
        bit_len  = req.exponent.bit_length()

        return {
            "exponent_bits": bit_len,
            "features": feats,
            "predicted_strategy": strategy,
            "strategy_rationale": _strategy_rationale(feats, strategy),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/compute", tags=["Dispatch"])
def compute(req: ComputeRequest):
    """
    Execute modular exponentiation: result = base^exponent mod modulus.
    Uses the specified dispatch mode.
    """
    if math.gcd(req.base, req.modulus) != 1:
        raise HTTPException(
            status_code=400,
            detail="gcd(base, modulus) != 1. base and modulus must be coprime."
        )
    try:
        t0  = time.perf_counter()
        res = AdaptiveCryptoEngine.execute(
            base=req.base, exp=req.exponent, mod=req.modulus,
            mode=req.mode, phi_m=req.phi_m, slice_bits=req.slice_bits,
        )
        total_ms = (time.perf_counter() - t0) * 1000

        m = res["metrics"]
        return {
            "result":            res["result"],
            "mode":              req.mode,
            "strategy_used":     res["selected_strategy"],
            "total_time_ms":     round(total_ms, 4),
            "dispatch_time_us":  round(res["dispatch_time_us"], 4),
            "metrics": {
                "squarings":     m["sqrs"],
                "multiplications": m["mults"],
                "iterations":    m["iters"],
                "hw_cost":       round(compute_hw_cost(m), 2),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/benchmark", tags=["Benchmark"])
def benchmark(req: BenchmarkRequest):
    """
    Run a live multi-strategy benchmark for the specified bit-length and profile.
    Returns timing, multiplications, and speedup for all 7 strategies.
    """
    try:
        p = generate_prime(req.bit_length // 2)
        q = generate_prime(req.bit_length // 2)
        while q == p:
            q = generate_prime(req.bit_length // 2)
        mod   = p * q
        phi_m = (p - 1) * (q - 1)
        base  = secrets.randbits(req.bit_length) % mod
        while math.gcd(base, mod) != 1:
            base = secrets.randbits(req.bit_length) % mod

        modes = [
            "fixed_binary", "fixed_naf", "fixed_wnaf",
            "fixed_vlim", "ml_adaptive", "hybrid_sliced", "blinded_adaptive"
        ]
        agg = {m: {"time_ms": 0.0, "mults": 0, "iters": 0, "hw_cost": 0.0} for m in modes}

        # Profile-specific exponent generator
        if req.profile == "alternating":
            exp_fn = lambda: _alternating_exp(req.bit_length)
        else:
            exp_fn = lambda: generate_custom_exponent(req.bit_length, req.profile)

        for _ in range(req.trials):
            exp = exp_fn()
            expected = pow(base, exp, mod)
            for mode in modes:
                res = AdaptiveCryptoEngine.execute(
                    base, exp, mod, mode=mode, phi_m=phi_m, slice_bits=256
                )
                assert res["result"] == expected
                m = res["metrics"]
                agg[mode]["time_ms"] += res["total_time_ms"]
                agg[mode]["mults"]   += m["mults"]
                agg[mode]["iters"]   += m["iters"]
                agg[mode]["hw_cost"] += compute_hw_cost(m)

        # Average
        results = []
        base_time = agg["fixed_binary"]["time_ms"] / req.trials
        base_mults = agg["fixed_binary"]["mults"] / req.trials
        for mode in modes:
            avg_t = agg[mode]["time_ms"]   / req.trials
            avg_m = agg[mode]["mults"]     / req.trials
            avg_i = agg[mode]["iters"]     / req.trials
            avg_h = agg[mode]["hw_cost"]   / req.trials
            results.append({
                "mode":           mode,
                "avg_time_ms":    round(avg_t, 3),
                "avg_mults":      round(avg_m, 1),
                "avg_iters":      round(avg_i, 1),
                "avg_hw_cost":    round(avg_h, 1),
                "speedup_pct":    round((base_time - avg_t) / base_time * 100, 2),
                "mult_cut_pct":   round((base_mults - avg_m) / base_mults * 100, 2),
            })

        return {
            "bit_length": req.bit_length,
            "profile":    req.profile,
            "trials":     req.trials,
            "results":    results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=traceback.format_exc())


# ------------------------------------------------------------------
# RSA Pipeline Endpoints
# ------------------------------------------------------------------

@app.post("/api/rsa/keygen", tags=["RSA Pipeline"])
def rsa_keygen(req: RSAKeygenRequest):
    """Generate a fresh RSA key pair."""
    try:
        pair = RSAPipeline.keygen(bits=req.bits)
        pub  = pair.public
        priv = pair.private
        return {
            "bits":  req.bits,
            "public_key":  {"e": pub.e, "n": pub.n},
            "private_key": {
                "d":     priv.d, "n": priv.n,
                "p":     priv.p, "q": priv.q,
                "phi_n": priv.phi_n,
            },
            "note": "Keep private_key confidential. Share only public_key.",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/rsa/encrypt", tags=["RSA Pipeline"])
def rsa_encrypt(req: RSAEncryptRequest):
    """Encrypt an integer with the public key using ML-Adaptive dispatch."""
    from crypto_pipeline.rsa_pipeline import RSAPublicKey
    try:
        pub = RSAPublicKey(e=req.e, n=req.n)
        res = RSAPipeline.encrypt(req.message, pub)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/rsa/decrypt", tags=["RSA Pipeline"])
def rsa_decrypt(req: RSADecryptRequest):
    """Decrypt a ciphertext with the private key using Blinded-Adaptive dispatch."""
    from crypto_pipeline.rsa_pipeline import RSAPrivateKey
    try:
        priv = RSAPrivateKey(d=req.d, n=req.n, p=req.p, q=req.q, phi_n=req.phi_n)
        res  = RSAPipeline.decrypt(req.ciphertext, priv)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/rsa/sign", tags=["RSA Pipeline"])
def rsa_sign(req: RSASignRequest):
    """Sign a message (integer or text) with the private key."""
    from crypto_pipeline.rsa_pipeline import RSAPrivateKey
    try:
        priv = RSAPrivateKey(d=req.d, n=req.n, p=req.p, q=req.q, phi_n=req.phi_n)
        if req.text is not None:
            return RSAPipeline.sign_text(req.text, priv)
        elif req.message is not None:
            return RSAPipeline.sign(req.message, priv)
        else:
            raise HTTPException(status_code=400, detail="Provide 'message' or 'text'.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/rsa/verify", tags=["RSA Pipeline"])
def rsa_verify(req: RSAVerifyRequest):
    """Verify a signature against a message or text."""
    from crypto_pipeline.rsa_pipeline import RSAPublicKey
    try:
        pub = RSAPublicKey(e=req.e, n=req.n)
        if req.text is not None:
            return RSAPipeline.verify_text(req.text, req.signature, pub)
        elif req.message is not None:
            return RSAPipeline.verify(req.signature, req.message, pub)
        else:
            raise HTTPException(status_code=400, detail="Provide 'message' or 'text'.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ------------------------------------------------------------------
# Backend Endpoints
# ------------------------------------------------------------------

@app.get("/api/backends", tags=["Multi-Backend"])
def get_backends():
    """List all available hardware backend profiles."""
    return {
        "backends": [
            {
                "name":        name,
                "cost_sqr":    cfg["cost_sqr"],
                "cost_mult":   cfg["cost_mult"],
                "cost_ctrl":   cfg["cost_ctrl"],
                "description": cfg["description"],
            }
            for name, cfg in BACKEND_CONFIGS.items()
        ]
    }


@app.post("/api/backends/dispatch", tags=["Multi-Backend"])
def backend_dispatch(req: BackendDispatchRequest):
    """
    Predict the optimal strategy for a specific hardware backend.
    Uses the backend-specific trained model if available,
    else falls back to the default compiled predictor.
    """
    try:
        feats    = extract_features(req.exponent, w=3)
        strategy = dispatch_for_backend(feats, req.backend)
        cfg      = BACKEND_CONFIGS.get(req.backend, {})
        return {
            "exponent_bits":     req.exponent.bit_length(),
            "backend":           req.backend,
            "predicted_strategy": strategy,
            "backend_costs": {
                "cost_sqr":  cfg.get("cost_sqr", 1.0),
                "cost_mult": cfg.get("cost_mult", 1.2),
                "cost_ctrl": cfg.get("cost_ctrl", 0.15),
            },
            "features": feats,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------
def _strategy_rationale(feats: dict, strategy: str) -> str:
    """Generate a human-readable explanation for the ML dispatch decision."""
    longest_one  = feats.get("longest_one_run", 0)
    hw           = feats.get("hamming_weight", 0)
    zero_density = feats.get("zero_density", 0)
    bit_length   = feats.get("bit_length", 0)

    if strategy == "Binary":
        return (
            f"Binary selected: Hamming weight is low ({hw}) or exponent is "
            f"short ({bit_length}-bit). Precomputation table cost of wNAF "
            f"would exceed its multiplication savings."
        )
    elif strategy == "NAF":
        return (
            f"NAF selected: Long 1-runs detected (max={longest_one}). "
            f"NAF collapses 1-runs from {longest_one} multiplications down to 2 "
            f"(2^k−1 trick). Precomputation overhead is minimal."
        )
    elif strategy == "wNAF":
        return (
            f"wNAF (w=3) selected: High Hamming weight ({hw}) and long 1-runs "
            f"({longest_one}) make window precomputation profitable. Expected "
            f"multiplication density: ~25% of bit-length."
        )
    elif strategy == "VLIM":
        return (
            f"VLIM selected: High zero density ({zero_density:.2%}) allows "
            f"aggressive zero-run batching. Control loop iterations reduced "
            f"by an estimated 50–87% vs Binary."
        )
    return "Strategy selected via compiled Decision Tree classifier."
