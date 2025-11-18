# Frontend Architecture

## Overview

Multi-website platform frontend built with Next.js 14 (App Router), TypeScript, and Tailwind CSS. Supports multiple site types (store, booking, tiffin, coaching) with shared components and site-specific features.

## Technology Stack

### Core Framework
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety and developer experience
- **React 18** - UI library with Server Components
- **Tailwind CSS** - Utility-first CSS framework

### State Management
- **Zustand** - Lightweight state management
- **React Query (TanStack Query)** - Server state management and caching
- **React Hook Form** - Form state and validation

### UI Components
- **Shadcn/ui** - Accessible component library
- **Radix UI** - Headless UI primitives
- **Lucide React** - Icon library
- **Framer Motion** - Animation library

### API Integration
- **Axios** - HTTP client with interceptors
- **Zod** - Schema validation
- **JWT Decode** - Token parsing

### Development Tools
- **ESLint** - Code linting
- **Prettier** - Code formatting
- **Husky** - Git hooks
- **Jest & React Testing Library** - Testing

## Architecture Principles

### 1. Site-Aware Architecture
Every page and component is site-aware:
- Site context from URL slug: `/:siteSlug/*`
- Site data fetched once and cached
- Site theme and branding applied globally

### 2. Multi-Tenant by Design
- All API calls include `site_id` from context
- User cart/orders scoped to current site
- Bookings specific to current site

### 3. Type-Safe API Layer
- Generated TypeScript types from backend schemas
- Centralized API client with interceptors
- Request/response validation with Zod

### 4. Performance Optimized
- Server Components for initial render
- Client Components only when needed (interactivity)
- Aggressive caching with React Query
- Image optimization with Next.js Image
- Code splitting by route and component

### 5. Progressive Enhancement
- Works without JavaScript (Server Components)
- Enhanced with client-side interactivity
- Optimistic updates for better UX

## Folder Structure

