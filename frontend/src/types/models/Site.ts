export interface Site {
  site_id: string;
  org_id: string;
  slug: string;
  site_type: 'store' | 'booking' | 'tiffin' | 'coaching' | 'custom';
  status: 'draft' | 'published' | 'suspended';
  name: string;
  domain: string | null;
  branding: SiteBranding;
  config: SiteConfig;
  created_at: string;
  updated_at: string;
}

export interface SiteBranding {
  logo_url?: string;
  favicon_url?: string;
  primary_color?: string;
  secondary_color?: string;
  accent_color?: string;
  font_family?: string;
  custom_css?: string;
}

export interface SiteConfig {
  features?: string[];
  integrations?: Record<string, any>;
  seo?: {
    title?: string;
    description?: string;
    keywords?: string[];
    og_image?: string;
  };
  contact?: {
    email?: string;
    phone?: string;
    address?: string;
  };
}

export interface Template {
  template_id: string;
  name: string;
  site_type: string;
  thumbnail_url: string;
  description: string;
  default_sections: TemplateSection[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface TemplateSection {
  section_id: string;
  template_id: string;
  name: string;
  section_type: string;
  order: number;
  default_content: Record<string, any>;
  is_required: boolean;
}

export interface SiteSection {
  section_id: string;
  site_id: string;
  name: string;
  section_type: string;
  order: number;
  content: Record<string, any>;
  is_visible: boolean;
  created_at: string;
  updated_at: string;
}
