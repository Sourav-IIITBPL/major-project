# Deployment & Operations Guide
## ML-Assisted Adaptive Cryptographic Engine

This guide provides end-to-end instructions for deploying both the **FastAPI REST Backend** and the **React 19 Interactive Frontend** in development, unified single-port production, Linux VPS servers, Docker containers, and Cloud hosting platforms.

---

## 🏛 Deployment Architecture Options

| Strategy | Recommended Use Case | Ports | Prerequisites |
| :--- | :--- | :--- | :--- |
| **Option 1: Unified Production (Built-in)** | Best for quick local demo, presentation, or single VPS port | Port `8000` (serves both React UI and REST APIs) | Python 3.10+, Virtualenv |
| **Option 2: Docker Container** | Best for zero-dependency containerized deployments | Port `8000` | Docker, Docker Compose |
| **Option 3: Dual Development Servers** | Best for active code editing with hot module replacement (HMR) | Port `8000` (Backend) + Port `3000` (Frontend) | Node.js 18+, Python 3.10+ |
| **Option 4: Linux VPS (systemd + Nginx)** | Best for persistent 24/7 production on AWS, DigitalOcean, Hetzner | Port `80` / `443` (SSL) | Ubuntu/Debian, Nginx, systemd |
| **Option 5: Free Cloud Platforms** | Best for sharing a public web URL (Render, Railway, Fly.io) | Cloud auto-assigned | Git repository |

---

## 🚀 Option 1: Unified Single-Port Deployment (Recommended)

In this mode, FastAPI serves the compiled React 19 production build directly from `frontend/dist/`.  
Both the interactive UI and all REST endpoints run on a **single port (`8000`)**, eliminating CORS issues and port routing complications.

### Step 1: Ensure Frontend is Built
```bash
cd /home/sourav/major-project/frontend
npm run build
cd ..
```

### Step 2: Launch with `deploy.sh`
```bash
./deploy.sh
```
*Alternatively, run Uvicorn directly:*
```bash
.venv/bin/uvicorn backend.api:app --host 0.0.0.0 --port 8000 --workers 2
```

