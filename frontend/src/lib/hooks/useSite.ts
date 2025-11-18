import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { siteApi } from '@/lib/api';
import { useSiteStore } from '@/lib/store/siteStore';
import type { Site, Template, SiteSection } from '@/types';

// Get site by slug
export function useSite(slug: string) {
  const { setSite, setLoading } = useSiteStore();

  return useQuery({
    queryKey: ['site', slug],
    queryFn: async () => {
      setLoading(true);
      try {
        const site = await siteApi.getSiteBySlug(slug);
        setSite(site);
        return site;
      } finally {
        setLoading(false);
      }
    },
    enabled: !!slug,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

// Get site by ID
export function useSiteById(siteId: string) {
  return useQuery({
    queryKey: ['site', siteId],
    queryFn: () => siteApi.getSiteById(siteId),
    enabled: !!siteId,
  });
}

// List sites for organization
export function useSites(orgId: string) {
  return useQuery({
    queryKey: ['sites', orgId],
    queryFn: () => siteApi.listSites(orgId),
    enabled: !!orgId,
  });
}

// Get templates
export function useTemplates(siteType?: string) {
  return useQuery({
    queryKey: ['templates', siteType],
    queryFn: () => {
      if (siteType) {
        return siteApi.getTemplatesBySiteType(siteType);
      }
      return siteApi.getTemplates();
    },
  });
}

// Get template by ID
export function useTemplate(templateId: string) {
  return useQuery({
    queryKey: ['template', templateId],
    queryFn: () => siteApi.getTemplate(templateId),
    enabled: !!templateId,
  });
}

// Get site sections
export function useSiteSections(siteId: string) {
  return useQuery({
    queryKey: ['site-sections', siteId],
    queryFn: () => siteApi.getSiteSections(siteId),
    enabled: !!siteId,
  });
}

// Create site
export function useCreateSite() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (siteData: Partial<Site>) => siteApi.createSite(siteData),
    onSuccess: (_, variables) => {
      if (variables.org_id) {
        queryClient.invalidateQueries({ queryKey: ['sites', variables.org_id] });
      }
    },
  });
}

// Update site
export function useUpdateSite() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ siteId, data }: { siteId: string; data: Partial<Site> }) =>
      siteApi.updateSite(siteId, data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['site', data.site_id] });
      queryClient.invalidateQueries({ queryKey: ['site', data.slug] });
    },
  });
}

// Publish site
export function usePublishSite() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (siteId: string) => siteApi.publishSite(siteId),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['site', data.site_id] });
      queryClient.invalidateQueries({ queryKey: ['site', data.slug] });
    },
  });
}

// Create site section
export function useCreateSiteSection() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ siteId, data }: { siteId: string; data: Partial<SiteSection> }) =>
      siteApi.createSiteSection(siteId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['site-sections', variables.siteId] });
    },
  });
}

// Update site section
export function useUpdateSiteSection() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      siteId,
      sectionId,
      data,
    }: {
      siteId: string;
      sectionId: string;
      data: Partial<SiteSection>;
    }) => siteApi.updateSiteSection(siteId, sectionId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['site-sections', variables.siteId] });
    },
  });
}

// Delete site section
export function useDeleteSiteSection() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ siteId, sectionId }: { siteId: string; sectionId: string }) =>
      siteApi.deleteSiteSection(siteId, sectionId),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['site-sections', variables.siteId] });
    },
  });
}
