# Economic Intelligence Dashboard - Product Requirements Document

## Executive Summary

A unified economic intelligence platform that aggregates real-time financial data, real estate market reports, and curated newsletters into a single, beautiful dashboard with a unique "Today Feed" feature that follows a weekly learning schedule.

## Vision Statement

Create the "Bloomberg Terminal for Real Estate Investors" - starting simple but architected for scale. Ad-free, focused, beautiful UI/UX that respects users' time and attention.

## Core Concepts

### 1. Today Feed
- **Primary Innovation**: Daily themed content following the weekly schedule
  - Monday: Federal Reserve & Interest Rates (weekly digest)
  - Tuesday: Real Estate Markets (weekly digest) 
  - Wednesday: Economic Indicators (weekly digest)
  - Thursday: Regional & Banking (weekly digest)
  - Friday: Market Summary & Forward Look
- **Breaking News Override**: Critical updates appear regardless of day theme
- **Smart Summaries**: AI-generated weekly digests from all collected data

### 2. Source Library
- Dedicated sections for each data source
- Historical data with interactive charts
- Search and filter capabilities
- Export functionality for reports

### 3. Intelligence Layer
- AI agent for natural language queries
- Pattern detection and alerts
- Trend analysis and predictions
- Custom report generation

## Technical Architecture

### Backend Stack
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL (Railway)
- **Cache**: Redis (Railway)
- **Task Queue**: Celery with Redis backend
- **Scheduler**: APScheduler or Celery Beat
- **Email Processing**: IMAP client + BeautifulSoup parser
- **Hosting**: Railway.app

### Frontend Stack
- **Framework**: React with TypeScript
- **UI Library**: Shadcn/ui (beautiful, modern components)
- **Charts**: Recharts or D3.js
- **State Management**: Zustand
- **Hosting**: Cloudflare Pages
- **Build Tool**: Vite

### Data Sources & APIs

#### Phase 1 - Free APIs (MVP)
1. **FRED (Federal Reserve Economic Data)**
   - API: https://fred.stlouisfed.org/docs/api/fred/
   - Rate Limit: 120 requests/minute
   - Key Metrics: Fed Funds Rate, 10-Year Treasury, CPI, Unemployment

2. **Alpha Vantage** (backup for financial data)
   - API: Free tier available
   - Real-time and historical market data

3. **BEA (Bureau of Economic Analysis)**
   - API: https://apps.bea.gov/api/
   - GDP, Personal Income, Regional data

4. **BLS (Bureau of Labor Statistics)**
   - API: https://www.bls.gov/developers/
   - Employment, CPI, PPI data

5. **Census Bureau**
   - API: https://www.census.gov/data/developers/
   - Housing starts, construction permits

6. **Email Newsletter Parsing**
   - Bisnow (via dedicated email inbox)
   - Parse HTML emails for content extraction

#### Phase 2 - Enhanced Sources
- CBRE Research Reports (web scraping)
- Dallas Fed API
- News aggregation via NewsAPI
- Twitter/X API for real-time alerts

## Data Model

```python
# Core Entities

class DataSource:
    id: UUID
    name: str  # "FRED", "Bisnow", "BEA"
    category: str  # "federal_reserve", "real_estate", "economic"
    api_endpoint: Optional[str]
    fetch_schedule: str  # cron expression
    last_fetched: datetime
    is_active: bool

class DataPoint:
    id: UUID
    source_id: UUID
    metric_name: str  # "fed_funds_rate", "houston_cap_rate"
    value: Decimal
    unit: str  # "percent", "dollars", "index"
    timestamp: datetime
    metadata: JSON  # flexible field for source-specific data

class Newsletter:
    id: UUID
    source: str  # "Bisnow"
    category: str  # "houston", "national", "multifamily"
    subject: str
    content_html: Text
    content_text: Text
    summary: Text  # AI-generated
    received_at: datetime
    parsed_at: datetime
    key_points: JSON  # extracted data points

class UserSave:
    id: UUID
    user_id: UUID
    item_type: str  # "datapoint", "newsletter", "chart"
    item_id: UUID
    tags: List[str]
    saved_at: datetime

class Alert:
    id: UUID
    user_id: UUID
    condition: JSON  # {"metric": "fed_funds_rate", "operator": ">", "value": 5.5}
    last_triggered: datetime
    is_active: bool
```

## Feature Specifications

### Phase 1: MVP (Weeks 1-4)

