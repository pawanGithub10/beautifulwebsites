/**
 * Dynamic Site Page - Public Website Renderer
 *
 * This page renders any website based on its slug.
 * It fetches site config and sections from Site Service and renders them dynamically.
 *
 * Examples:
 * - /rams-grocery → Departmental Store
 * - /bella-salon → Salon Website
 * - /tasty-tiffin → Tiffin Service
 */

import { Metadata } from 'next'
import { headers } from 'next/headers'
import { notFound } from 'next/navigation'
import { SectionRenderer } from '@/components/SectionRenderer'
import { ThemeProvider } from '@/components/ThemeProvider'
import { getSiteSections } from '@/lib/api/site-service'

interface SitePageProps {
  params: {
    slug: string
  }
  searchParams: {
    page?: string
  }
}

/**
 * Generate metadata for SEO
 */
export async function generateMetadata({
  params,
}: SitePageProps): Promise<Metadata> {
  // Get site config from middleware headers
  const headersList = headers()
  const siteConfigHeader = headersList.get('x-site-config')

  if (!siteConfigHeader) {
    return {
      title: 'Site Not Found',
    }
  }

  const siteConfig = JSON.parse(siteConfigHeader)

  return {
    title: siteConfig.meta_title || siteConfig.slug,
    description: siteConfig.meta_description || `Welcome to ${siteConfig.slug}`,
    openGraph: {
      title: siteConfig.meta_title || siteConfig.slug,
      description: siteConfig.meta_description,
      images: siteConfig.logo_url ? [siteConfig.logo_url] : [],
    },
    icons: {
      icon: siteConfig.favicon_url || '/default-favicon.ico',
    },
  }
}

/**
 * Main Site Page Component
 */
export default async function SitePage({ params, searchParams }: SitePageProps) {
  // Get site config from middleware headers
  const headersList = headers()
  const siteConfigHeader = headersList.get('x-site-config')

  if (!siteConfigHeader) {
    notFound()
  }

  const siteConfig = JSON.parse(siteConfigHeader)

  // Determine which page to render
  const pagePath = searchParams.page || '/'

  // Fetch sections for this page
  const sections = await getSiteSections(siteConfig.site_id, pagePath)

  if (!sections || sections.length === 0) {
    // No sections configured for this page
    return (
      <ThemeProvider siteConfig={siteConfig}>
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Page Under Construction
            </h1>
            <p className="text-gray-600">
              This page is being set up. Check back soon!
            </p>
          </div>
        </div>
      </ThemeProvider>
    )
  }

  return (
    <ThemeProvider siteConfig={siteConfig}>
      <div className="site-page">
        {/* Render each section */}
        {sections
          .filter((section: any) => section.is_visible)
          .sort((a: any, b: any) => a.section_order - b.section_order)
          .map((section: any) => (
            <SectionRenderer
              key={section.section_id}
              type={section.section_type}
              config={section.section_config}
              siteId={siteConfig.site_id}
              siteType={siteConfig.site_type}
            />
          ))}

        {/* Floating action buttons (WhatsApp, etc.) */}
        <FloatingActions siteId={siteConfig.site_id} />
      </div>
    </ThemeProvider>
  )
}

/**
 * Floating action buttons (WhatsApp, Chatbot, etc.)
 */
async function FloatingActions({ siteId }: { siteId: string }) {
  // Fetch widgets configured for floating display
  // For now, just render a WhatsApp button if configured

  return (
    <div className="fixed bottom-6 right-6 flex flex-col gap-4 z-50">
      {/* WhatsApp button will be rendered by widget service */}
    </div>
  )
}

/**
 * Generate static params for static site generation (optional)
 * In production, you might want to pre-render popular sites
 */
export async function generateStaticParams() {
  // Fetch list of sites to pre-render
  // For now, return empty array (all sites rendered on-demand)
  return []
}

/**
 * Revalidate configuration
 * ISR: Regenerate page every 5 minutes
 */
export const revalidate = 300
