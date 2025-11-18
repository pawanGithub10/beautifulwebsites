import { storefrontServiceClient } from './client';
import type {
  Category,
  Product,
  ProductVariant,
  ProductFilters,
  ProductList,
  Cart,
  CartItem,
  CartItemAdd,
  CartItemUpdate,
  Order,
  OrderCreate,
  OrderFilters,
  OrderList,
} from '@/types';

export const storefrontApi = {
  // ===== CATEGORIES =====
  getCategories: async (siteId: string): Promise<Category[]> => {
    const response = await storefrontServiceClient.get(`/api/v1/${siteId}/categories`);
    return response.data;
  },

  getCategory: async (siteId: string, categoryId: string): Promise<Category> => {
    const response = await storefrontServiceClient.get(`/api/v1/${siteId}/categories/${categoryId}`);
    return response.data;
  },

  // ===== PRODUCTS =====
  getProducts: async (siteId: string, filters?: ProductFilters): Promise<ProductList> => {
    const response = await storefrontServiceClient.get(`/api/v1/${siteId}/products`, {
      params: filters,
    });
    return response.data;
  },

  getProduct: async (siteId: string, productId: string): Promise<Product> => {
    const response = await storefrontServiceClient.get(`/api/v1/${siteId}/products/${productId}`);
    return response.data;
  },

  getProductBySlug: async (siteId: string, slug: string): Promise<Product> => {
    const response = await storefrontServiceClient.get(`/api/v1/${siteId}/products/slug/${slug}`);
    return response.data;
  },

  getFeaturedProducts: async (siteId: string, limit: number = 8): Promise<Product[]> => {
    const response = await storefrontServiceClient.get(`/api/v1/${siteId}/products/featured`, {
      params: { limit },
    });
    return response.data;
  },

  // ===== PRODUCT VARIANTS =====
  getProductVariants: async (siteId: string, productId: string): Promise<ProductVariant[]> => {
    const response = await storefrontServiceClient.get(
      `/api/v1/${siteId}/products/${productId}/variants`
    );
    return response.data;
  },

  // ===== CART =====
  getCart: async (siteId: string, cartId: string): Promise<Cart> => {
    const response = await storefrontServiceClient.get(`/api/v1/${siteId}/cart/${cartId}`);
    return response.data;
  },

  createCart: async (siteId: string, userId?: string, sessionId?: string): Promise<Cart> => {
    const response = await storefrontServiceClient.post(`/api/v1/${siteId}/cart`, {
      user_id: userId,
      session_id: sessionId,
    });
    return response.data;
  },

  addToCart: async (siteId: string, cartId: string, item: CartItemAdd): Promise<CartItem> => {
    const response = await storefrontServiceClient.post(
      `/api/v1/${siteId}/cart/${cartId}/items`,
      item
    );
    return response.data;
  },

  updateCartItem: async (
    siteId: string,
    cartId: string,
    itemId: string,
    update: CartItemUpdate
  ): Promise<CartItem> => {
    const response = await storefrontServiceClient.put(
      `/api/v1/${siteId}/cart/${cartId}/items/${itemId}`,
      update
    );
    return response.data;
  },

  removeFromCart: async (siteId: string, cartId: string, itemId: string): Promise<void> => {
    await storefrontServiceClient.delete(`/api/v1/${siteId}/cart/${cartId}/items/${itemId}`);
  },

  clearCart: async (siteId: string, cartId: string): Promise<void> => {
    await storefrontServiceClient.delete(`/api/v1/${siteId}/cart/${cartId}/items`);
  },

  mergeCarts: async (siteId: string, sessionId: string, userId: string): Promise<Cart> => {
    const response = await storefrontServiceClient.post(`/api/v1/${siteId}/cart/merge`, {
      session_id: sessionId,
      user_id: userId,
    });
    return response.data;
  },

  // ===== ORDERS =====
  getOrders: async (siteId: string, filters?: OrderFilters): Promise<OrderList> => {
    const response = await storefrontServiceClient.get(`/api/v1/${siteId}/orders`, {
      params: filters,
    });
    return response.data;
  },

  getOrder: async (siteId: string, orderId: string): Promise<Order> => {
    const response = await storefrontServiceClient.get(`/api/v1/${siteId}/orders/${orderId}`);
    return response.data;
  },

  getOrderByNumber: async (siteId: string, orderNumber: string): Promise<Order> => {
    const response = await storefrontServiceClient.get(
      `/api/v1/${siteId}/orders/number/${orderNumber}`
    );
    return response.data;
  },

  createOrder: async (siteId: string, orderData: OrderCreate): Promise<Order> => {
    const response = await storefrontServiceClient.post(`/api/v1/${siteId}/orders`, orderData);
    return response.data;
  },

  updateOrderStatus: async (siteId: string, orderId: string, status: string): Promise<Order> => {
    const response = await storefrontServiceClient.put(`/api/v1/${siteId}/orders/${orderId}/status`, {
      order_status: status,
    });
    return response.data;
  },

  cancelOrder: async (siteId: string, orderId: string, reason: string): Promise<Order> => {
    const response = await storefrontServiceClient.post(`/api/v1/${siteId}/orders/${orderId}/cancel`, {
      reason,
    });
    return response.data;
  },

  getOrderHistory: async (siteId: string, orderId: string): Promise<any[]> => {
    const response = await storefrontServiceClient.get(
      `/api/v1/${siteId}/orders/${orderId}/history`
    );
    return response.data;
  },
};
