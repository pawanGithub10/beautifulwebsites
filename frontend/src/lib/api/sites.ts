import { siteServiceClient } from './client';
import type { Site, Template, SiteSection } from '@/types';

export const siteApi = {
  // Get site by slug
  getSiteBySlug: async (slug: string): Promise<Site> => {
    const response = await siteServiceClient.get(`/api/v1/sites/slug/${slug}`);
    return response.data;
  },

  // Get site by ID
  getSiteById: async (siteId: string): Promise<Site> => {
    const response = await siteServiceClient.get(`/api/v1/sites/${siteId}`);
    return response.data;
  },

  // List sites for an organization
  listSites: async (orgId: string): Promise<Site[]> => {
    const response = await siteServiceClient.get(`/api/v1/sites`, {
      params: { org_id: orgId },
    });
    return response.data;
  },

  // Create a new site
  createSite: async (siteData: Partial<Site>): Promise<Site> => {
    const response = await siteServiceClient.post(`/api/v1/sites`, siteData);
    return response.data;
  },

  // Update site
  updateSite: async (siteId: string, siteData: Partial<Site>): Promise<Site> => {
    const response = await siteServiceClient.put(`/api/v1/sites/${siteId}`, siteData);
    return response.data;
  },

  // Delete site
  deleteSite: async (siteId: string): Promise<void> => {
    await siteServiceClient.delete(`/api/v1/sites/${siteId}`);
  },

  // Publish site
  publishSite: async (siteId: string): Promise<Site> => {
    const response = await siteServiceClient.post(`/api/v1/sites/${siteId}/publish`);
    return response.data;
  },

  // Get all templates
  getTemplates: async (): Promise<Template[]> => {
    const response = await siteServiceClient.get(`/api/v1/templates`);
    return response.data;
  },

  // Get template by ID
  getTemplate: async (templateId: string): Promise<Template> => {
    const response = await siteServiceClient.get(`/api/v1/templates/${templateId}`);
    return response.data;
  },

  // Get templates by site type
  getTemplatesBySiteType: async (siteType: string): Promise<Template[]> => {
    const response = await siteServiceClient.get(`/api/v1/templates/type/${siteType}`);
    return response.data;
  },

  // Get site sections
  getSiteSections: async (siteId: string): Promise<SiteSection[]> => {
    const response = await siteServiceClient.get(`/api/v1/sites/${siteId}/sections`);
    return response.data;
  },

  // Create site section
  createSiteSection: async (siteId: string, sectionData: Partial<SiteSection>): Promise<SiteSection> => {
    const response = await siteServiceClient.post(`/api/v1/sites/${siteId}/sections`, sectionData);
    return response.data;
  },

  // Update site section
  updateSiteSection: async (
    siteId: string,
    sectionId: string,
    sectionData: Partial<SiteSection>
  ): Promise<SiteSection> => {
    const response = await siteServiceClient.put(
      `/api/v1/sites/${siteId}/sections/${sectionId}`,
      sectionData
    );
    return response.data;
  },

  // Delete site section
  deleteSiteSection: async (siteId: string, sectionId: string): Promise<void> => {
    await siteServiceClient.delete(`/api/v1/sites/${siteId}/sections/${sectionId}`);
  },

  // Reorder sections
  reorderSections: async (siteId: string, sectionOrders: { section_id: string; order: number }[]): Promise<void> => {
    await siteServiceClient.post(`/api/v1/sites/${siteId}/sections/reorder`, {
      sections: sectionOrders,
    });
  },
};
