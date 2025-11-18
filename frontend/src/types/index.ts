// Models
export * from './models/Site';
export * from './models/Product';
export * from './models/Cart';
export * from './models/Order';
export * from './models/Booking';
export * from './models/User';

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface ApiError {
  detail: string;
  status_code: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}
