# Quick Command Reference

## Backend Commands

### Setup (One-time)
```powershell
cd backend
uv venv                          # Create virtual environment
.venv\Scripts\activate          # Activate venv
uv pip install -e .             # Install dependencies
copy .env.example .env          # Create environment file
# Edit .env with your DATABASE_URL
python test_setup.py            # Verify setup
```

### Daily Development
```powershell
cd backend
.venv\Scripts\activate          # Activate venv
uvicorn src.main:app --reload --port 8000  # Start server
# Open http://localhost:8000/docs
```

### Testing
```powershell
python test_setup.py            # Verify configuration
curl http://localhost:8000/health  # Health check
# Test in Swagger UI: http://localhost:8000/docs
```

## Frontend Commands (Coming Next)

### Setup (One-time)
```powershell
cd frontend
npm install                     # Install dependencies
copy .env.example .env.local   # Create environment file
# Edit .env.local with backend URL
```

### Daily Development
```powershell
cd frontend
npm run dev                     # Start Next.js dev server
# Open http://localhost:3000
```

## Full Stack (Both Services)

### Terminal 1 - Backend
```powershell
cd backend
.venv\Scripts\activate
uvicorn src.main:app --reload --port 8000
```

### Terminal 2 - Frontend
```powershell
cd frontend
npm run dev
```

## Docker (Alternative)

```powershell
docker-compose up              # Start all services
docker-compose down            # Stop all services
docker-compose logs -f         # View logs
```

## Git Commands

```powershell
git status                     # Check changes
git add .                      # Stage all changes
git commit -m "message"        # Commit with message
git push origin main           # Push to GitHub
```

## Troubleshooting

### Backend won't start
```powershell
# Check if venv is activated
.venv\Scripts\activate

# Reinstall dependencies
uv pip install -e .

# Check .env file exists and has DATABASE_URL
cat .env
```

### Database connection error
```
# Verify DATABASE_URL in .env
# Check Neon dashboard that database is active
# Ensure connection string has ?sslmode=require
```

### Port already in use
```powershell
# Backend on different port
uvicorn src.main:app --reload --port 8001

# Frontend on different port
npm run dev -- -p 3001
```

### Module not found errors
```powershell
# Reinstall dependencies
cd backend
.venv\Scripts\activate
uv pip install -e .

cd ../frontend
npm install
```

## Useful URLs

- **Backend Swagger UI**: http://localhost:8000/docs
- **Backend ReDoc**: http://localhost:8000/redoc
- **Backend Health**: http://localhost:8000/health
- **Frontend Dev**: http://localhost:3000
- **Neon Console**: https://console.neon.tech/
- **Vercel Dashboard**: https://vercel.com/dashboard

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=min-32-chars
CORS_ORIGINS=http://localhost:3000
ENVIRONMENT=development
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=same-as-backend
BETTER_AUTH_URL=http://localhost:3000
```

## Project Structure

```
hackathon-ii-full-stack/
├── backend/              # FastAPI backend
│   ├── src/
│   │   ├── main.py      # Entry point
│   │   ├── routers/     # API endpoints
│   │   ├── models/      # Database models
│   │   └── utils/       # Security utilities
│   ├── .env             # Environment variables
│   └── pyproject.toml   # Dependencies
├── frontend/            # Next.js frontend (coming next)
│   ├── app/             # App Router
│   ├── components/      # React components
│   ├── lib/             # API client
│   └── package.json     # Dependencies
├── specs/               # Specifications
├── README.md           # Main documentation
├── CLAUDE.md          # Agent instructions
└── docker-compose.yml # Docker config (coming)
```

## Next Steps Checklist

- [ ] Set up Neon database
- [ ] Update backend/.env with DATABASE_URL
- [ ] Run `python test_setup.py` (should pass all tests)
- [ ] Start backend server
- [ ] Test API in Swagger UI
- [ ] Tell Claude to create frontend
- [ ] Test full application
- [ ] Deploy to Vercel
- [ ] Record demo video
- [ ] Submit to GIAIC

---

**Save this file for quick reference during development!**