```
frontend/
├── src/
│   ├── app/                        # Next.js App Router
│   │   ├── (public)/              # Public routes (no auth)
│   │   │   ├── [siteSlug]/        # Site-specific routes
│   │   │   │   ├── page.tsx       # Homepage
│   │   │   │   ├── products/      # Storefront pages
│   │   │   │   │   ├── page.tsx           # Product listing
│   │   │   │   │   └── [productId]/       # Product detail
│   │   │   │   ├── booking/       # Booking pages
│   │   │   │   │   ├── page.tsx           # Service listing
│   │   │   │   │   ├── availability/      # Check availability
│   │   │   │   │   └── confirm/           # Booking confirmation
│   │   │   │   ├── cart/          # Shopping cart
│   │   │   │   ├── checkout/      # Checkout flow
│   │   │   │   ├── blog/          # Content pages
│   │   │   │   └── contact/       # Lead capture
│   │   │   ├── auth/              # Auth pages
│   │   │   │   ├── login/
│   │   │   │   ├── signup/
│   │   │   │   └── forgot-password/
│   │   │   └── layout.tsx
│   │   ├── (dashboard)/           # Protected routes
│   │   │   ├── [siteSlug]/
│   │   │   │   ├── dashboard/     # User dashboard
│   │   │   │   ├── orders/        # Order history
│   │   │   │   ├── bookings/      # Booking history
│   │   │   │   └── profile/       # User profile
│   │   │   └── layout.tsx
│   │   ├── (admin)/               # Admin routes
│   │   │   ├── admin/
│   │   │   │   ├── sites/         # Site management
│   │   │   │   ├── products/      # Product management
│   │   │   │   ├── bookings/      # Booking management
│   │   │   │   └── leads/         # Lead management
│   │   │   └── layout.tsx
│   │   ├── api/                   # API routes (if needed)
│   │   │   └── webhooks/
│   │   ├── layout.tsx             # Root layout
│   │   └── providers.tsx          # Global providers
│   │
│   ├── components/                # React components
│   │   ├── ui/                    # Base UI components (shadcn)
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── input.tsx
│   │   │   ├── dialog.tsx
│   │   │   └── ...
│   │   ├── shared/                # Shared components
│   │   │   ├── Header.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── Navigation.tsx
│   │   │   ├── SiteThemeProvider.tsx
│   │   │   └── LoadingSpinner.tsx
│   │   ├── storefront/            # Storefront components
│   │   │   ├── ProductCard.tsx
│   │   │   ├── ProductGrid.tsx
│   │   │   ├── ProductFilter.tsx
│   │   │   ├── CartDrawer.tsx
│   │   │   ├── CartItem.tsx
│   │   │   ├── CheckoutForm.tsx
│   │   │   └── OrderSummary.tsx
│   │   ├── booking/               # Booking components
│   │   │   ├── ServiceCard.tsx
│   │   │   ├── ServiceList.tsx
│   │   │   ├── AvailabilityCalendar.tsx
│   │   │   ├── TimeSlotPicker.tsx
│   │   │   ├── BookingForm.tsx
│   │   │   └── BookingCard.tsx
│   │   ├── content/               # Content components
│   │   │   ├── BlogPost.tsx
│   │   │   ├── BlogList.tsx
│   │   │   └── PageRenderer.tsx
│   │   ├── lead/                  # Lead components
│   │   │   ├── ContactForm.tsx
│   │   │   ├── QuoteForm.tsx
│   │   │   └── NewsletterForm.tsx
│   │   └── widgets/               # Widget components
│   │       ├── TestimonialWidget.tsx
│   │       ├── CTAWidget.tsx
│   │       ├── HeroWidget.tsx
│   │       └── WidgetRenderer.tsx
│   │
│   ├── lib/                       # Core libraries
│   │   ├── api/                   # API clients
│   │   │   ├── client.ts          # Base axios client
│   │   │   ├── sites.ts           # Site service API
│   │   │   ├── storefront.ts      # Storefront service API
│   │   │   ├── booking.ts         # Booking service API
│   │   │   ├── lead.ts            # Lead service API
│   │   │   ├── content.ts         # Content service API
│   │   │   ├── widget.ts          # Widget service API
│   │   │   └── auth.ts            # Auth service API
│   │   ├── hooks/                 # Custom React hooks
│   │   │   ├── useSite.ts         # Site context hook
│   │   │   ├── useCart.ts         # Cart management
│   │   │   ├── useAuth.ts         # Authentication
│   │   │   ├── useProducts.ts     # Product queries
│   │   │   └── useBooking.ts      # Booking queries
│   │   ├── store/                 # Zustand stores
│   │   │   ├── cartStore.ts       # Cart state
│   │   │   ├── authStore.ts       # Auth state
│   │   │   └── siteStore.ts       # Site state
│   │   ├── utils/                 # Utility functions
│   │   │   ├── formatting.ts      # Date, currency formatting
│   │   │   ├── validation.ts      # Form validation schemas
│   │   │   └── helpers.ts         # General helpers
│   │   └── constants.ts           # App constants
│   │
│   ├── types/                     # TypeScript types
│   │   ├── api/                   # API response types
│   │   │   ├── site.ts
│   │   │   ├── storefront.ts
│   │   │   ├── booking.ts
│   │   │   ├── lead.ts
│   │   │   ├── content.ts
│   │   │   └── widget.ts
│   │   ├── models/                # Domain models
│   │   │   ├── Site.ts
│   │   │   ├── Product.ts
│   │   │   ├── Cart.ts
│   │   │   ├── Order.ts
│   │   │   ├── Booking.ts
│   │   │   └── User.ts
│   │   └── index.ts
│   │
│   └── middleware.ts              # Next.js middleware (auth, etc.)
│
├── public/                        # Static assets
│   ├── images/
│   ├── icons/
│   └── fonts/
│
├── tests/                         # Tests
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── .env.local                     # Environment variables
├── .env.example
├── next.config.js                 # Next.js configuration
├── tailwind.config.ts             # Tailwind configuration
├── tsconfig.json                  # TypeScript configuration
└── package.json

```