### Step 3: Access the Application
- **Interactive Web Dashboard:** [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger REST Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Health Check:** [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

## 🐳 Option 2: Docker Container Deployment

A multi-stage `Dockerfile` and `docker-compose.yml` are provided in the repository root.

### Build & Run Container in Background
```bash
# Launch container
docker compose up -d --build

# View container logs
docker compose logs -f

# Check health status
docker compose ps
```

### Stop Container
```bash
docker compose down
```

---

## 💻 Option 3: Dual Development Mode (Hot Reload)

For developers actively modifying React JSX components or FastAPI endpoints:

### One-Command Dev Startup:
```bash
./deploy.sh --dev
```

### Or Manual Two-Terminal Startup:
**Terminal 1 (Backend API):**
```bash
cd /home/sourav/major-project
.venv/bin/uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 (Frontend with Vite HMR):**
```bash
cd /home/sourav/major-project/frontend
npm run dev -- --host
```

- Open [http://localhost:3000](http://localhost:3000) in your browser. Vite automatically proxies all `/api/*` calls to `http://localhost:8000`.

---

## 🖥 Option 4: Linux VPS Production Setup (Ubuntu/Debian)

To run the engine 24/7 on a remote Linux server (AWS EC2, DigitalOcean Droplet, Linode, Hetzner):

### 1. Install System Dependencies & Clone Repository
```bash
sudo apt update && sudo apt install -y python3-venv python3-pip git build-essential nginx
git clone <YOUR_REPO_URL> /var/www/crypto-engine
cd /var/www/crypto-engine
```

### 2. Set Up Virtual Environment & Dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Build Frontend Assets
```bash
cd frontend
npm install && npm run build
cd ..
```

### 4. Configure `systemd` Service
```bash
# Copy provided service file
sudo cp crypto-engine.service /etc/systemd/system/crypto-engine.service

# Edit username and working directory if different
sudo nano /etc/systemd/system/crypto-engine.service

# Reload and enable service
sudo systemctl daemon-reload
sudo systemctl enable --now crypto-engine
sudo systemctl status crypto-engine
```

### 5. Configure Nginx Reverse Proxy
```bash
# Copy provided Nginx config
sudo cp nginx_crypto_engine.conf /etc/nginx/sites-available/crypto-engine.conf
sudo ln -s /etc/nginx/sites-available/crypto-engine.conf /etc/nginx/sites-enabled/

# Test syntax and reload Nginx
sudo nginx -t
sudo systemctl reload nginx
```

### 6. Enable Free HTTPS / SSL with Certbot
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## ☁ Option 5: Deploying Backend to Render & Frontend to Vercel (Step-by-Step)

This distributed cloud architecture gives you the best performance:
- **Backend on Render:** Hosts FastAPI with high computational throughput and large BigInt support.
- **Frontend on Vercel:** Hosted on Vercel's global Edge CDN with sub-second asset delivery.

```
┌──────────────────────────────────────┐         REST API calls          ┌──────────────────────────────────────────────┐
│  Vercel Global Edge CDN (Frontend)   │ ──────────────────────────────> │   Render Python Web Service (Backend)        │
│  https://crypto-engine.vercel.app    │  (via VITE_API_BASE_URL)        │   https://crypto-engine-backend.onrender.com │
└──────────────────────────────────────┘                                 └──────────────────────────────────────────────┘
```

---

### Step 1: Push Project to GitHub

Ensure your local repository is committed and pushed to GitHub:
```bash
git add .
git commit -m "feat: configure deployment for Render and Vercel"
git push origin main
```

---

### Step 2: Deploy Backend to Render

1. Go to [dashboard.render.com](https://dashboard.render.com) and log in.
2. Click **New +** -> **Web Service**.
3. Select your GitHub repository (`major-project`).
4. Configure the settings:
   - **Name:** `crypto-engine-backend` (or your preferred name)
   - **Region:** Any (e.g., Oregon, Frankfurt)
   - **Branch:** `main`
   - **Root Directory:** Leave blank (or `./`)
   - **Runtime:** `Python 3`
   - **Build Command:**
     ```bash
     pip install --upgrade pip && pip install -r requirements.txt
     ```
   - **Start Command:**
     ```bash
     uvicorn backend.api:app --host 0.0.0.0 --port $PORT
     ```
   - **Plan:** Free
5. Under **Advanced Settings**:
   - **Health Check Path:** `/api/health`
   - Add Environment Variable:
     - `PYTHON_VERSION` = `3.12.3`
6. Click **Create Web Service**.
7. Render will build and deploy the backend. Once active, note your live backend URL:
   `https://<YOUR-RENDER-NAME>.onrender.com`
   *(Test by opening `https://<YOUR-RENDER-NAME>.onrender.com/api/health` in your browser)*

> [!NOTE]
> On Render's Free tier, services spin down after 15 minutes of inactivity. The first request after sleep may take ~30–45 seconds while the instance wakes up.

---

### Step 3: Deploy Frontend to Vercel

1. Go to [vercel.com/new](https://vercel.com/new) and log in with GitHub.
2. Under **Import Git Repository**, select your `major-project` repository.
3. In the **Configure Project** screen:
   - **Project Name:** `crypto-engine-dashboard` (or preferred)
   - **Framework Preset:** `Vite`
   - **Root Directory:** Click **Edit** and choose `frontend` 👈 *(Crucial Step!)*
   - **Build Command:** `npm run build` (default)
   - **Output Directory:** `dist` (default)
4. Expand **Environment Variables**:
   - **Key:** `VITE_API_BASE_URL`
   - **Value:** `https://<YOUR-RENDER-NAME>.onrender.com` *(Replace with your actual Render URL from Step 2, without trailing slash)*
5. Click **Deploy**.
6. Vercel will build and deploy the React 19 application in ~30 seconds, generating your live frontend URL (e.g. `https://crypto-engine-dashboard.vercel.app`).

---

### Step 4: Verify the Live Deployment

1. Open your live **Vercel URL** in any web browser or mobile device.
2. Go to **Exponent Analyzer**: Click **Generate Exponent** (1024-bit) then **Analyze**.
3. Go to **RSA Full Lifecycle**: Click **Generate Keypair**, **Sign Message**, and **Verify Signature**.
4. All calls will seamlessly execute against your Render backend!


---

## 🔍 Verification & Health Monitoring

To verify that the deployment is operating properly:

```bash
# 1. Check API Health
curl -s http://localhost:8000/api/health | jq .

# 2. Check Supported Hardware Backends
curl -s http://localhost:8000/api/backends | jq .

# 3. Test Algorithmic Dispatch
curl -s -X POST http://localhost:8000/api/backends/dispatch \
  -H "Content-Type: application/json" \
  -d '{"exponent": "1000", "backend": "asic_csa52"}' | jq .
```