#### 1.1 Basic Dashboard
- Today Feed with daily theme
- Current values for top 10 metrics
- Simple line charts for historical data
- Responsive design for desktop/tablet

#### 1.2 Data Collection
- FRED API integration (Fed rates, unemployment, CPI)
- Email parser for Bisnow newsletters
- Scheduled fetching (3 AM CST daily)
- Basic data storage in PostgreSQL

#### 1.3 User Features
- Simple authentication (email/password)
- Save/bookmark functionality
- Basic search across newsletters

### Phase 2: Enhanced Platform (Weeks 5-8)

#### 2.1 Advanced Visualizations
- Interactive multi-series charts
- Comparison tools
- Heat maps for regional data
- Custom date range selection

#### 2.2 AI Integration
- Natural language queries via GPT-4
- Auto-generated weekly summaries
- Trend detection and insights
- Smart categorization of newsletters

#### 2.3 Alerts & Monitoring
- Custom alert conditions
- Weekly digest emails (optional)
- Breaking news detection
- Threshold-based notifications

### Phase 3: Scale & Expand (Weeks 9-12)

#### 3.1 Multi-Market Support
- Add more cities beyond Houston/Austin
- Regional comparison tools
- Market selection preferences

#### 3.2 Advanced Features
- PDF report generation
- API for mobile app
- Team/sharing features
- Custom dashboards

#### 3.3 Premium Data Sources
- WSJ API integration (if available)
- CoStar data (if budget allows)
- Bloomberg data feeds

## API Design

### Core Endpoints

```python
# Dashboard
GET /api/today-feed
GET /api/dashboard/overview
GET /api/metrics/{metric_name}/historical

# Data Sources
GET /api/sources
GET /api/sources/{source_id}/data
POST /api/sources/{source_id}/refresh

# Newsletters
GET /api/newsletters
GET /api/newsletters/{id}
GET /api/newsletters/search?q={query}

# User Actions
POST /api/saves
GET /api/saves
DELETE /api/saves/{id}
POST /api/alerts
GET /api/alerts

# AI Features
POST /api/ai/query
GET /api/ai/summary/{date_range}
```

## Claude Code Implementation Plan

### Project Structure
```
economic-dashboard/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── services/
│   │   ├── workers/
│   │   └── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
└── docker-compose.yml
```

### Claude Code Agents Setup

Create these specialized agents using `/agent` command:

#### 1. Backend API Agent
```
/agent backend-api
Role: FastAPI backend development specialist
Context: Building economic data dashboard with FastAPI, PostgreSQL, Redis
Focus: API endpoints, data models, authentication, scheduled tasks
Technologies: Python, FastAPI, SQLAlchemy, Celery, APScheduler
```

#### 2. Data Fetcher Agent
```
/agent data-fetcher
Role: Data integration and ETL specialist
Context: Fetching data from FRED, BEA, BLS APIs and parsing email newsletters
Focus: API integrations, web scraping, email parsing, data normalization
Technologies: Python, requests, BeautifulSoup, pandas, email parsing
```

#### 3. Frontend UI Agent
```
/agent frontend-ui
Role: React and TypeScript UI development specialist
Context: Building responsive dashboard with React, TypeScript, and Shadcn/ui
Focus: Component architecture, state management, data visualization
Technologies: React, TypeScript, Recharts, Zustand, Tailwind CSS
```

#### 4. Database Agent
```
/agent database
Role: Database architecture and optimization specialist
Context: PostgreSQL database for time-series financial data
Focus: Schema design, indexes, query optimization, migrations
Technologies: PostgreSQL, SQLAlchemy, Alembic, Redis
```

#### 5. DevOps Agent
```
/agent devops
Role: Deployment and infrastructure specialist
Context: Deploying to Railway (backend) and Cloudflare Pages (frontend)
Focus: CI/CD, Docker, environment configuration, monitoring
Technologies: Docker, Railway, Cloudflare, GitHub Actions
```

### Development Phases

#### Week 1: Foundation
1. Set up project structure
2. Configure Railway PostgreSQL and Redis
3. Create base FastAPI application
4. Set up React with Vite and Shadcn/ui
5. Implement basic authentication

#### Week 2: Data Integration
1. FRED API integration
2. Email inbox setup and parser
3. Database schema implementation
4. Scheduled fetching system
5. Basic data storage

#### Week 3: Core Dashboard
1. Today Feed implementation
2. Metric cards and charts
3. Newsletter display
4. Save/bookmark functionality
5. Basic search