## Key Features Implementation

### 1. Site Context Management

**Site Detection Flow:**
```
URL: /:siteSlug/products
↓
Middleware extracts siteSlug
↓
Layout fetches site data (Server Component)
↓
Site context provided to children
↓
All API calls use site_id from context
```

**Implementation:**
```typescript
// app/[siteSlug]/layout.tsx
export default async function SiteLayout({ params, children }) {
  const site = await getSiteBySlug(params.siteSlug);

  return (
    <SiteProvider site={site}>
      <SiteThemeProvider branding={site.branding}>
        <Header />
        {children}
        <Footer />
      </SiteThemeProvider>
    </SiteProvider>
  );
}
```

### 2. Multi-Service Integration

**API Client Architecture:**
```typescript
// lib/api/client.ts
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_GATEWAY_URL,
  timeout: 10000,
});

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = getAuthToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Service-specific clients
export const siteApi = createServiceClient('/api/sites');
export const storefrontApi = createServiceClient('/api/storefront');
export const bookingApi = createServiceClient('/api/bookings');
```

**React Query Integration:**
```typescript
// lib/hooks/useProducts.ts
export function useProducts(siteId: string, filters: ProductFilters) {
  return useQuery({
    queryKey: ['products', siteId, filters],
    queryFn: () => storefrontApi.getProducts(siteId, filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
```

### 3. Cart Management

**Zustand Store:**
```typescript
// lib/store/cartStore.ts
interface CartStore {
  cartId: string | null;
  items: CartItem[];
  total: number;

  // Actions
  addItem: (product: Product, quantity: number) => Promise<void>;
  updateQuantity: (itemId: string, quantity: number) => Promise<void>;
  removeItem: (itemId: string) => Promise<void>;
  clearCart: () => void;
  syncWithServer: () => Promise<void>;
}

export const useCartStore = create<CartStore>((set, get) => ({
  // Implementation with optimistic updates
}));
```

**Guest Cart Handling:**
- Generate session ID on first visit
- Store in localStorage and cookies
- Merge with user cart on login
- Persist across page refreshes

### 4. Booking Flow

**Multi-Step Booking Process:**
```
1. Select Service
   ↓
2. Choose Date
   ↓
3. Check Availability (API call)
   ↓
4. Select Time Slot
   ↓
5. Provide Details
   ↓
6. Confirm Booking
```

**Implementation:**
```typescript
// components/booking/BookingWizard.tsx
export function BookingWizard() {
  const [step, setStep] = useState(1);
  const [selectedService, setSelectedService] = useState<Service | null>(null);
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [selectedSlot, setSelectedSlot] = useState<TimeSlot | null>(null);

  // Fetch availability when service and date selected
  const { data: slots } = useAvailability(siteId, {
    serviceId: selectedService?.service_id,
    date: selectedDate,
  });

  return (
    <div>
      {step === 1 && <ServiceSelection onSelect={handleServiceSelect} />}
      {step === 2 && <DatePicker onSelect={handleDateSelect} />}
      {step === 3 && <TimeSlotPicker slots={slots} onSelect={handleSlotSelect} />}
      {step === 4 && <BookingForm onSubmit={handleSubmit} />}
      {step === 5 && <BookingConfirmation booking={booking} />}
    </div>
  );
}
```

### 5. Theme Customization

**Site-Specific Branding:**
```typescript
// components/shared/SiteThemeProvider.tsx
export function SiteThemeProvider({ branding, children }) {
  useEffect(() => {
    // Apply branding to CSS variables
    document.documentElement.style.setProperty('--primary-color', branding.primary_color);
    document.documentElement.style.setProperty('--secondary-color', branding.secondary_color);
    document.documentElement.style.setProperty('--font-family', branding.font_family);
  }, [branding]);

  return <>{children}</>;
}
```

