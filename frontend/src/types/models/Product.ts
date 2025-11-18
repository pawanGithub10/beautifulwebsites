export interface Category {
  category_id: string;
  site_id: string;
  parent_id: string | null;
  name: string;
  slug: string;
  description: string | null;
  image_url: string | null;
  is_active: boolean;
  display_order: number;
  created_at: string;
  updated_at: string;
}

export interface Product {
  product_id: string;
  site_id: string;
  category_id: string;
  name: string;
  slug: string;
  description: string;
  short_description: string | null;
  sku: string;
  price: string;
  compare_at_price: string | null;
  cost_price: string | null;
  track_inventory: boolean;
  stock_quantity: number;
  low_stock_threshold: number | null;
  images: string[];
  is_active: boolean;
  is_featured: boolean;
  tags: string[];
  attributes: Record<string, any>;
  created_at: string;
  updated_at: string;
  category?: Category;
  variants?: ProductVariant[];
}

export interface ProductVariant {
  variant_id: string;
  product_id: string;
  site_id: string;
  name: string;
  sku: string;
  price: string | null;
  compare_at_price: string | null;
  stock_quantity: number;
  low_stock_threshold: number | null;
  options: Record<string, any>;
  image_url: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProductFilters {
  category_id?: string;
  search?: string;
  tags?: string[];
  min_price?: number;
  max_price?: number;
  is_featured?: boolean;
  is_active?: boolean;
  page?: number;
  page_size?: number;
}

export interface ProductList {
  items: Product[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}
