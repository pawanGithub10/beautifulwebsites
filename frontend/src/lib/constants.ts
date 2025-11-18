// App constants

// Site types
export const SITE_TYPES = {
  STORE: 'store',
  BOOKING: 'booking',
  TIFFIN: 'tiffin',
  COACHING: 'coaching',
  CUSTOM: 'custom',
} as const;

export const SITE_TYPE_LABELS = {
  [SITE_TYPES.STORE]: 'Online Store',
  [SITE_TYPES.BOOKING]: 'Booking Service',
  [SITE_TYPES.TIFFIN]: 'Tiffin Service',
  [SITE_TYPES.COACHING]: 'Coaching/Tutoring',
  [SITE_TYPES.CUSTOM]: 'Custom Website',
} as const;

// Order statuses
export const ORDER_STATUSES = {
  PLACED: 'placed',
  CONFIRMED: 'confirmed',
  PREPARING: 'preparing',
  DISPATCHED: 'dispatched',
  DELIVERED: 'delivered',
  CANCELLED: 'cancelled',
  REFUNDED: 'refunded',
} as const;

// Booking statuses
export const BOOKING_STATUSES = {
  CONFIRMED: 'confirmed',
  CANCELLED_BY_CUSTOMER: 'cancelled_by_customer',
  CANCELLED_BY_BUSINESS: 'cancelled_by_business',
  COMPLETED: 'completed',
  NO_SHOW: 'no_show',
} as const;

// Payment statuses
export const PAYMENT_STATUSES = {
  PENDING: 'pending',
  PAID: 'paid',
  FAILED: 'failed',
  REFUNDED: 'refunded',
} as const;

// Payment methods
export const PAYMENT_METHODS = [
  { value: 'cash', label: 'Cash on Delivery' },
  { value: 'upi', label: 'UPI' },
  { value: 'card', label: 'Credit/Debit Card' },
  { value: 'netbanking', label: 'Net Banking' },
  { value: 'wallet', label: 'Digital Wallet' },
] as const;

// Days of week
export const DAYS_OF_WEEK = [
  { value: 0, label: 'Monday', short: 'Mon' },
  { value: 1, label: 'Tuesday', short: 'Tue' },
  { value: 2, label: 'Wednesday', short: 'Wed' },
  { value: 3, label: 'Thursday', short: 'Thu' },
  { value: 4, label: 'Friday', short: 'Fri' },
  { value: 5, label: 'Saturday', short: 'Sat' },
  { value: 6, label: 'Sunday', short: 'Sun' },
] as const;

// Time slots (for booking)
export const TIME_SLOTS = Array.from({ length: 48 }, (_, i) => {
  const hour = Math.floor(i / 2);
  const minute = i % 2 === 0 ? '00' : '30';
  const time = `${hour.toString().padStart(2, '0')}:${minute}:00`;
  const displayHour = hour % 12 || 12;
  const ampm = hour < 12 ? 'AM' : 'PM';
  const display = `${displayHour}:${minute} ${ampm}`;
  return { value: time, label: display };
});

// Pagination defaults
export const PAGINATION = {
  DEFAULT_PAGE: 1,
  DEFAULT_PAGE_SIZE: 20,
  PAGE_SIZE_OPTIONS: [10, 20, 50, 100],
} as const;

// API errors
export const API_ERRORS = {
  UNAUTHORIZED: 'You are not authorized to perform this action',
  FORBIDDEN: 'Access forbidden',
  NOT_FOUND: 'Resource not found',
  SERVER_ERROR: 'An unexpected server error occurred',
  NETWORK_ERROR: 'Network error. Please check your connection',
} as const;

// Cart expiry (24 hours)
export const CART_EXPIRY_HOURS = 24;

// Indian states
export const INDIAN_STATES = [
  'Andhra Pradesh',
  'Arunachal Pradesh',
  'Assam',
  'Bihar',
  'Chhattisgarh',
  'Goa',
  'Gujarat',
  'Haryana',
  'Himachal Pradesh',
  'Jharkhand',
  'Karnataka',
  'Kerala',
  'Madhya Pradesh',
  'Maharashtra',
  'Manipur',
  'Meghalaya',
  'Mizoram',
  'Nagaland',
  'Odisha',
  'Punjab',
  'Rajasthan',
  'Sikkim',
  'Tamil Nadu',
  'Telangana',
  'Tripura',
  'Uttar Pradesh',
  'Uttarakhand',
  'West Bengal',
  'Andaman and Nicobar Islands',
  'Chandigarh',
  'Dadra and Nagar Haveli and Daman and Diu',
  'Delhi',
  'Jammu and Kashmir',
  'Ladakh',
  'Lakshadweep',
  'Puducherry',
] as const;
