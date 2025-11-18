export interface Order {
  order_id: string;
  site_id: string;
  user_id: string | null;
  cart_id: string;
  order_number: string;
  order_status:
    | 'placed'
    | 'confirmed'
    | 'preparing'
    | 'dispatched'
    | 'delivered'
    | 'cancelled'
    | 'refunded';
  payment_status: 'pending' | 'paid' | 'failed' | 'refunded';
  payment_method: string;
  items: OrderItem[];
  subtotal: string;
  tax_amount: string;
  shipping_amount: string;
  discount_amount: string;
  total_amount: string;
  customer_details: CustomerDetails;
  shipping_address: Address;
  billing_address: Address;
  notes: string | null;
  created_at: string;
  updated_at: string;
  history?: OrderHistory[];
}

export interface OrderItem {
  item_id: string;
  order_id: string;
  product_id: string;
  variant_id: string | null;
  quantity: number;
  unit_price: string;
  total_price: string;
  product_snapshot: ProductSnapshot;
  created_at: string;
}

export interface ProductSnapshot {
  name: string;
  sku: string;
  image_url: string | null;
  attributes: Record<string, any>;
}

export interface CustomerDetails {
  name: string;
  email: string;
  phone: string;
}

export interface Address {
  line1: string;
  line2?: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
}

export interface OrderHistory {
  history_id: string;
  order_id: string;
  changed_by: string | null;
  change_type: string;
  old_status: string | null;
  new_status: string;
  notes: string | null;
  created_at: string;
}

export interface OrderCreate {
  cart_id: string;
  customer_details: CustomerDetails;
  shipping_address: Address;
  billing_address: Address;
  payment_method: string;
  notes?: string;
}

export interface OrderFilters {
  user_id?: string;
  status?: string;
  payment_status?: string;
  start_date?: string;
  end_date?: string;
  page?: number;
  page_size?: number;
}

export interface OrderList {
  items: Order[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}
