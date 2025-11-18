import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Cart, CartItem, Product, ProductVariant } from '@/types';
import { storefrontApi } from '@/lib/api';
import { getSessionId } from '@/lib/utils/helpers';

interface CartState {
  cart: Cart | null;
  isLoading: boolean;

  // Actions
  loadCart: (siteId: string, userId?: string) => Promise<void>;
  addItem: (siteId: string, product: Product, variant?: ProductVariant, quantity?: number) => Promise<void>;
  updateQuantity: (siteId: string, itemId: string, quantity: number) => Promise<void>;
  removeItem: (siteId: string, itemId: string) => Promise<void>;
  clearCart: (siteId: string) => Promise<void>;
  mergeGuestCart: (siteId: string, userId: string) => Promise<void>;
  getItemCount: () => number;
  getTotal: () => number;
}

export const useCartStore = create<CartState>()(
  persist(
    (set, get) => ({
      cart: null,
      isLoading: false,

      loadCart: async (siteId, userId) => {
        set({ isLoading: true });
        try {
          const state = get();
          let cart = state.cart;

          // If we have a cart ID, fetch it
          if (cart?.cart_id) {
            try {
              cart = await storefrontApi.getCart(siteId, cart.cart_id);
            } catch (error) {
              // Cart not found or expired, create new one
              cart = null;
            }
          }

          // Create new cart if we don't have one
          if (!cart) {
            const sessionId = userId ? undefined : getSessionId();
            cart = await storefrontApi.createCart(siteId, userId, sessionId);
          }

          set({ cart, isLoading: false });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      addItem: async (siteId, product, variant, quantity = 1) => {
        const state = get();
        if (!state.cart) {
          await state.loadCart(siteId);
        }

        const cart = state.cart;
        if (!cart) throw new Error('No cart available');

        set({ isLoading: true });
        try {
          await storefrontApi.addToCart(siteId, cart.cart_id, {
            product_id: product.product_id,
            variant_id: variant?.variant_id || null,
            quantity,
          });

          // Reload cart to get updated data
          const updatedCart = await storefrontApi.getCart(siteId, cart.cart_id);
          set({ cart: updatedCart, isLoading: false });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      updateQuantity: async (siteId, itemId, quantity) => {
        const state = get();
        const cart = state.cart;
        if (!cart) throw new Error('No cart available');

        set({ isLoading: true });
        try {
          await storefrontApi.updateCartItem(siteId, cart.cart_id, itemId, { quantity });

          // Reload cart to get updated data
          const updatedCart = await storefrontApi.getCart(siteId, cart.cart_id);
          set({ cart: updatedCart, isLoading: false });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      removeItem: async (siteId, itemId) => {
        const state = get();
        const cart = state.cart;
        if (!cart) throw new Error('No cart available');

        set({ isLoading: true });
        try {
          await storefrontApi.removeFromCart(siteId, cart.cart_id, itemId);

          // Reload cart to get updated data
          const updatedCart = await storefrontApi.getCart(siteId, cart.cart_id);
          set({ cart: updatedCart, isLoading: false });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      clearCart: async (siteId) => {
        const state = get();
        const cart = state.cart;
        if (!cart) return;

        set({ isLoading: true });
        try {
          await storefrontApi.clearCart(siteId, cart.cart_id);

          // Reload cart to get updated data
          const updatedCart = await storefrontApi.getCart(siteId, cart.cart_id);
          set({ cart: updatedCart, isLoading: false });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      mergeGuestCart: async (siteId, userId) => {
        const state = get();
        const cart = state.cart;
        if (!cart || !cart.session_id) return;

        set({ isLoading: true });
        try {
          const mergedCart = await storefrontApi.mergeCarts(siteId, cart.session_id, userId);
          set({ cart: mergedCart, isLoading: false });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      getItemCount: () => {
        const cart = get().cart;
        if (!cart || !cart.items) return 0;
        return cart.items.reduce((total, item) => total + item.quantity, 0);
      },

      getTotal: () => {
        const cart = get().cart;
        if (!cart) return 0;
        return parseFloat(cart.total || '0');
      },
    }),
    {
      name: 'cart-storage',
      partialize: (state) => ({
        cart: state.cart,
      }),
    }
  )
);
