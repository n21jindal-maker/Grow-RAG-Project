# Deployment Plan: RAG MF Assistant

This document outlines the deployment strategy for the RAG MF Assistant application. 

**Infrastructure Choices:**
- **Backend (Python / FastAPI):** Railway
- **Frontend (Next.js):** Vercel

---

## 1. Backend Deployment (Railway)

The backend is built with FastAPI and runs the RAG pipeline. Railway will automatically build and deploy it using a Python environment.

### Prerequisites
- A GitHub repository containing the backend code (`rag-mf-assistant`).
- A [Railway account](https://railway.app/) linked to your GitHub account.

### Step-by-Step Deployment
1. **Prepare the Start Command:** 
   Railway usually auto-detects standard Python setups if a `Procfile` is present. Alternatively, you can specify a custom start command in Railway's settings. 
   - The entry point for FastAPI is in the `api` folder. 
   - **Start Command:** `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

2. **Create a Railway Project:**
   - Go to your Railway Dashboard.
   - Click **New Project** -> **Deploy from GitHub repo**.
   - Select the `rag-mf-assistant` repository.
   - *Note:* Change the **Root Directory** to `/rag-mf-assistant` in the Railway project settings, because the `requirements.txt` and backend code are located inside this subdirectory, not at the root of the repository.

3. **Configure Environment Variables:**
   - In your Railway project, navigate to the **Variables** tab.
   - Add all the required keys from your `.env` file, for example:
     - `GEMINI_API_KEY`
     - `GROQ_API_KEY`

4. **Verify CORS Settings:**
   - Ensure that `api/main.py` has CORS configured to allow requests from your future Vercel frontend URL (or `*` temporarily during testing).

5. **Deploy & Get URL:**
   - Railway will automatically start building.
   - Once deployed successfully, go to the **Settings** tab under **Public Networking** and click **Generate Domain**. 
   - **Save this Backend URL** (e.g., `https://your-backend.up.railway.app`); you will need it for the frontend.

---

## 2. Frontend Deployment (Vercel)

The frontend is a Next.js application located in the `frontend/` directory.

### Prerequisites
- A [Vercel account](https://vercel.com/) linked to your GitHub account.

### Step-by-Step Deployment
1. **Create a Vercel Project:**
   - Go to your Vercel Dashboard and click **Add New...** -> **Project**.
   - Import your `rag-mf-assistant` repository.

2. **Configure Build Settings:**
   - Because the Next.js app is not in the root of the repository, you must configure the Root Directory.
   - **Root Directory:** Click "Edit" and select `frontend`.
   - Vercel will automatically detect Next.js and apply the correct build commands (`npm run build`).

3. **Configure Environment Variables:**
   - Expand the **Environment Variables** section.
   - Add the backend API URL. For Next.js to expose it to the browser, it usually needs to be prefixed with `NEXT_PUBLIC_`.
   - Key: `NEXT_PUBLIC_API_URL` (or however your frontend is configured to read the API URL).
   - Value: `https://your-backend.up.railway.app` (the URL you generated from Railway).

4. **Deploy:**
   - Click **Deploy**. Vercel will install dependencies, build the Next.js app, and deploy it.

5. **Verification:**
   - Once deployment is complete, Vercel will provide you with a public URL (e.g., `https://rag-mf-assistant.vercel.app`).
   - Visit the URL to ensure the frontend loads correctly.
   - Submit a test query to verify that the frontend can successfully communicate with the Railway backend.

---

## 3. Post-Deployment Checklist

- [ ] Ensure backend CORS allows the exact Vercel frontend domain.
- [ ] Monitor Railway logs for any runtime errors during model inference or retrieval.
- [ ] Check Vercel logs if frontend requests are failing.
- [ ] If using local files (like a pickle file or Chroma DB) for the vector store, ensure Railway has enough memory/storage, or consider migrating to a managed vector database (like Pinecone or hosted Chroma) for production persistence.
