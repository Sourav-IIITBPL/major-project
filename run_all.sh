#!/usr/bin/env bash
# =============================================================================
#  ML-Assisted Adaptive Cryptographic Engine — Master Setup & Run Script
# =============================================================================
# Usage:
#   bash run_all.sh setup        # Install deps + run all enhancements
#   bash run_all.sh dataset      # Enhancement 1: Generate extended dataset
#   bash run_all.sh train        # Enhancement 3: Train DT+RF+XGBoost+SHAP
#   bash run_all.sh test-rsa     # Enhancement 4: Test RSA pipeline
#   bash run_all.sh profile      # Enhancement 6: Hardware profiler
#   bash run_all.sh backends     # Enhancement 7: Train per-backend models
#   bash run_all.sh api          # Enhancement 2: Start FastAPI backend
#   bash run_all.sh frontend     # Enhancement 2: Start React frontend
# =============================================================================

set -e
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON=".venv/bin/python"
PIP=".venv/bin/pip"

cd "$PROJECT_DIR"

# Ensure venv exists
if [ ! -f ".venv/bin/python" ]; then
  echo "[Setup] Creating Python virtual environment…"
  python3 -m venv .venv
fi

case "${1:-all}" in

  setup)
    echo "=== Installing Python dependencies ==="
    $PIP install --quiet xgboost shap fastapi uvicorn python-multipart \
        scikit-learn joblib pandas numpy matplotlib
    echo "=== Installing Node dependencies ==="
    cd frontend && npm install --silent && cd ..
    echo "✅ Setup complete."
    ;;

  dataset)
    echo "=== Enhancement 1: Extended Dataset Generation ==="
    $PYTHON enhanced_dataset/generate_extended_dataset.py
    ;;

  train)
    echo "=== Enhancement 3: Multi-Model Training (software target) ==="
    $PYTHON models/train_all_models.py --target software
    echo ""
    echo "=== Enhancement 3: Multi-Model Training (hardware target) ==="
    $PYTHON models/train_all_models.py --target hardware
    ;;

  test-rsa)
    echo "=== Enhancement 4: RSA Pipeline Tests ==="
    $PYTHON crypto_pipeline/test_rsa_pipeline.py
    ;;

  profile)
    echo "=== Enhancement 6: Hardware Auto-Profiler ==="
    $PYTHON profiler/hardware_profiler.py --iterations 5000
    ;;

  backends)
    echo "=== Enhancement 7: Per-Backend Model Training ==="
    $PYTHON multi_backend/train_per_backend.py --backend all
    ;;

  api)
    echo "=== Enhancement 2: Starting FastAPI Backend on http://localhost:8000 ==="
    echo "    Press Ctrl+C to stop."
    .venv/bin/uvicorn backend.api:app --reload --port 8000 --host 0.0.0.0
    ;;

  frontend)
    echo "=== Enhancement 2: Starting React Frontend on http://localhost:3000 ==="
    echo "    Press Ctrl+C to stop."
    cd frontend && npm run dev
    ;;

  all)
    echo "============================================================"
    echo "  Running ALL Enhancements in Sequence"
    echo "============================================================"
    $PIP install --quiet xgboost shap fastapi uvicorn python-multipart \
        scikit-learn joblib pandas numpy matplotlib
    echo ""
    echo "[1/5] Enhancement 1 — Extended Dataset…"
    $PYTHON enhanced_dataset/generate_extended_dataset.py
    echo ""
    echo "[2/5] Enhancement 3 — Train DT+RF+XGBoost (software target)…"
    $PYTHON models/train_all_models.py --target software
    echo ""
    echo "[3/5] Enhancement 4 — RSA Pipeline Tests…"
    $PYTHON crypto_pipeline/test_rsa_pipeline.py
    echo ""
    echo "[4/5] Enhancement 6 — Hardware Profiler…"
    $PYTHON profiler/hardware_profiler.py --iterations 3000
    echo ""
    echo "[5/5] Enhancement 7 — Per-Backend Models…"
    $PYTHON multi_backend/train_per_backend.py --backend all
    echo ""
    echo "============================================================"
    echo "  ALL ENHANCEMENTS COMPLETE!"
    echo "  To start the web dashboard:"
    echo "    Terminal 1: bash run_all.sh api"
    echo "    Terminal 2: bash run_all.sh frontend"
    echo "    Then open:  http://localhost:3000"
    echo "============================================================"
    ;;

  *)
    echo "Usage: bash run_all.sh [setup|dataset|train|test-rsa|profile|backends|api|frontend|all]"
    exit 1
    ;;
esac
