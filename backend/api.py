"""
FastAPI REST Backend for ML-Assisted Adaptive Cryptographic Engine
===================================================================
Production-grade REST API supporting arbitrary-precision cryptography.
All large integers (1024-bit, 2048-bit, 4096-bit) are safely accepted
as strings or integers and returned as exact decimal/hex strings to
prevent IEEE 754 floating-point truncation in browser JavaScript.
"""

import sys
import os
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")
import math
import secrets
import time
import traceback
from typing import Optional, Literal, Union, Any

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Core project imports
from major.src.features.feature_extractor import extract_features
from major.src.adaptive_engine import AdaptiveCryptoEngine
from major.src.crypto_utils import generate_prime
from major.src.ml.compiled_predictor import predict_strategy
from major.src.ml.generate_dataset import generate_custom_exponent, compute_hw_cost
from crypto_pipeline.rsa_pipeline import RSAPipeline
from multi_backend.backend_configs import BACKEND_CONFIGS
from multi_backend.train_per_backend import dispatch_for_backend


# ---------------------------------------------------------------------------
# BigInt Parser (safely parses int, decimal string, or hex 0x... string)
# ---------------------------------------------------------------------------

def parse_large_int(val: Union[int, str, None], field_name: str = "value") -> int:
    """Parse large cryptographic integers with arbitrary precision."""
    if val is None:
        raise HTTPException(status_code=400, detail=f"Missing required parameter: {field_name}")
    if isinstance(val, int):
        return val
    s = str(val).strip().replace("\n", "").replace(" ", "").replace("_", "")
    if not s:
        raise HTTPException(status_code=400, detail=f"Parameter '{field_name}' cannot be empty")
    try:
        if s.startswith("0x") or s.startswith("0X"):
            return int(s, 16)
        return int(s)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid integer format for '{field_name}'. Must be decimal or 0x-prefixed hex string."
        )


# ---------------------------------------------------------------------------
# App initialization
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Adaptive Cryptographic Engine API",
    description="Workload-Aware Exponentiation & Side-Channel Mitigation Platform",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request Schemas (Using Union[int, str] for BigInt safety)
# ---------------------------------------------------------------------------

class AnalyzeRequest(BaseModel):
    exponent: Union[int, str] = Field(..., description="Exponent integer or decimal/hex string")
    w: int = Field(3, ge=2, le=6, description="wNAF window size")


class GenerateExponentRequest(BaseModel):
    bits: int = Field(1024, ge=16, le=8192)
    profile: Literal["uniform", "sparse", "dense", "bursty", "alternating", "ecc_random"] = "uniform"


class ComputeRequest(BaseModel):
    base: Union[int, str]
    exponent: Union[int, str]
    modulus: Union[int, str]
    mode: Literal[
        "ml_adaptive", "fixed_binary", "fixed_naf",
        "fixed_wnaf", "fixed_vlim", "hybrid_sliced", "blinded_adaptive"
    ] = "ml_adaptive"
    phi_m: Optional[Union[int, str]] = None
    slice_bits: int = 256


class BenchmarkRequest(BaseModel):
    bit_length: int = Field(1024, ge=128, le=4096)
    profile: Literal["uniform", "sparse", "dense", "bursty", "alternating"] = "uniform"
    trials: int = Field(2, ge=1, le=10)


class RSAKeygenRequest(BaseModel):
    bits: int = Field(1024, ge=256, le=4096)


class RSAEncryptRequest(BaseModel):
    message: Union[int, str]
    e: Union[int, str]
    n: Union[int, str]


class RSADecryptRequest(BaseModel):
    ciphertext: Union[int, str]
    d: Union[int, str]
    n: Union[int, str]
    p: Union[int, str]
    q: Union[int, str]
    phi_n: Union[int, str]


class RSASignRequest(BaseModel):
    message: Optional[Union[int, str]] = None
    text: Optional[str] = None
    d: Union[int, str]
    n: Union[int, str]
    p: Union[int, str]
    q: Union[int, str]
    phi_n: Union[int, str]


class RSAVerifyRequest(BaseModel):
    signature: Union[int, str]
    message: Optional[Union[int, str]] = None
    text: Optional[str] = None
    e: Union[int, str]
    n: Union[int, str]


class BackendDispatchRequest(BaseModel):
    exponent: Union[int, str]
    backend: str = "python_bigint"


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------

