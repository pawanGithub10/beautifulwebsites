/**
 * Hero Section Component
 *
 * A large, prominent banner section typically used at the top of pages.
 * Supports:
 * - Background image or gradient
 * - Title, subtitle, and CTA button
 * - Flexible text alignment
 * - Responsive design
 */

'use client'

import React from 'react'
import Image from 'next/image'
import Link from 'next/link'
import { cn } from '@/lib/utils'

interface HeroSectionProps {
  // Content
  title: string
  subtitle?: string
  cta_text?: string
  cta_link?: string
  secondary_cta_text?: string
  secondary_cta_link?: string

  // Visual
  background_image?: string
  background_gradient?: string
  background_overlay?: boolean
  overlay_opacity?: number

  // Layout
  text_alignment?: 'left' | 'center' | 'right'
  height?: 'small' | 'medium' | 'large' | 'full'
  text_color?: 'light' | 'dark'

  // Animation
  animate?: boolean

  // Props from Section Renderer
  siteId?: string
  siteType?: string
}

export function HeroSection({
  title,
  subtitle,
  cta_text,
  cta_link,
  secondary_cta_text,
  secondary_cta_link,
  background_image,
  background_gradient,
  background_overlay = true,
  overlay_opacity = 0.4,
  text_alignment = 'center',
  height = 'large',
  text_color = 'light',
  animate = true,
}: HeroSectionProps) {
  // Height classes
  const heightClasses = {
    small: 'h-[400px]',
    medium: 'h-[600px]',
    large: 'h-[700px]',
    full: 'h-screen',
  }

  // Text alignment classes
  const alignmentClasses = {
    left: 'text-left items-start',
    center: 'text-center items-center',
    right: 'text-right items-end',
  }

  // Text color classes
  const textColorClasses = {
    light: 'text-white',
    dark: 'text-gray-900',
  }

  // Background style
  const backgroundStyle: React.CSSProperties = background_image
    ? {
        backgroundImage: `url(${background_image})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
      }
    : background_gradient
    ? { background: background_gradient }
    : { background: 'linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%)' }

  return (
    <section
      className={cn(
        'relative flex items-center justify-center overflow-hidden',
        heightClasses[height]
      )}
      style={backgroundStyle}
    >
      {/* Overlay */}
      {background_overlay && (
        <div
          className="absolute inset-0 bg-black"
          style={{ opacity: overlay_opacity }}
        />
      )}

      {/* Content */}
      <div
        className={cn(
          'relative z-10 container mx-auto px-4 flex flex-col gap-6',
          alignmentClasses[text_alignment]
        )}
      >
        {/* Title */}
        <h1
          className={cn(
            'text-4xl md:text-5xl lg:text-6xl font-bold max-w-4xl',
            textColorClasses[text_color],
            animate && 'animate-fade-in-up'
          )}
        >
          {title}
        </h1>

        {/* Subtitle */}
        {subtitle && (
          <p
            className={cn(
              'text-lg md:text-xl lg:text-2xl max-w-2xl',
              text_color === 'light' ? 'text-gray-200' : 'text-gray-600',
              animate && 'animate-fade-in-up animation-delay-200'
            )}
          >
            {subtitle}
          </p>
        )}

        {/* CTAs */}
        {(cta_text || secondary_cta_text) && (
          <div
            className={cn(
              'flex flex-wrap gap-4',
              text_alignment === 'center' && 'justify-center',
              text_alignment === 'right' && 'justify-end',
              animate && 'animate-fade-in-up animation-delay-400'
            )}
          >
            {/* Primary CTA */}
            {cta_text && cta_link && (
              <Link
                href={cta_link}
                className="bg-primary hover:bg-primary-hover text-white px-8 py-4 rounded-lg font-semibold text-lg transition-all duration-300 transform hover:scale-105 shadow-lg"
              >
                {cta_text}
              </Link>
            )}

            {/* Secondary CTA */}
            {secondary_cta_text && secondary_cta_link && (
              <Link
                href={secondary_cta_link}
                className={cn(
                  'px-8 py-4 rounded-lg font-semibold text-lg transition-all duration-300 border-2',
                  text_color === 'light'
                    ? 'border-white text-white hover:bg-white hover:text-gray-900'
                    : 'border-gray-900 text-gray-900 hover:bg-gray-900 hover:text-white'
                )}
              >
                {secondary_cta_text}
              </Link>
            )}
          </div>
        )}
      </div>

      {/* Decorative elements */}
      <div className="absolute bottom-0 left-0 right-0">
        <svg
          viewBox="0 0 1440 120"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="w-full h-auto"
        >
          <path
            d="M0 120L60 105C120 90 240 60 360 45C480 30 600 30 720 37.5C840 45 960 60 1080 67.5C1200 75 1320 75 1380 75L1440 75V120H1380C1320 120 1200 120 1080 120C960 120 840 120 720 120C600 120 480 120 360 120C240 120 120 120 60 120H0Z"
            fill="currentColor"
            className="text-white"
          />
        </svg>
      </div>
    </section>
  )
}

/**
 * Hero Section Variants
 * Pre-configured hero sections for common use cases
 */

export function SimpleHero({ title, subtitle, cta_text, cta_link }: Partial<HeroSectionProps>) {
  return (
    <HeroSection
      title={title || 'Welcome'}
      subtitle={subtitle}
      cta_text={cta_text}
      cta_link={cta_link}
      height="medium"
      text_alignment="center"
    />
  )
}

export function FullScreenHero(props: Partial<HeroSectionProps>) {
  return (
    <HeroSection
      {...props}
      height="full"
      background_overlay={true}
      overlay_opacity={0.5}
    />
  )
}

export function MinimalHero({ title, subtitle }: Partial<HeroSectionProps>) {
  return (
    <HeroSection
      title={title || 'Welcome'}
      subtitle={subtitle}
      height="small"
      text_alignment="center"
      text_color="dark"
      background_overlay={false}
    />
  )
}