**Tailwind CSS Configuration:**
```javascript
// tailwind.config.ts
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: 'var(--primary-color)',
        secondary: 'var(--secondary-color)',
      },
      fontFamily: {
        sans: 'var(--font-family)',
      },
    },
  },
};
```

## Page Implementations

### Storefront Pages

#### Product Listing (`/[siteSlug]/products`)
- Grid/List view toggle
- Category filtering
- Search functionality
- Price range filter
- Tag-based filtering
- Pagination
- Server-side rendering for SEO

#### Product Detail (`/[siteSlug]/products/[productId]`)
- Image gallery
- Variant selection (size, color, etc.)
- Stock availability
- Add to cart with quantity
- Related products
- Product reviews (future)

#### Shopping Cart (`/[siteSlug]/cart`)
- Item list with thumbnails
- Quantity adjustment
- Remove items
- Coupon code (future)
- Order summary
- Checkout button

#### Checkout (`/[siteSlug]/checkout`)
- Multi-step form (shipping, payment, review)
- Address autocomplete
- Payment method selection
- Order review
- Order confirmation

### Booking Pages

#### Service Listing (`/[siteSlug]/booking`)
- Service categories
- Service cards with duration, price
- Filter by category
- Search services

#### Availability Check (`/[siteSlug]/booking/availability`)
- Service selection
- Date picker (calendar view)
- Available time slots
- Provider selection (optional)
- Duration display

#### Booking Confirmation (`/[siteSlug]/booking/confirm`)
- Booking details summary
- Customer information form
- Special requests
- Booking confirmation
- Calendar invite download

### Dashboard Pages

#### My Orders (`/[siteSlug]/dashboard/orders`)
- Order history list
- Order status tracking
- Order details modal
- Reorder functionality
- Download invoice

#### My Bookings (`/[siteSlug]/dashboard/bookings`)
- Upcoming bookings
- Past bookings
- Cancel booking
- Reschedule booking
- Booking details

## API Integration Patterns

### 1. Server Components (Default)
```typescript
// app/[siteSlug]/products/page.tsx
export default async function ProductsPage({ params, searchParams }) {
  // Fetch on server for SEO
  const products = await storefrontApi.getProducts(params.siteSlug, {
    page: searchParams.page || 1,
    category: searchParams.category,
  });

  return <ProductGrid products={products} />;
}
```

### 2. Client Components (Interactive)
```typescript
'use client';

// components/storefront/ProductFilter.tsx
export function ProductFilter() {
  const { siteId } = useSite();
  const [filters, setFilters] = useState<ProductFilters>({});

  // Use React Query for client-side data fetching
  const { data, isLoading } = useProducts(siteId, filters);

  return (
    <div>
      <FilterControls onChange={setFilters} />
      {isLoading ? <LoadingSpinner /> : <ProductGrid products={data} />}
    </div>
  );
}
```

### 3. Optimistic Updates
```typescript
// lib/hooks/useCart.ts
export function useAddToCart() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (item) => cartApi.addItem(item),
    onMutate: async (newItem) => {
      // Optimistically update UI
      await queryClient.cancelQueries(['cart']);
      const previousCart = queryClient.getQueryData(['cart']);

      queryClient.setQueryData(['cart'], (old) => ({
        ...old,
        items: [...old.items, newItem],
      }));

      return { previousCart };
    },
    onError: (err, newItem, context) => {
      // Rollback on error
      queryClient.setQueryData(['cart'], context.previousCart);
    },
    onSuccess: () => {
      // Refetch to get accurate data from server
      queryClient.invalidateQueries(['cart']);
    },
  });
}
```

## Authentication Flow

