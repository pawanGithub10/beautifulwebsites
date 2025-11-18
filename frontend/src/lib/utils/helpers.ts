import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

// Classname utility (used by shadcn/ui)
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Generate session ID for guest users
export const generateSessionId = (): string => {
  return `sess_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

// Get or create session ID
export const getSessionId = (): string => {
  if (typeof window === 'undefined') return '';

  let sessionId = localStorage.getItem('session_id');
  if (!sessionId) {
    sessionId = generateSessionId();
    localStorage.setItem('session_id', sessionId);
  }
  return sessionId;
};

// Sleep utility
export const sleep = (ms: number): Promise<void> => {
  return new Promise((resolve) => setTimeout(resolve, ms));
};

// Debounce function
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;

  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null;
      func(...args);
    };

    if (timeout) {
      clearTimeout(timeout);
    }
    timeout = setTimeout(later, wait);
  };
}

// Group array by key
export const groupBy = <T>(array: T[], key: keyof T): Record<string, T[]> => {
  return array.reduce((result, item) => {
    const groupKey = String(item[key]);
    if (!result[groupKey]) {
      result[groupKey] = [];
    }
    result[groupKey].push(item);
    return result;
  }, {} as Record<string, T[]>);
};

// Calculate cart total
export const calculateCartTotal = (items: { quantity: number; unit_price: string }[]): number => {
  return items.reduce((total, item) => {
    return total + item.quantity * parseFloat(item.unit_price);
  }, 0);
};

// Check if item is in stock
export const isInStock = (quantity: number, lowStockThreshold: number = 0): boolean => {
  return quantity > 0;
};

// Check if item is low stock
export const isLowStock = (quantity: number, lowStockThreshold: number = 5): boolean => {
  return quantity > 0 && quantity <= lowStockThreshold;
};

// Get stock status
export const getStockStatus = (
  quantity: number,
  lowStockThreshold: number = 5
): 'in_stock' | 'low_stock' | 'out_of_stock' => {
  if (quantity === 0) return 'out_of_stock';
  if (quantity <= lowStockThreshold) return 'low_stock';
  return 'in_stock';
};

// Get stock status label
export const getStockStatusLabel = (status: string): string => {
  const labels: Record<string, string> = {
    in_stock: 'In Stock',
    low_stock: 'Low Stock',
    out_of_stock: 'Out of Stock',
  };
  return labels[status] || status;
};

// Get stock status color
export const getStockStatusColor = (status: string): string => {
  const colors: Record<string, string> = {
    in_stock: 'text-green-600',
    low_stock: 'text-yellow-600',
    out_of_stock: 'text-red-600',
  };
  return colors[status] || 'text-gray-600';
};

// Parse query params
export const parseQueryParams = (searchParams: URLSearchParams): Record<string, any> => {
  const params: Record<string, any> = {};

  searchParams.forEach((value, key) => {
    // Handle arrays (e.g., tags[]=value1&tags[]=value2)
    if (key.endsWith('[]')) {
      const arrayKey = key.slice(0, -2);
      if (!params[arrayKey]) {
        params[arrayKey] = [];
      }
      params[arrayKey].push(value);
    } else {
      params[key] = value;
    }
  });

  return params;
};

// Build query string
export const buildQueryString = (params: Record<string, any>): string => {
  const searchParams = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') return;

    if (Array.isArray(value)) {
      value.forEach((item) => searchParams.append(`${key}[]`, String(item)));
    } else {
      searchParams.append(key, String(value));
    }
  });

  const queryString = searchParams.toString();
  return queryString ? `?${queryString}` : '';
};

// Get image URL or placeholder
export const getImageUrl = (url: string | null | undefined, placeholder: string = '/images/placeholder.png'): string => {
  return url || placeholder;
};

// Calculate discount percentage
export const calculateDiscountPercentage = (originalPrice: number, salePrice: number): number => {
  if (originalPrice <= 0) return 0;
  return Math.round(((originalPrice - salePrice) / originalPrice) * 100);
};
