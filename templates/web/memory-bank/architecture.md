# Architecture

## Directory Structure
app/
├── layout.tsx
├── page.tsx
├── login/
└── dashboard/

components/
├── ui/
└── auth/

lib/
└── supabase/

## Data Flow
- Server Actions for mutations
- Client-side fetches for real-time subscriptions
- Middleware for route protection
