/**
 * Next.js Middleware - Multi-Tenant Routing
 *
 * This middleware handles:
 * 1. Slug-based site resolution (yourplatform.com/rams-grocery)
 * 2. Subdomain-based site resolution (rams-grocery.yourplatform.com)
 * 3. Custom domain resolution (www.ramsgrocery.com)
 * 4. Site config caching
 * 5. Request context enrichment
 */

import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Site config cache (in production, use Redis)
const siteConfigCache = new Map<string, any>()
const CACHE_TTL = 5 * 60 * 1000 // 5 minutes

interface SiteConfig {
  site_id: string
  slug: string
  site_type: string
  template_id: string
  domain?: string
  status: string
  primary_color: string
  secondary_color: string
  font_family: string
  logo_url?: string
  meta_title?: string
  meta_description?: string
}

/**
 * Fetch site config from Site Service with caching
 */
async function fetchSiteConfig(
  identifier: string,
  type: 'slug' | 'domain'
): Promise<SiteConfig | null> {
  const cacheKey = `${type}:${identifier}`

  // Check cache
  const cached = siteConfigCache.get(cacheKey)
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.data
  }

  try {
    // Call Site Service
    const siteServiceUrl = process.env.SITE_SERVICE_URL || 'http://localhost:8010'
    const endpoint = type === 'slug'
      ? `/v1/sites/by-slug/${identifier}`
      : `/v1/sites/by-domain/${identifier}`

    const response = await fetch(`${siteServiceUrl}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        // Add service-to-service auth if needed
      },
      next: { revalidate: 300 } // Revalidate every 5 minutes
    })

    if (!response.ok) {
      if (response.status === 404) {
        return null
      }
      throw new Error(`Site Service returned ${response.status}`)
    }

    const siteConfig = await response.json()

    // Cache the result
    siteConfigCache.set(cacheKey, {
      data: siteConfig,
      timestamp: Date.now()
    })

    return siteConfig
  } catch (error) {
    console.error(`Error fetching site config for ${type}:${identifier}:`, error)
    return null
  }
}

/**
 * Extract site identifier from request
 */
function extractSiteIdentifier(request: NextRequest): {
  type: 'slug' | 'domain' | 'subdomain'
  identifier: string
} | null {
  const { pathname, host } = request.nextUrl

  // Strategy 1: Custom domain (e.g., www.ramsgrocery.com)
  const customDomains = process.env.CUSTOM_DOMAINS?.split(',') || []
  if (customDomains.some(domain => host.includes(domain))) {
    return { type: 'domain', identifier: host }
  }

  // Strategy 2: Subdomain (e.g., rams-grocery.yourplatform.com)
  const platformDomain = process.env.PLATFORM_DOMAIN || 'localhost:3000'
  if (host !== platformDomain && host.endsWith(platformDomain.split(':')[0])) {
    const subdomain = host.split('.')[0]
    if (subdomain !== 'www' && subdomain !== 'admin') {
      return { type: 'slug', identifier: subdomain }
    }
  }

  // Strategy 3: Slug-based routing (e.g., yourplatform.com/rams-grocery)
  const pathParts = pathname.split('/').filter(Boolean)
  if (pathParts.length > 0) {
    const slug = pathParts[0]

    // Exclude admin routes and static assets
    const excludedPaths = ['admin', 'api', '_next', 'static', 'favicon.ico', 'robots.txt', 'sitemap.xml']
    if (!excludedPaths.includes(slug)) {
      return { type: 'slug', identifier: slug }
    }
  }

  return null
}

/**
 * Main middleware function
 */
export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Skip middleware for static assets and API routes
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/api') ||
    pathname.startsWith('/static') ||
    pathname.match(/\.(ico|png|jpg|jpeg|svg|css|js|woff|woff2|ttf|eot)$/)
  ) {
    return NextResponse.next()
  }

  // Skip middleware for admin routes
  if (pathname.startsWith('/admin')) {
    return NextResponse.next()
  }

  // Extract site identifier
  const siteInfo = extractSiteIdentifier(request)

  if (!siteInfo) {
    // No site identifier found - redirect to platform home or 404
    return NextResponse.redirect(new URL('/', request.url))
  }

  // Fetch site config
  const siteConfig = await fetchSiteConfig(siteInfo.identifier, siteInfo.type === 'subdomain' ? 'slug' : siteInfo.type)

  if (!siteConfig) {
    // Site not found
    return NextResponse.rewrite(new URL('/404', request.url))
  }

  // Check if site is published
  if (siteConfig.status !== 'published') {
    return NextResponse.rewrite(new URL('/site-unavailable', request.url))
  }

  // Create response and add site context to headers
  const response = NextResponse.next()

  // Add site config to headers (accessible in route handlers and pages)
  response.headers.set('x-site-id', siteConfig.site_id)
  response.headers.set('x-site-slug', siteConfig.slug)
  response.headers.set('x-site-type', siteConfig.site_type)
  response.headers.set('x-site-config', JSON.stringify(siteConfig))

  return response
}

/**
 * Configure which routes should run through middleware
 */
export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    '/((?!_next/static|_next/image|favicon.ico|static|api/auth).*)',
  ],
}
