import { create } from 'zustand';
import type { Site } from '@/types';

interface SiteState {
  site: Site | null;
  isLoading: boolean;

  // Actions
  setSite: (site: Site | null) => void;
  setLoading: (isLoading: boolean) => void;
}

export const useSiteStore = create<SiteState>()((set) => ({
  site: null,
  isLoading: false,

  setSite: (site) => set({ site }),
  setLoading: (isLoading) => set({ isLoading }),
}));
