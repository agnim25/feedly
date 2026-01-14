# Feedly - Feed Aggregator

A modern web application for aggregating and organizing content across major sources (news sites, blogs, etc).

## Setup

1. **Activate virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
# Backend dependencies
pip install -r backend/requirements.txt

# Frontend dependencies
cd frontend
npm install
cd ..
```

3. **Create environment files:**

Create `backend/.env`:
```env
DATABASE_URL=sqlite:///./feedly.db

GOOGLE_CLIENT_ID=your-google-client-id  # Optional, for Google OAuth
GOOGLE_CLIENT_SECRET=your-google-client-secret  # Optional, for Google OAuth
GOOGLE_REDIRECT_URI=http://localhost:3000/google/callback  # Optional, for Google OAuth

CORS_ORIGINS=["http://localhost:3000"]
```

Create `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```
4. **Run services:**
```bash
./start.sh
```

This will start both the backend API (`http://localhost:8000`) and frontend app (`http://localhost:3000`).

Press `Ctrl+C` to stop all services.

## License

MIT

