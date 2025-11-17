/**
 * Section Renderer - Dynamic Component Loader
 *
 * This component dynamically renders sections based on their type.
 * It acts as a registry of all available section components.
 *
 * To add a new section type:
 * 1. Create component in components/sections/
 * 2. Add to SECTION_COMPONENTS registry below
 * 3. Done! No other changes needed.
 */

import React from 'react'
import { HeroSection } from './sections/HeroSection'
import { ProductGridSection } from './sections/ProductGridSection'
import { ServiceGridSection } from './sections/ServiceGridSection'
import { TestimonialsSection } from './sections/TestimonialsSection'
import { ContactFormSection } from './sections/ContactFormSection'
import { WhatsAppButtonSection } from './sections/WhatsAppButtonSection'
import { CTASection } from './sections/CTASection'
import { FeaturesSection } from './sections/FeaturesSection'
import { PricingSection } from './sections/PricingSection'
import { FAQSection } from './sections/FAQSection'
import { BlogPreviewSection } from './sections/BlogPreviewSection'
import { GallerySection } from './sections/GallerySection'
import { BookingCalendarSection } from './sections/BookingCalendarSection'
import { LeadFormSection } from './sections/LeadFormSection'
import { StaffProfilesSection } from './sections/StaffProfilesSection'

/**
 * Section Component Registry
 *
 * Add new section types here to make them available for rendering
 */
const SECTION_COMPONENTS: Record<string, React.ComponentType<any>> = {
  // Layout sections
  hero: HeroSection,
  cta: CTASection,
  features: FeaturesSection,

  // E-commerce sections
  product_grid: ProductGridSection,
  pricing: PricingSection,

  // Service business sections
  service_grid: ServiceGridSection,
  booking_calendar: BookingCalendarSection,
  staff_profiles: StaffProfilesSection,

  // Content sections
  testimonials: TestimonialsSection,
  faq: FAQSection,
  blog_preview: BlogPreviewSection,
  gallery: GallerySection,

  // Interaction sections
  contact_form: ContactFormSection,
  lead_form: LeadFormSection,
  whatsapp_button: WhatsAppButtonSection,
}

/**
 * Section Renderer Props
 */
interface SectionRendererProps {
  type: string
  config: Record<string, any>
  siteId: string
  siteType: string
}

/**
 * Section Renderer Component
 */
export function SectionRenderer({
  type,
  config,
  siteId,
  siteType,
}: SectionRendererProps) {
  // Get component for this section type
  const Component = SECTION_COMPONENTS[type]

  if (!Component) {
    // Unknown section type
    console.error(`Unknown section type: ${type}`)

    // In development, show error
    if (process.env.NODE_ENV === 'development') {
      return (
        <div className="bg-red-50 border-2 border-red-500 p-8 m-4 rounded-lg">
          <h3 className="text-red-800 font-bold text-xl mb-2">
            ⚠️ Unknown Section Type
          </h3>
          <p className="text-red-700">
            Section type <code className="bg-red-200 px-2 py-1 rounded">{type}</code> is not registered.
          </p>
          <p className="text-red-700 mt-2 text-sm">
            Add it to <code>SECTION_COMPONENTS</code> in <code>SectionRenderer.tsx</code>
          </p>
        </div>
      )
    }

    // In production, silently skip
    return null
  }

  // Render component with config props
  return (
    <Component
      {...config}
      siteId={siteId}
      siteType={siteType}
    />
  )
}

/**
 * Get list of available section types (for admin panel)
 */
export function getAvailableSectionTypes(): string[] {
  return Object.keys(SECTION_COMPONENTS)
}

/**
 * Get section metadata (for admin panel section picker)
 */
export interface SectionMetadata {
  type: string
  name: string
  description: string
  category: 'layout' | 'ecommerce' | 'service' | 'content' | 'interaction'
  icon: string
  preview_image?: string
  default_config: Record<string, any>
}

