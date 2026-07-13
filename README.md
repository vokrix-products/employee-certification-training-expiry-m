# Employee Certification & Training Expiry Monitor

Dashboard for tracking employee certifications, licenses, and training expiry dates. Built with Shadcn Admin dashboard template and supabase backend.

## Features
- Upload certification records (PDF/CSV) for automated extraction
- Monitor expiry dates with status indicators (Valid, Expiring Soon, Expired, Missing)
- Real-time updates via Supabase
- AI-powered extraction using Claude API

## Tech Stack
- Frontend: React + TypeScript + Vite (Shadcn Admin)
- Backend: Python poller (Railway worker)
- Database: Supabase (Postgres)
- Storage: Supabase Storage
- AI: Anthropic Claude

## Deployment
- Frontend: Vercel
- Backend: Railway (background worker)
- DNS: Cloudflare

