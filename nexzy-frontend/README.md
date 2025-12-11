# Nexzy Frontend 🎯

**Modern React frontend for Nexzy: Project NEXT Intelligence**  
A sleek OSINT platform interface for detecting leaked university credentials.

## 🎨 Features

- ✅ **Modern UI/UX**: Built with React 19 + Tailwind CSS 4
- ✅ **Supabase Authentication**: Secure JWT-based user authentication
- ✅ **Real-time Updates**: Live scan progress via WebSocket connections
- ✅ **Command Palette**: Quick navigation with Ctrl/Cmd+K
- ✅ **Magnetic Interactions**: Custom hover effects and animations
- ✅ **Responsive Design**: Works seamlessly on desktop and mobile
- ✅ **Protected Routes**: Secure access control for authenticated users
- ✅ **Toast Notifications**: User-friendly feedback system

## 📁 Project Structure

```
nexzy-frontend/
├── src/
│   ├── components/          # Reusable UI components
│   ├── contexts/            # React context providers
│   ├── hooks/               # Custom React hooks
│   ├── lib/                 # API client and utilities
│   ├── pages/               # Page components
│   ├── App.jsx              # Main app component
│   └── main.jsx             # App entry point
├── .env.example             # Environment variables template
└── package.json             # Dependencies
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm/pnpm
- Supabase account with configured backend
- Backend API running (see nexzy-backend README)

### 1. Install Dependencies

```bash
cd nexzy-frontend
npm install
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

**Required variables:**

```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
VITE_API_URL=http://localhost:8001
```

**Get Supabase credentials:**

1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Open your project → **Settings** → **API**
3. Copy:
   - **Project URL** → `VITE_SUPABASE_URL`
   - **anon public key** → `VITE_SUPABASE_ANON_KEY`

### 3. Run Development Server

```bash
npm run dev
```

Frontend will start at: **http://localhost:5173**

### 4. Build for Production

```bash
npm run build
npm run preview  # Preview production build
```

## 🎯 Key Features

### Command Palette

Press **Ctrl+K** (Windows/Linux) or **Cmd+K** (Mac) for quick navigation:
- Dashboard, Search, Alerts, Settings, Logout

### Authentication Flow

1. **Landing Page**: Welcome screen
2. **Login/Signup**: Supabase authentication
3. **Protected Routes**: Auto-redirect if not authenticated
4. **Session Management**: Persistent sessions

### Real-time Scan Updates

- WebSocket connection for live updates
- Progress bars and toast notifications
- Automatic result refresh

### Dashboard

- Statistics overview (scans, credentials, alerts)
- Trend graphs and recent alerts
- Quick actions to start new scans

## 🛠️ Development

### Key Libraries

- **React 19**: Latest React features
- **React Router DOM 7**: Client-side routing
- **@supabase/supabase-js**: Supabase client
- **Tailwind CSS 4**: Utility-first styling
- **Lucide React**: Icon library

### Custom Hooks

- `useAuth()`: Authentication context
- `useToast()`: Toast notifications
- `useMagnetic()`: Magnetic hover effects
- `useWebSocket()`: WebSocket connections

## 🔒 Security

- Never commit `.env` files (added to .gitignore)
- JWT-based authentication
- Protected routes with guards
- Use HTTPS in production

## 🐛 Troubleshooting

### Cannot connect to backend

```bash
curl http://localhost:8001/health
# Verify VITE_API_URL in .env
```

### Authentication errors

Check Supabase credentials match backend configuration.

### Build errors

```bash
rm -rf node_modules package-lock.json
npm install
```

## 📦 Deployment

### Vercel/Netlify

Set environment variables in your platform:
- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_ANON_KEY`
- `VITE_API_URL` (production backend URL)

Build command: `npm run build`  
Publish directory: `dist`

## 🔗 Related

- [Backend Repository](../nexzy-backend/)
- [Database Schema](../nexzy-backend/SCHEMA.md)

---

**Built with ❤️ for Project NEXT Intelligence**