export function getSectionMetadata(type: string): SectionMetadata | null {
  const metadata: Record<string, SectionMetadata> = {
    hero: {
      type: 'hero',
      name: 'Hero Section',
      description: 'Large banner with title, subtitle, and call-to-action',
      category: 'layout',
      icon: '🎯',
      default_config: {
        title: 'Welcome to Our Store',
        subtitle: 'Quality products at great prices',
        cta_text: 'Shop Now',
        cta_link: '/products',
        background_image: '/default-hero.jpg',
        text_alignment: 'center',
      },
    },
    product_grid: {
      type: 'product_grid',
      name: 'Product Grid',
      description: 'Display products in a responsive grid',
      category: 'ecommerce',
      icon: '🛍️',
      default_config: {
        columns: 3,
        show_price: true,
        show_add_to_cart: true,
        category_filter: null,
      },
    },
    service_grid: {
      type: 'service_grid',
      name: 'Service Grid',
      description: 'Display services with pricing',
      category: 'service',
      icon: '💼',
      default_config: {
        columns: 3,
        show_price: true,
        show_duration: true,
      },
    },
    testimonials: {
      type: 'testimonials',
      name: 'Testimonials',
      description: 'Customer reviews and ratings',
      category: 'content',
      icon: '⭐',
      default_config: {
        layout: 'grid',
        columns: 3,
        show_ratings: true,
        max_count: 6,
      },
    },
    contact_form: {
      type: 'contact_form',
      name: 'Contact Form',
      description: 'Let customers send inquiries',
      category: 'interaction',
      icon: '✉️',
      default_config: {
        fields: ['name', 'email', 'phone', 'message'],
        submit_text: 'Send Message',
        success_message: 'Thank you! We\'ll get back to you soon.',
      },
    },
    booking_calendar: {
      type: 'booking_calendar',
      name: 'Booking Calendar',
      description: 'Let customers book appointments',
      category: 'service',
      icon: '📅',
      default_config: {
        view: 'week',
        show_staff_selection: true,
        allow_multiple_bookings: false,
      },
    },
    whatsapp_button: {
      type: 'whatsapp_button',
      name: 'WhatsApp Button',
      description: 'Floating WhatsApp chat button',
      category: 'interaction',
      icon: '💬',
      default_config: {
        phone_number: '',
        pre_filled_message: 'Hi! I\'m interested in your services.',
        button_text: 'Chat on WhatsApp',
        position: 'bottom-right',
      },
    },
    faq: {
      type: 'faq',
      name: 'FAQ Section',
      description: 'Frequently asked questions',
      category: 'content',
      icon: '❓',
      default_config: {
        layout: 'accordion',
        category_filter: null,
      },
    },
  }

  return metadata[type] || null
}

/**
 * Get sections filtered by site type
 * Different site types may have different available sections
 */
export function getSectionsForSiteType(siteType: string): string[] {
  const siteTypeMap: Record<string, string[]> = {
    departmental_store: [
      'hero',
      'product_grid',
      'testimonials',
      'contact_form',
      'whatsapp_button',
      'cta',
      'features',
      'faq',
    ],
    tiffin_service: [
      'hero',
      'product_grid', // Meal plans
      'pricing',
      'testimonials',
      'contact_form',
      'whatsapp_button',
      'faq',
    ],
    salon: [
      'hero',
      'service_grid',
      'staff_profiles',
      'booking_calendar',
      'gallery',
      'testimonials',
      'contact_form',
      'whatsapp_button',
    ],
    coaching_center: [
      'hero',
      'service_grid', // Courses
      'staff_profiles', // Instructors
      'testimonials',
      'lead_form',
      'blog_preview',
      'faq',
    ],
    clinic: [
      'hero',
      'service_grid',
      'staff_profiles', // Doctors
      'booking_calendar',
      'testimonials',
      'contact_form',
      'faq',
    ],
  }

  return siteTypeMap[siteType] || Object.keys(SECTION_COMPONENTS)
}
