import { Product, ProductVariant } from './Product';

export interface Cart {
  cart_id: string;
  site_id: string;
  user_id: string | null;
  session_id: string | null;
  status: 'active' | 'converted' | 'expired';
  items: CartItem[];
  subtotal: string;
  total: string;
  expires_at: string;
  created_at: string;
  updated_at: string;
}

export interface CartItem {
  item_id: string;
  cart_id: string;
  product_id: string;
  variant_id: string | null;
  quantity: number;
  unit_price: string;
  total_price: string;
  created_at: string;
  updated_at: string;
  product?: Product;
  variant?: ProductVariant;
}

export interface CartItemAdd {
  product_id: string;
  variant_id?: string | null;
  quantity: number;
}

export interface CartItemUpdate {
  quantity: number;
}

export interface CartSummary {
  itemCount: number;
  subtotal: number;
  tax: number;
  shipping: number;
  total: number;
}
