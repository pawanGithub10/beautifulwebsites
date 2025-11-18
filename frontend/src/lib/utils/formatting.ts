import { format, parseISO, formatDistance } from 'date-fns';

// Currency formatting
export const formatCurrency = (amount: string | number, currency: string = 'INR'): string => {
  const numAmount = typeof amount === 'string' ? parseFloat(amount) : amount;

  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(numAmount);
};

// Date formatting
export const formatDate = (date: string | Date, formatStr: string = 'MMM dd, yyyy'): string => {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  return format(dateObj, formatStr);
};

export const formatDateTime = (date: string | Date): string => {
  return formatDate(date, 'MMM dd, yyyy hh:mm a');
};

export const formatTime = (time: string): string => {
  // Convert "HH:MM:SS" to "hh:mm AM/PM"
  const [hours, minutes] = time.split(':');
  const hour = parseInt(hours, 10);
  const ampm = hour >= 12 ? 'PM' : 'AM';
  const displayHour = hour % 12 || 12;
  return `${displayHour}:${minutes} ${ampm}`;
};

export const formatRelativeTime = (date: string | Date): string => {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  return formatDistance(dateObj, new Date(), { addSuffix: true });
};

// Number formatting
export const formatNumber = (num: number, decimals: number = 0): string => {
  return new Intl.NumberFormat('en-IN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(num);
};

// Phone formatting
export const formatPhone = (phone: string): string => {
  // Format Indian phone numbers: +91 XXXXX XXXXX
  const cleaned = phone.replace(/\D/g, '');
  if (cleaned.length === 10) {
    return `+91 ${cleaned.slice(0, 5)} ${cleaned.slice(5)}`;
  }
  return phone;
};

// Truncate text
export const truncate = (text: string, length: number = 100): string => {
  if (text.length <= length) return text;
  return text.slice(0, length) + '...';
};

// Status badge colors
export const getStatusColor = (status: string): string => {
  const statusColors: Record<string, string> = {
    // Order statuses
    placed: 'bg-blue-100 text-blue-800',
    confirmed: 'bg-green-100 text-green-800',
    preparing: 'bg-yellow-100 text-yellow-800',
    dispatched: 'bg-purple-100 text-purple-800',
    delivered: 'bg-green-100 text-green-800',
    cancelled: 'bg-red-100 text-red-800',
    refunded: 'bg-gray-100 text-gray-800',

    // Booking statuses
    'confirmed': 'bg-green-100 text-green-800',
    'cancelled_by_customer': 'bg-red-100 text-red-800',
    'cancelled_by_business': 'bg-red-100 text-red-800',
    'completed': 'bg-blue-100 text-blue-800',
    'no_show': 'bg-gray-100 text-gray-800',

    // Payment statuses
    pending: 'bg-yellow-100 text-yellow-800',
    paid: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',

    // Site statuses
    draft: 'bg-gray-100 text-gray-800',
    published: 'bg-green-100 text-green-800',
    suspended: 'bg-red-100 text-red-800',

    // Cart statuses
    active: 'bg-green-100 text-green-800',
    converted: 'bg-blue-100 text-blue-800',
    expired: 'bg-gray-100 text-gray-800',
  };

  return statusColors[status.toLowerCase()] || 'bg-gray-100 text-gray-800';
};

// Status labels
export const getStatusLabel = (status: string): string => {
  const labels: Record<string, string> = {
    cancelled_by_customer: 'Cancelled by Customer',
    cancelled_by_business: 'Cancelled by Business',
    no_show: 'No Show',
  };

  return labels[status] || status.charAt(0).toUpperCase() + status.slice(1);
};