#### Week 4: Polish & Deploy
1. Responsive design refinements
2. Error handling and logging
3. Deploy backend to Railway
4. Deploy frontend to Cloudflare
5. Testing and bug fixes

## Configuration & Secrets

### Environment Variables (Backend)
```env
# Database
DATABASE_URL=postgresql://...
REDIS_URL=redis://...

# APIs
FRED_API_KEY=xxx
BEA_API_KEY=xxx
BLS_API_KEY=xxx

# Email
EMAIL_SERVER=imap.gmail.com
EMAIL_USERNAME=dashboard@example.com
EMAIL_PASSWORD=xxx

# Auth
JWT_SECRET_KEY=xxx
JWT_ALGORITHM=HS256

# General
ENVIRONMENT=production
TIMEZONE=America/Chicago
```

### Environment Variables (Frontend)
```env
VITE_API_URL=https://api.yourdomain.com
VITE_ENABLE_ANALYTICS=true
```

## Success Metrics

### Phase 1 Success Criteria
- [ ] Dashboard loads in under 2 seconds
- [ ] All free API integrations working
- [ ] Daily data fetching running reliably
- [ ] At least 5 Bisnow newsletters parsed daily
- [ ] Today Feed updates automatically

### Phase 2 Success Criteria  
- [ ] AI queries return relevant results
- [ ] Historical data goes back 1+ years
- [ ] Charts are interactive and exportable
- [ ] 95% uptime achieved

### Phase 3 Success Criteria
- [ ] Support for 5+ cities
- [ ] Mobile app released
- [ ] 100+ daily active users
- [ ] Premium features generating revenue

## Risk Mitigation

### Technical Risks
1. **API Rate Limits**: Implement caching and request queuing
2. **Email Parsing Breaks**: Multiple parsing strategies, fallbacks
3. **Data Quality**: Validation and anomaly detection
4. **Scaling Issues**: Horizontal scaling ready architecture

### Business Risks  
1. **Paywalled Content**: Start with free sources, add paid later
2. **User Adoption**: Focus on superior UX from day one
3. **Competition**: Unique "Today Feed" differentiator

## Appendix A: Data Source Details

### FRED Metrics to Track
- DFF - Federal Funds Rate
- DGS10 - 10-Year Treasury Rate  
- UNRATE - Unemployment Rate
- CPIAUCSL - Consumer Price Index
- MORTGAGE30US - 30-Year Mortgage Rate
- HOUST - Housing Starts
- PERMIT - Building Permits
- DEXUSEU - USD/EUR Exchange Rate

### Bisnow Newsletter Categories
Based on your subscriptions:
- **National**: Capital Markets, Multifamily, Retail, Investment
- **Regional**: Houston Morning Brief, Austin/San Antonio Brief
- **Specialized**: Student Housing, Texas Tea, What Tenants Want

### BEA Key Indicators
- GDP by State and Metropolitan Area
- Personal Income by State
- Regional Price Parities
- Industry GDP contributions

## Appendix B: UI/UX Principles

1. **Information Density**: Pack valuable data without clutter
2. **Scannability**: Key metrics visible in 3 seconds
3. **Progressive Disclosure**: Details on demand
4. **Dark Mode**: Essential for early morning reading
5. **Mobile First**: Though desktop optimized
6. **Zero Friction**: No popups, ads, or distractions

## Appendix C: Sample Claude Code Commands

```bash
# Start project
claude-code init economic-dashboard --stack fastapi-react

# Generate backend structure
claude-code generate backend --framework fastapi --db postgresql

# Create data fetcher
claude-code create service fred-fetcher --schedule "0 3 * * *"

# Build dashboard component
claude-code create component TodayFeed --type react-typescript

# Deploy to Railway
claude-code deploy backend --platform railway

# Generate API documentation
claude-code docs generate --format openapi
```

## Next Steps

1. **Immediate Actions**
   - Create Railway project and provision PostgreSQL/Redis
   - Set up dedicated Gmail for newsletter subscriptions
   - Apply for free API keys (FRED, BEA, BLS)
   - Create GitHub repository

2. **Week 1 Deliverables**
   - Working FastAPI backend with auth
   - React frontend with Shadcn/ui
   - FRED API integration
   - Basic Today Feed

3. **Success Validation**
   - Deploy MVP to production
   - Use for 1 week personally
   - Iterate based on experience
   - Prepare for user expansion