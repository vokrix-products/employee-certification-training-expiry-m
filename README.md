# Employee Certification & Training Expiry Monitor

*Subdomain: employee-certificati.vokrix.com*

Track employee certifications, licenses, and training expiry dates. Upload PDF or CSV records to automatically extract employee name, certification type, issue date, and expiry date. Dashboard shows expired, expiring soon, valid, and missing certifications.

## Architecture

- **Dashboard**: Vite + React + TanStack Table (extraction archetype)
- **Backend**: Python poller running on Railway, processes uploads via Anthropic API
- **Database**: Supabase (PostgreSQL + Storage)
- **Deployment**: Vercel (dashboard), Railway (poller), Cloudflare DNS

## Setup

1. Clone repo
2. Copy `dashboard/.env.example` to `dashboard/.env.local` and fill variables
3. Run `cd dashboard && npm install && npm run dev`
4. Deploy poller: `railway up --service poller` (set env vars in Railway dashboard)
5. Configure Cloudflare DNS: CNAME `employee-certificati` → Railway app URL

## Environment Variables

| Variable | Description |
|----------|-------------|
| `VITE_SUPABASE_URL` | Supabase project URL |
| `VITE_SUPABASE_ANON_KEY` | Supabase anon key |
| `VITE_PRODUCT_ID` | Product identifier |
| `VITE_DEEPSEEK_API_KEY` | DeepSeek API key for extraction |

## Poller

`backend/poller.py` polls Supabase `jobs` table for pending uploads, extracts certifications using Anthropic API, stores results in Supabase Storage and inserts records. Deployed as a Railway service.