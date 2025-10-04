# Economic Dashboard - Frontend

A beautiful, production-ready React + TypeScript dashboard for economic indicators and market insights.

## Features

- Modern, dark-themed UI with Tailwind CSS
- Real-time economic indicators with sparkline visualizations
- Breaking news alerts and weekly summaries
- JWT-based authentication
- Responsive design for mobile and desktop
- Smooth animations and transitions
- Type-safe API integration with axios
- State management with Zustand

## Tech Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS with Shadcn/ui components
- **Charts**: Recharts
- **State Management**: Zustand
- **Routing**: React Router v6
- **HTTP Client**: Axios with interceptors
- **Animations**: Framer Motion + Lucide Icons

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
cd frontend
npm install
```

### Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=https://economic-dashboard-production.up.railway.app
```

### Development

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Production Build

```bash
npm run build
```

The production build will be in the `dist/` directory.

## Deployment to Cloudflare Pages

### Via Cloudflare Dashboard

1. Connect your GitHub repository to Cloudflare Pages
2. Configure build settings:
   - **Build command**: `npm run build`
   - **Build output directory**: `dist`
   - **Root directory**: `frontend`
3. Add environment variable:
   - `VITE_API_URL`: `https://economic-dashboard-production.up.railway.app`
4. Deploy!

### Via Wrangler CLI

```bash
# Install Wrangler
npm install -g wrangler

# Login to Cloudflare
wrangler login

# Deploy
npm run build
wrangler pages deploy dist --project-name=economic-dashboard
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/              # Shadcn/ui base components
│   │   ├── layout/          # Header, Navigation, Layout
│   │   ├── dashboard/       # Dashboard-specific components
│   │   └── charts/          # Chart components
│   ├── pages/
│   │   ├── Dashboard.tsx    # Main dashboard page
│   │   ├── Login.tsx        # Login page
│   │   └── Register.tsx     # Registration page
│   ├── hooks/
│   │   ├── useAuth.ts       # Authentication state & logic
│   │   └── useData.ts       # Dashboard data fetching
│   ├── services/
│   │   ├── api.ts           # Axios client with interceptors
│   │   └── auth.ts          # Auth API calls
│   ├── lib/
│   │   └── utils.ts         # Utility functions
│   ├── types/
│   │   └── index.ts         # TypeScript type definitions
│   ├── App.tsx              # Main app with routing
│   ├── main.tsx             # Entry point
│   └── index.css            # Global styles
├── public/                  # Static assets
├── .env                     # Environment variables
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## Key Components

### Authentication
- JWT token storage in localStorage
- Auto-redirect on 401 responses
- Protected routes with route guards

### API Integration
- Centralized API client with axios
- Request/response interceptors for auth
- Error handling and retry logic
- Type-safe API calls

### State Management
- `useAuth`: User authentication state
- `useData`: Dashboard data (today feed, metrics, breaking news, weekly summary)
- Persistent auth token

### Design System
- Dark mode by default
- Custom color palette (purple/blue theme)
- Consistent spacing and typography
- Smooth transitions and hover effects
- Loading skeletons for all async data

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint

## API Endpoints Used

- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user
- `GET /dashboard/today` - Today's feed
- `GET /dashboard/metrics` - Key metrics
- `GET /dashboard/breaking` - Breaking news
- `GET /dashboard/weekly` - Weekly summary

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

MIT
