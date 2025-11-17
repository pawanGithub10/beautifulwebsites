/**
 * Theme Provider Component
 *
 * Dynamically applies site-specific theming using CSS variables.
 * Each site can have its own:
 * - Primary and secondary colors
 * - Font family
 * - Spacing and border radius
 * - Custom CSS overrides
 *
 * The theme is injected as CSS variables that Tailwind CSS can use.
 */

'use client'

import React from 'react'

interface SiteConfig {
  site_id: string
  slug: string
  site_type: string
  primary_color?: string
  secondary_color?: string
  font_family?: string
  logo_url?: string
  config?: Record<string, any>
}

interface ThemeProviderProps {
  siteConfig: SiteConfig
  children: React.ReactNode
}

/**
 * Convert hex color to RGB values (for Tailwind opacity modifiers)
 */
function hexToRgb(hex: string): string {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
  if (!result) return '0, 0, 0'

  const r = parseInt(result[1], 16)
  const g = parseInt(result[2], 16)
  const b = parseInt(result[3], 16)

  return `${r}, ${g}, ${b}`
}

/**
 * Darken a hex color by a percentage
 */
function darkenColor(hex: string, percent: number): string {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
  if (!result) return hex

  const r = Math.max(0, parseInt(result[1], 16) - Math.round(255 * (percent / 100)))
  const g = Math.max(0, parseInt(result[2], 16) - Math.round(255 * (percent / 100)))
  const b = Math.max(0, parseInt(result[3], 16) - Math.round(255 * (percent / 100)))

  return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`
}

/**
 * Lighten a hex color by a percentage
 */
function lightenColor(hex: string, percent: number): string {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
  if (!result) return hex

  const r = Math.min(255, parseInt(result[1], 16) + Math.round(255 * (percent / 100)))
  const g = Math.min(255, parseInt(result[2], 16) + Math.round(255 * (percent / 100)))
  const b = Math.min(255, parseInt(result[3], 16) + Math.round(255 * (percent / 100)))

  return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`
}

/**
 * Generate CSS variables from site config
 */
function generateThemeCSS(siteConfig: SiteConfig): string {
  const {
    primary_color = '#3b82f6',
    secondary_color = '#10b981',
    font_family = 'Inter, system-ui, sans-serif',
    config = {},
  } = siteConfig

  // Generate color variants
  const primaryRgb = hexToRgb(primary_color)
  const secondaryRgb = hexToRgb(secondary_color)
  const primaryHover = darkenColor(primary_color, 10)
  const primaryLight = lightenColor(primary_color, 40)
  const secondaryHover = darkenColor(secondary_color, 10)

  // Custom spacing and radius (if configured)
  const borderRadius = config.border_radius || '0.5rem'
  const spacing = config.spacing_unit || '1rem'

  return `
    :root {
      /* Brand Colors */
      --color-primary: ${primary_color};
      --color-primary-rgb: ${primaryRgb};
      --color-primary-hover: ${primaryHover};
      --color-primary-light: ${primaryLight};

      --color-secondary: ${secondary_color};
      --color-secondary-rgb: ${secondaryRgb};
      --color-secondary-hover: ${secondaryHover};

      /* Typography */
      --font-family: ${font_family};
      --font-family-heading: ${config.heading_font_family || font_family};

      /* Spacing */
      --spacing-unit: ${spacing};
      --border-radius: ${borderRadius};
      --border-radius-lg: calc(${borderRadius} * 1.5);
      --border-radius-sm: calc(${borderRadius} * 0.5);

      /* Shadows */
      --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
      --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
      --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);

      /* Theme-specific overrides */
      ${config.custom_css_variables || ''}
    }

    /* Apply font family */
    body {
      font-family: var(--font-family);
    }

    h1, h2, h3, h4, h5, h6 {
      font-family: var(--font-family-heading);
    }

    /* Tailwind utility classes using CSS variables */
    .bg-primary {
      background-color: var(--color-primary);
    }

    .bg-primary-hover:hover {
      background-color: var(--color-primary-hover);
    }

    .text-primary {
      color: var(--color-primary);
    }

    .border-primary {
      border-color: var(--color-primary);
    }

    .bg-secondary {
      background-color: var(--color-secondary);
    }

    .text-secondary {
      color: var(--color-secondary);
    }

    /* Animation utilities */
    @keyframes fade-in-up {
      from {
        opacity: 0;
        transform: translateY(20px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    .animate-fade-in-up {
      animation: fade-in-up 0.6s ease-out;
    }

    .animation-delay-200 {
      animation-delay: 0.2s;
    }

    .animation-delay-400 {
      animation-delay: 0.4s;
    }

    .animation-delay-600 {
      animation-delay: 0.6s;
    }
  `
}

/**
 * Theme Provider Component
 */
export function ThemeProvider({ siteConfig, children }: ThemeProviderProps) {
  const themeCSS = generateThemeCSS(siteConfig)

  return (
    <>
      {/* Inject theme styles */}
      <style dangerouslySetInnerHTML={{ __html: themeCSS }} />

      {/* Load custom fonts if specified */}
      {siteConfig.font_family && siteConfig.font_family !== 'Inter' && (
        <link
          rel="stylesheet"
          href={`https://fonts.googleapis.com/css2?family=${siteConfig.font_family.split(',')[0].trim().replace(' ', '+')}:wght@400;500;600;700&display=swap`}
        />
      )}

      {/* Render children with theme context */}
      <div className="site-theme" data-site-id={siteConfig.site_id} data-site-type={siteConfig.site_type}>
        {children}
      </div>
    </>
  )
}

/**
 * Hook to access site config (for components that need it)
 */
export function useSiteConfig(): SiteConfig | null {
  // In a real implementation, this would use React Context
  // For now, we'll read from data attributes
  if (typeof window === 'undefined') return null

  const themeElement = document.querySelector('.site-theme')
  if (!themeElement) return null

  return {
    site_id: themeElement.getAttribute('data-site-id') || '',
    slug: '',
    site_type: themeElement.getAttribute('data-site-type') || '',
  }
}

/**
 * Pre-defined theme presets (for quick setup)
 */
export const THEME_PRESETS = {
  modern: {
    primary_color: '#3b82f6',
    secondary_color: '#10b981',
    font_family: 'Inter, sans-serif',
    config: {
      border_radius: '0.75rem',
      spacing_unit: '1rem',
    },
  },
  elegant: {
    primary_color: '#4f46e5',
    secondary_color: '#ec4899',
    font_family: 'Playfair Display, serif',
    config: {
      border_radius: '0.25rem',
      spacing_unit: '1.5rem',
      heading_font_family: 'Playfair Display, serif',
    },
  },
  bold: {
    primary_color: '#dc2626',
    secondary_color: '#f59e0b',
    font_family: 'Montserrat, sans-serif',
    config: {
      border_radius: '0rem',
      spacing_unit: '1rem',
    },
  },
  minimal: {
    primary_color: '#1f2937',
    secondary_color: '#6b7280',
    font_family: 'Helvetica Neue, sans-serif',
    config: {
      border_radius: '0.25rem',
      spacing_unit: '0.75rem',
    },
  },
  vibrant: {
    primary_color: '#8b5cf6',
    secondary_color: '#06b6d4',
    font_family: 'Poppins, sans-serif',
    config: {
      border_radius: '1rem',
      spacing_unit: '1.25rem',
    },
  },
}