@app.get("/api/health", tags=["Health"])
def health():
    return {
        "status": "online",
        "service": "Adaptive Cryptographic Engine API",
        "version": "2.0.0",
        "supported_backends": list(BACKEND_CONFIGS.keys()),
    }



@app.post("/api/generate-exponent", tags=["Core"])
def generate_exponent_api(req: GenerateExponentRequest):
    """Generate a random exponent string with specific bit-length and topology."""
    try:
        from enhanced_dataset.generate_extended_dataset import PROFILE_GENERATORS
        if req.profile in PROFILE_GENERATORS:
            exp = PROFILE_GENERATORS[req.profile](req.bits)
        else:
            exp = secrets.randbits(req.bits) | (1 << (req.bits - 1)) | 1
        
        return {
            "exponent": str(exp),
            "hex": hex(exp),
            "bits": exp.bit_length(),
            "profile": req.profile,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze", tags=["Core"])
def analyze_exponent(req: AnalyzeRequest):
    """Extract structural features from an exponent and predict optimal strategy."""
    try:
        exp_int = parse_large_int(req.exponent, "exponent")
        if exp_int <= 0:
            raise HTTPException(status_code=400, detail="Exponent must be positive.")
        
        t0 = time.perf_counter_ns()
        feats = extract_features(exp_int, w=req.w)
        strategy = predict_strategy(feats)
        extract_time_us = (time.perf_counter_ns() - t0) / 1000.0

        return {
            "exponent_bits": feats["bit_length"],
            "features": feats,
            "predicted_strategy": strategy,
            "strategy_rationale": _generate_rationale(feats, strategy),
            "extract_time_us": round(extract_time_us, 2),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feature extraction failed: {str(e)}")


@app.post("/api/compute", tags=["Core"])
def compute_modular_exponentiation(req: ComputeRequest):
    """Execute A^B mod M using the chosen dispatch strategy."""
    try:
        base = parse_large_int(req.base, "base")
        exp = parse_large_int(req.exponent, "exponent")
        mod = parse_large_int(req.modulus, "modulus")
        phi = parse_large_int(req.phi_m, "phi_m") if req.phi_m is not None else None

        if mod <= 1:
            raise HTTPException(status_code=400, detail="Modulus must be > 1.")
        if math.gcd(base, mod) != 1:
            raise HTTPException(status_code=400, detail="gcd(base, modulus) != 1. Base must be coprime to modulus.")

        t0 = time.perf_counter()
        res = AdaptiveCryptoEngine.execute(
            base=base, exp=exp, mod=mod,
            mode=req.mode, phi_m=phi, slice_bits=req.slice_bits
        )
        total_ms = (time.perf_counter() - t0) * 1000.0

        m = res["metrics"]
        return {
            "result": str(res["result"]),
            "hex": hex(res["result"]),
            "mode": req.mode,
            "strategy_used": res["selected_strategy"],
            "total_time_ms": round(total_ms, 3),
            "dispatch_time_us": round(res["dispatch_time_us"], 3),
            "metrics": {
                "squarings": m["sqrs"],
                "multiplications": m["mults"],
                "iterations": m["iters"],
                "hw_cost": round(compute_hw_cost(m), 2),
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Computation failed: {str(e)}")


@app.post("/api/benchmark", tags=["Benchmark"])
def run_benchmark(req: BenchmarkRequest):
    """Execute live multi-strategy comparative benchmark across true RSA primes."""
    try:
        p = generate_prime(req.bit_length // 2)
        q = generate_prime(req.bit_length // 2)
        while q == p:
            q = generate_prime(req.bit_length // 2)
        mod = p * q
        phi_m = (p - 1) * (q - 1)
        base = secrets.randbits(req.bit_length) % mod
        while math.gcd(base, mod) != 1:
            base = secrets.randbits(req.bit_length) % mod

        modes = [
            "fixed_binary", "fixed_naf", "fixed_wnaf",
            "fixed_vlim", "ml_adaptive", "hybrid_sliced", "blinded_adaptive"
        ]
        agg = {m: {"time_ms": 0.0, "mults": 0, "iters": 0, "hw_cost": 0.0} for m in modes}

        if req.profile == "alternating":
            exp_val = 0
            for i in range(req.bit_length):
                if i % 2 == 0:
                    exp_val |= (1 << i)
            exp_fn = lambda: exp_val
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
                agg[mode]["mults"] += m["mults"]
                agg[mode]["iters"] += m["iters"]
                agg[mode]["hw_cost"] += compute_hw_cost(m)

        base_time = (agg["fixed_binary"]["time_ms"] / req.trials) or 1.0
        base_mults = (agg["fixed_binary"]["mults"] / req.trials) or 1.0
        results = []

        for mode in modes:
            avg_t = agg[mode]["time_ms"] / req.trials
            avg_m = agg[mode]["mults"] / req.trials
            avg_i = agg[mode]["iters"] / req.trials
            avg_h = agg[mode]["hw_cost"] / req.trials
            results.append({
                "mode": mode,
                "avg_time_ms": round(avg_t, 3),
                "avg_mults": round(avg_m, 1),
                "avg_iters": round(avg_i, 1),
                "avg_hw_cost": round(avg_h, 1),
                "speedup_pct": round((base_time - avg_t) / base_time * 100.0, 1),
                "mult_cut_pct": round((base_mults - avg_m) / base_mults * 100.0, 1),
            })

        return {
            "bit_length": req.bit_length,
            "profile": req.profile,
            "trials": req.trials,
            "results": results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# RSA Lifecycle Endpoints (Strings for BigInt exactness)
# ---------------------------------------------------------------------------

@app.post("/api/rsa/keygen", tags=["RSA"])
def rsa_keygen(req: RSAKeygenRequest):
    """Generate RSA key pair and return components as exact strings."""
    try:
        pair = RSAPipeline.keygen(bits=req.bits)
        pub = pair.public
        priv = pair.private
        return {
            "bits": req.bits,
            "public_key": {
                "e": str(pub.e),
                "n": str(pub.n),
                "n_hex": hex(pub.n),
            },
            "private_key": {
                "d": str(priv.d),
                "d_hex": hex(priv.d),
                "n": str(priv.n),
                "p": str(priv.p),
                "q": str(priv.q),
                "phi_n": str(priv.phi_n),
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/rsa/encrypt", tags=["RSA"])
def rsa_encrypt(req: RSAEncryptRequest):
    """Encrypt message with public key using ML-Adaptive dispatch."""
    from crypto_pipeline.rsa_pipeline import RSAPublicKey
    try:
        msg = parse_large_int(req.message, "message")
        e = parse_large_int(req.e, "e")
        n = parse_large_int(req.n, "n")
        pub = RSAPublicKey(e=e, n=n)
        res = RSAPipeline.encrypt(msg, pub)
        return {
            "ciphertext": str(res["ciphertext"]),
            "ciphertext_hex": hex(res["ciphertext"]),
            "strategy_used": res["strategy_used"],
            "total_time_ms": round(res["total_time_ms"], 3),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/rsa/decrypt", tags=["RSA"])
def rsa_decrypt(req: RSADecryptRequest):
    """Decrypt ciphertext with private key using Blinded-Adaptive dispatch."""
    from crypto_pipeline.rsa_pipeline import RSAPrivateKey
    try:
        ct = parse_large_int(req.ciphertext, "ciphertext")
        d = parse_large_int(req.d, "d")
        n = parse_large_int(req.n, "n")
        p = parse_large_int(req.p, "p")
        q = parse_large_int(req.q, "q")
        phi = parse_large_int(req.phi_n, "phi_n")
        priv = RSAPrivateKey(d=d, n=n, p=p, q=q, phi_n=phi)
        res = RSAPipeline.decrypt(ct, priv)
        return {
            "plaintext": str(res["plaintext"]),
            "plaintext_hex": hex(res["plaintext"]),
            "strategy_used": res["strategy_used"],
            "total_time_ms": round(res["total_time_ms"], 3),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/rsa/sign", tags=["RSA"])
def rsa_sign(req: RSASignRequest):
    """Sign message digest with private key using Blinded-Adaptive dispatch."""
    from crypto_pipeline.rsa_pipeline import RSAPrivateKey
    try:
        d = parse_large_int(req.d, "d")
        n = parse_large_int(req.n, "n")
        p = parse_large_int(req.p, "p")
        q = parse_large_int(req.q, "q")
        phi = parse_large_int(req.phi_n, "phi_n")
        priv = RSAPrivateKey(d=d, n=n, p=p, q=q, phi_n=phi)

        if req.text is not None:
            res = RSAPipeline.sign_text(req.text, priv)
            return {
                "signature": str(res["signature"]),
                "signature_hex": hex(res["signature"]),
                "message_hash_int": str(res.get("message_hash_int", "")),
                "strategy_used": res["strategy_used"],
                "total_time_ms": round(res["total_time_ms"], 3),
            }
        elif req.message is not None:
            msg = parse_large_int(req.message, "message")
            res = RSAPipeline.sign(msg, priv)
            return {
                "signature": str(res["signature"]),
                "signature_hex": hex(res["signature"]),
                "strategy_used": res["strategy_used"],
                "total_time_ms": round(res["total_time_ms"], 3),
            }
        else:
            raise HTTPException(status_code=400, detail="Provide 'text' or 'message'.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/rsa/verify", tags=["RSA"])
def rsa_verify(req: RSAVerifyRequest):
    """Verify signature with public key using ML-Adaptive dispatch."""
    from crypto_pipeline.rsa_pipeline import RSAPublicKey
    try:
        sig = parse_large_int(req.signature, "signature")
        e = parse_large_int(req.e, "e")
        n = parse_large_int(req.n, "n")
        pub = RSAPublicKey(e=e, n=n)

        if req.text is not None:
            res = RSAPipeline.verify_text(req.text, sig, pub)
        elif req.message is not None:
            msg = parse_large_int(req.message, "message")
            res = RSAPipeline.verify(sig, msg, pub)
        else:
            raise HTTPException(status_code=400, detail="Provide 'text' or 'message'.")

        return {
            "verified": res["verified"],
            "recovered": str(res.get("recovered", "")),
            "strategy_used": res["strategy_used"],
            "total_time_ms": round(res["total_time_ms"], 3),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Hardware Backend Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/backends", tags=["Hardware"])
def get_hardware_backends():
    """List hardware target profiles and cost ratios."""
    return {
        "backends": [
            {
                "name": name,
                "cost_sqr": cfg["cost_sqr"],
                "cost_mult": cfg["cost_mult"],
                "cost_ctrl": cfg["cost_ctrl"],
                "description": cfg["description"],
            }
            for name, cfg in BACKEND_CONFIGS.items()
        ]
    }


@app.post("/api/backends/dispatch", tags=["Hardware"])
def dispatch_backend(req: BackendDispatchRequest):
    """Predict strategy for specific hardware backend target."""
    try:
        exp_int = parse_large_int(req.exponent, "exponent")
        feats = extract_features(exp_int, w=3)
        strategy = dispatch_for_backend(feats, req.backend)
        cfg = BACKEND_CONFIGS.get(req.backend, {})

        return {
            "exponent_bits": exp_int.bit_length(),
            "backend": req.backend,
            "predicted_strategy": strategy,
            "backend_costs": {
                "cost_sqr": cfg.get("cost_sqr", 1.0),
                "cost_mult": cfg.get("cost_mult", 1.2),
                "cost_ctrl": cfg.get("cost_ctrl", 0.15),
            },
            "features": feats,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Helper Rationale
# ---------------------------------------------------------------------------

def _generate_rationale(feats: dict, strategy: str) -> str:
    hw = feats.get("hamming_weight", 0)
    bits = feats.get("bit_length", 0)
    l_one = feats.get("longest_one_run", 0)
    zero_density = feats.get("zero_density", 0.0)

    if strategy == "Binary":
        return f"Binary L-to-R selected: Exponent has low Hamming density ({hw}/{bits}) or low bit-length ({bits}-bit). Avoiding window table precomputation overhead yields optimal execution."
    elif strategy == "wNAF":
        return f"Windowed NAF (w=3) selected: High density ({hw} ones) and bit streaks (longest one run = {l_one}) justify table precomputations. Multiplications reduced by up to 75-90%."
    elif strategy == "NAF":
        return f"Standard NAF selected: Long one-runs ({l_one} bits) are collapsed via signed recoding (2^k - 1) with negligible precomputation penalty."
    elif strategy == "VLIM":
        return f"Adaptive VLIM selected: High zero density ({zero_density:.1%}) enables aggressive zero-run batch squarings, compressing loop cycles by 50-87%."
    return "Optimized routing via compiled Decision Tree graph."


# ---------------------------------------------------------------------------
# Static Frontend Serving (Unified Production Deployment)
# ---------------------------------------------------------------------------

frontend_dist = os.path.join(ROOT, "frontend", "dist")
if os.path.isdir(frontend_dist):
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse

    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="static_assets")

    @app.get("/", include_in_schema=False)
    def serve_frontend_index():
        return FileResponse(os.path.join(frontend_dist, "index.html"))

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa_fallback(full_path: str):
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
else:
    @app.get("/", tags=["Health"])
    def root_fallback():
        return health()


