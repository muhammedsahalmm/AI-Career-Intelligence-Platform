# AI Career Intelligence Platform

An AI-powered resume screening platform that predicts job roles, calculates semantic JD matching, and generates recruiter-style feedback using Google Gemini.

Built as a project demonstrating end-to-end ML + LLM + full-stack engineering.

---

## Features

- **Top-2 Role Prediction** - XGBoost classifier trained on 3,447 resumes (24 job categories)
- **Semantic JD Matching** - Sentence Transformers (all-MiniLM-L6-v2) + cosine similarity
- **Keyword Gap Analysis** - Dynamic matched/missing keyword extraction from JD
- **AI Recruiter Feedback** - Gemini 2.5 Flash generates strengths, gaps, and improvement suggestions
- **Multi-Resume Support** - Analyze up to 20 resumes per request
- **Rate Limiting** - Backend-enforced 5 Gemini requests per minute
- **Production-Ready API** - FastAPI with Pydantic schemas, validation, logging, health checks

---

## Tech Stack

| Layer | Technology |
|---|---|
| ML | scikit-learn, XGBoost, TF-IDF |
| NLP | Sentence Transformers, PyMuPDF |
| LLM | Google Gemini 2.5 Flash |
| Backend | FastAPI, Uvicorn, Pydantic |
| Frontend | Streamlit |
| DevOps | Docker, Docker Compose |
| Testing | pytest (29 tests passing) |

---

## Quick Start

### Prerequisites

- Docker and Docker Compose
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

### Setup

```bash
# 1. Clone
git clone https://github.com/muhammedsahalmm/AI-Career-Intelligence-Platform.git
cd AI-Career-Intelligence-Platform

# 2. Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 3. Build and run
docker compose up -d --build
```

### Access

- **Streamlit UI:** http://localhost:8501
- **FastAPI Docs (dev only):** http://localhost:8000/docs
- **FastAPI Health:** http://localhost:8000/health

---

## Project Structure

```
AI-Career-Intelligence-Platform/
|-- app.py                     # Streamlit UI
|-- api/main.py                # FastAPI backend
|-- modules/                   # Core logic (predictor, jd_matcher, recruiter_agent, etc.)
|-- services/resume_service.py # Analysis pipeline
|-- schemas/                   # Pydantic request/response models
|-- models/                    # Trained ML artifacts (.pkl)
|-- prompts/                   # Gemini prompt templates
|-- tests/                     # pytest test suite
|-- Dockerfile
|-- docker-compose.yml
|-- requirements.txt
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API status message |
| GET | `/health` | Health check |
| POST | `/analyze` | Analyze resumes against a JD |
| POST | `/generate-feedback` | Generate AI recruiter feedback |

---

## ML Model

- **Algorithm:** Tuned XGBoost
- **Features:** TF-IDF (max_features=5000, ngram_range=(1,2))
- **Dataset:** 3,447 resumes, 24 job categories
- **Accuracy:** 76.86%
- **Weighted F1:** 76.53%

---

## Testing

```bash
# Run all tests (mocked Gemini - no real API calls)
pytest tests/ -v
```

---

## License

MIT
