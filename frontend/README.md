# Beautiful Websites - Frontend

Multi-website platform frontend built with Next.js 14, TypeScript, and Tailwind CSS.

## Tech Stack

- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **State Management:** Zustand
- **Data Fetching:** TanStack Query (React Query)
- **Forms:** React Hook Form + Zod
- **UI Components:** Radix UI + Custom Components
- **HTTP Client:** Axios

## Getting Started

### Prerequisites

- Node.js 20+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.example .env.local

# Update .env.local with your API URLs
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build

```bash
npm run build
npm start
```

## Project Structure

```
src/
├── app/                    # Next.js App Router
│   ├── (public)/          # Public routes
│   ├── (dashboard)/       # Protected user routes
│   ├── (admin)/           # Admin routes
│   ├── layout.tsx         # Root layout
│   └── providers.tsx      # Global providers
├── components/            # React components
│   ├── ui/               # Base UI components
│   ├── shared/           # Shared components
│   ├── storefront/       # Storefront components
│   ├── booking/          # Booking components
│   └── ...
├── lib/                   # Core libraries
│   ├── api/              # API clients
│   ├── hooks/            # Custom React hooks
│   ├── store/            # Zustand stores
│   └── utils/            # Utility functions
└── types/                 # TypeScript types
```

## Features

- **Multi-Site Support:** Route-based site selection (`/:siteSlug`)
- **Type-Safe API:** TypeScript types for all API responses
- **Optimistic Updates:** Instant UI feedback with server synchronization
- **Cart Management:** Guest and user carts with merging on login
- **Authentication:** JWT-based auth with automatic token refresh
- **Responsive Design:** Mobile-first design with Tailwind CSS
- **SEO Optimized:** Server-side rendering for all public pages

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript compiler check
- `npm test` - Run tests
- `npm run format` - Format code with Prettier

## Environment Variables

See `.env.example` for all available environment variables.

Key variables:
- `NEXT_PUBLIC_API_GATEWAY_URL` - API Gateway URL
- `NEXT_PUBLIC_SITE_SERVICE_URL` - Site Service URL
- `NEXT_PUBLIC_STOREFRONT_SERVICE_URL` - Storefront Service URL
- `NEXT_PUBLIC_BOOKING_SERVICE_URL` - Booking Service URL

## Documentation

See [FRONTEND_ARCHITECTURE.md](../FRONTEND_ARCHITECTURE.md) for detailed architecture documentation.

## Contributing

1. Follow the existing code style
2. Write TypeScript types for all new code
3. Use React Query for data fetching
4. Use Zustand for global state
5. Follow the component structure in `/components`
