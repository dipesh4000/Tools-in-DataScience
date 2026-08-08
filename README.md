# Tools in Data Science (TDS)

A collection of data science tools, exercises, and demos built for the IITM Tools in Data Science course.

## Structure

```
TDS/
├── week0/          — Introductory exercises (sentiment API, variance, HTML outputs)
├── week2/          — FastAPI demos (prediction API, observability, OAuth, tunnels)
├── Week6/          — Image forensics and prompt auditing tools
└── mlp_week8/      — Mask detection dataset and model (data excluded from git)
```

---

## week0 — Exercises

Small standalone scripts and outputs.

| File | Description |
|------|-------------|
| `q11.py` | FastAPI batch sentiment analysis endpoint (`POST /sentiment`) |
| `q3.py`, `q4.py`, `q7.py`, `q8.py` | Miscellaneous exercise scripts |
| `q10/ques.py` | FastAPI CSV exercise |
| `q1.html`, `q6.html` | HTML output exercises |
| `q-calculate-variance.json` | Variance calculation output |

Run the sentiment API:
```
cd week0
uvicorn q11:app --reload --port 8000
# POST http://localhost:8000/sentiment
```

---

## week2 — FastAPI Demos

### fastapi — Prediction API with Redis caching

A mini ML prediction API with validation, caching, background logging, and job status.

**Requirements:** Redis running on `localhost:6379`

```
cd week2/fastapi
pip install -r requirements.txt
uvicorn main:app --reload
```

Endpoints:
- `GET /health` — API + Redis status
- `POST /predict` — `{ "text": "...", "language": "en" }` → prediction
- `GET /predict/{id}` — retrieve a prediction
- `PATCH /predict/{id}/feedback` — submit feedback
- `DELETE /predict/{id}` — delete a prediction

### fastapi-observability-demo — Metrics with Prometheus

FastAPI app instrumented with Prometheus metrics.

```
cd week2/fastapi-observability-demo
docker compose up
```

See `README.md` inside for full details.

### google-oauth-fastapi — Google OAuth2 login

FastAPI app with Google OpenID Connect login via Authlib.

```
cd week2/google-oauth-fastapi
cp .env.example .env   # fill in GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, SESSION_SECRET
pip install -r requirements.txt
uvicorn main:app --reload
```

Endpoints: `GET /login`, `GET /me`, `GET /logout`

### tunnel-demo — Cloudflare Tunnel

Exposes a local FastAPI app via Cloudflare tunnel. See: https://tds.s-anand.net/2026-02/docs/week-2/10-cloudflare-tunnels/

---

## Week6 — Image Forensics & Prompt Auditing

### ImageForensics

Recovers a shuffled, rotated, and mirrored 6×6 image grid using beam search.

```
cd Week6/ImageForensics
pip install pillow numpy
python solve_rotated_grid.py
# Output: recovered_grid_and_token.png
```

### Prompt Auditing

Finds the optimal combination of prompt fragments to maximise LLM evaluation scores across multiple models (GPT-4o, GPT-4.1, GPT-4.1-mini, GPT-5-mini).

```
cd Week6/Prompt_Auditing
python main.py
```

---

## mlp_week8 — Mask Detection

CNN/MLP model for face mask detection using `with_mask` / `without_mask` image datasets.

> **Note:** The `data/` folder is excluded from git (see `.gitignore`).

```
cd mlp_week8
jupyter notebook practice.ipynb
```
