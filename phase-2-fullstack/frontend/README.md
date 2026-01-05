# Todo App Frontend

Next.js 16+ frontend with App Router, TypeScript, and Tailwind CSS.

## Setup

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.local.example .env.local

# Update .env.local with your backend URL
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Features

- ✅ User authentication (register/login)
- ✅ JWT token management with HTTP-only cookies
- ✅ Task CRUD operations
- ✅ Real-time task filtering (all/pending/completed)
- ✅ Responsive design with Tailwind CSS
- ✅ Server and Client Components
- ✅ TypeScript for type safety

## Project Structure

```
frontend/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   └── register/
│   ├── dashboard/
│   ├── api/
│   │   ├── auth/
│   │   └── tasks/
│   ├── layout.tsx
│   └── page.tsx
├── components/
│   ├── Header.tsx
│   ├── TaskList.tsx
│   ├── TaskItem.tsx
│   └── TaskForm.tsx
└── lib/
    ├── api.ts
    └── auth.ts
```

## Build for Production

```bash
npm run build
npm start
```
