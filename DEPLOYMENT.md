# Deployment

This project has two deployable apps:

- `idp-pipeline`: FastAPI backend for PDF processing.
- `project 2/docflow`: Next.js frontend.

## Backend on Render

You can either use the included `render.yaml` blueprint or create a Web Service manually.

Manual setup:

1. Create a new Render Web Service from the repository.
2. Set the root directory to `idp-pipeline`.
3. Use these commands:
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn api.routes:app --host 0.0.0.0 --port $PORT`
4. Add environment variables:
   - `API_GEMINI_KEY`: your Gemini API key.
   - `CORS_ORIGINS`: your Vercel frontend URL, for example `https://your-app.vercel.app`.
   - Optional: `DB_PATH`, `OUTPUT_DIR`, `APPROVAL_THRESHOLD`, `CONFIDENCE_THRESHOLD`, `DTI_THRESHOLD`, `GEMINI_MODEL`.
5. After deploy, verify `https://your-render-service.onrender.com/health`.

For persistent job history on Render, add a disk mounted at `/var/data` and set:

```text
DB_PATH=/var/data/idp_pipeline.sqlite3
OUTPUT_DIR=/var/data/output
```

## Frontend on Vercel

1. Import the repository in Vercel.
2. Set the project root directory to `project 2/docflow`.
3. Add this environment variable:
   - `NEXT_PUBLIC_API_BASE_URL`: your Render backend URL, for example `https://your-render-service.onrender.com`.
4. Deploy.

## Local Run

Backend:

```bash
cd idp-pipeline
pip install -r requirements.txt
uvicorn api.routes:app --reload --host 0.0.0.0 --port 8000
```

Frontend:

```bash
cd "project 2/docflow"
npm install
npm run dev
```