### 1. JWT Token Management
```typescript
// lib/api/auth.ts
export const authService = {
  login: async (email: string, password: string) => {
    const response = await authApi.post('/login', { email, password });
    const { access_token, refresh_token, user } = response.data;

    // Store tokens
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);

    return user;
  },

  refreshToken: async () => {
    const refreshToken = localStorage.getItem('refresh_token');
    const response = await authApi.post('/refresh', { refresh_token: refreshToken });
    localStorage.setItem('access_token', response.data.access_token);
  },
};
```

### 2. Protected Routes
```typescript
// middleware.ts
export function middleware(request: NextRequest) {
  const token = request.cookies.get('access_token');

  // Protect dashboard routes
  if (request.nextUrl.pathname.startsWith('/dashboard') && !token) {
    return NextResponse.redirect(new URL('/auth/login', request.url));
  }

  return NextResponse.next();
}
```

## Performance Optimizations

### 1. Image Optimization
```typescript
// Use Next.js Image component
<Image
  src={product.image_url}
  alt={product.name}
  width={400}
  height={400}
  placeholder="blur"
  loading="lazy"
/>
```

### 2. Code Splitting
```typescript
// Dynamic imports for heavy components
const BookingWizard = dynamic(() => import('@/components/booking/BookingWizard'), {
  loading: () => <LoadingSpinner />,
  ssr: false,
});
```

### 3. Caching Strategy
```typescript
// React Query configuration
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      refetchOnWindowFocus: false,
    },
  },
});
```

## Environment Variables

```env
# .env.local
NEXT_PUBLIC_API_GATEWAY_URL=http://localhost/api
NEXT_PUBLIC_AUTH_SERVICE_URL=http://localhost:8000
NEXT_PUBLIC_SITE_SERVICE_URL=http://localhost:8010
NEXT_PUBLIC_STOREFRONT_SERVICE_URL=http://localhost:8011
NEXT_PUBLIC_BOOKING_SERVICE_URL=http://localhost:8012

# Analytics (optional)
NEXT_PUBLIC_GA_ID=
NEXT_PUBLIC_SENTRY_DSN=

# Feature Flags
NEXT_PUBLIC_ENABLE_REVIEWS=false
NEXT_PUBLIC_ENABLE_WISHLIST=false
```

## Build & Deployment

### Development
```bash
npm run dev
```

### Production Build
```bash
npm run build
npm run start
```

### Docker
```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
EXPOSE 3000
CMD ["npm", "start"]
```

## Testing Strategy

### Unit Tests
- Component testing with React Testing Library
- Hook testing with @testing-library/react-hooks
- Utility function testing with Jest

### Integration Tests
- API client testing with MSW (Mock Service Worker)
- Form submission flows
- Cart operations

### E2E Tests
- Critical user journeys with Playwright
- Checkout flow
- Booking flow
- Authentication flow

## Accessibility

- WCAG 2.1 Level AA compliance
- Semantic HTML
- ARIA labels and roles
- Keyboard navigation
- Screen reader support
- Focus management
- Color contrast ratios

## SEO Optimization

- Server-side rendering for all public pages
- Dynamic meta tags per page
- Open Graph tags
- Structured data (JSON-LD)
- Sitemap generation
- Robots.txt
- Canonical URLs

## Next Steps

1. **Phase 1: Core Setup** ✓
   - Project initialization
   - Folder structure
   - Base configuration

2. **Phase 2: API Layer**
   - API clients for all services
   - React Query setup
   - Type definitions

3. **Phase 3: Storefront**
   - Product pages
   - Cart functionality
   - Checkout flow

4. **Phase 4: Booking**
   - Service listing
   - Availability checking
   - Booking flow

5. **Phase 5: Dashboard**
   - User profile
   - Order history
   - Booking management

6. **Phase 6: Admin**
   - Product management
   - Booking management
   - Lead management

7. **Phase 7: Polish**
   - Animations
   - Loading states
   - Error handling
   - Testing
