# Economic Intelligence Dashboard

Real-time economic data visualization and Bisnow real estate newsletter management system.

## Features

### 📊 Economic Data
- Federal Reserve (FRED) economic indicators
- Interactive charts with Recharts
- Real-time data updates
- Custom dashboard layouts

### 📰 Newsletter System
- Bisnow real estate newsletter integration via Gmail IMAP
- Individual article extraction and display
- Articles grouped by newsletter category (Texas Tea, Houston Morning Brief, etc.)
- Clickable article links to Bisnow website
- Custom bookmark lists (up to 10 per user)
- Bookmark individual articles for later reading

### 🔖 Bookmarking
- Create custom bookmark lists
- Save individual articles (not entire newsletters)
- Organize articles by topic
- Quick access to saved content

## Tech Stack

**Backend:**
- FastAPI (Python)
- PostgreSQL + SQLAlchemy 2.0
- Redis (caching)
- IMAP email parsing (BeautifulSoup4)
- Deployed on Railway

**Frontend:**
- React + TypeScript + Vite
- Tailwind CSS + Shadcn/ui
- Recharts for data visualization
- Deployed on Cloudflare Pages

## Project Structure

```
economic-dashboard/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/routes/  # API endpoints
│   │   ├── models/      # SQLAlchemy models
│   │   ├── schemas/     # Pydantic schemas
│   │   └── services/    # Business logic
│   ├── alembic/         # Database migrations
│   └── scripts/         # Utility scripts
└── frontend/            # React frontend
    └── src/
        ├── components/  # React components
        ├── pages/       # Page components
        ├── services/    # API clients
        └── types/       # TypeScript types
```

## Key Models

**Article** - Individual newsletter articles
- Headline, URL, category, received date
- Can appear in multiple newsletters
- Primary entity for bookmarking

**Newsletter** - Email container from Bisnow
- Source for articles
- Maintains original email metadata

**BookmarkList** - User's custom organization lists
- Max 10 lists per user
- Contains articles (not newsletters)

## API Endpoints

### Articles
- `GET /articles/recent` - Get recent articles (optionally grouped by category)
- `GET /articles/category/{category}` - Get articles for specific category
- `GET /articles/search?q={query}` - Search articles by headline
- `GET /articles/{id}` - Get single article with sources

### Bookmarks
- `GET /bookmarks/lists` - Get user's bookmark lists
- `POST /bookmarks/lists` - Create new list
- `POST /bookmarks/lists/{list_id}/articles/{article_id}` - Bookmark article
- `GET /bookmarks/lists/{list_id}/articles` - Get articles in list

### Newsletters
- `POST /newsletters/fetch?days=7` - Fetch newsletters from Gmail

## Environment Variables

**Backend (.env):**
```
DATABASE_URL=postgresql+asyncpg://...
REDIS_URL=redis://...
SECRET_KEY=...
```

**Frontend (.env):**
```
VITE_API_URL=https://api.example.com
```

## Deployment

**Backend:** Auto-deploys to Railway on push to main
**Frontend:** Auto-deploys to Cloudflare Pages on push to main

Migrations run automatically on Railway deployment.

## Development

**Backend:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```
