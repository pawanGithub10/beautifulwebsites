import { bookingServiceClient } from './client';
import type {
  ServiceCategory,
  Service,
  Provider,
  Booking,
  BookingCreate,
  BookingFilters,
  BookingList,
  AvailabilityQuery,
  AvailabilityResponse,
  RecurringSchedule,
  ProviderSchedule,
  BlockedSlot,
} from '@/types';

export const bookingApi = {
  // ===== SERVICE CATEGORIES =====
  getServiceCategories: async (siteId: string): Promise<ServiceCategory[]> => {
    const response = await bookingServiceClient.get(`/api/v1/${siteId}/categories`);
    return response.data;
  },

  getServiceCategory: async (siteId: string, categoryId: string): Promise<ServiceCategory> => {
    const response = await bookingServiceClient.get(`/api/v1/${siteId}/categories/${categoryId}`);
    return response.data;
  },

  // ===== SERVICES =====
  getServices: async (siteId: string, categoryId?: string): Promise<Service[]> => {
    const response = await bookingServiceClient.get(`/api/v1/${siteId}/services`, {
      params: categoryId ? { category_id: categoryId } : {},
    });
    return response.data;
  },

  getService: async (siteId: string, serviceId: string): Promise<Service> => {
    const response = await bookingServiceClient.get(`/api/v1/${siteId}/services/${serviceId}`);
    return response.data;
  },

  // ===== PROVIDERS =====
  getProviders: async (siteId: string, serviceId?: string): Promise<Provider[]> => {
    const response = await bookingServiceClient.get(`/api/v1/${siteId}/providers`, {
      params: serviceId ? { service_id: serviceId } : {},
    });
    return response.data;
  },

  getProvider: async (siteId: string, providerId: string): Promise<Provider> => {
    const response = await bookingServiceClient.get(`/api/v1/${siteId}/providers/${providerId}`);
    return response.data;
  },

  // ===== AVAILABILITY =====
  checkAvailability: async (
    siteId: string,
    query: AvailabilityQuery
  ): Promise<AvailabilityResponse> => {
    const response = await bookingServiceClient.post(`/api/v1/${siteId}/availability`, query);
    return response.data;
  },

  getProviderSchedule: async (
    siteId: string,
    providerId: string,
    startDate: string,
    endDate: string
  ): Promise<ProviderSchedule[]> => {
    const response = await bookingServiceClient.get(
      `/api/v1/${siteId}/providers/${providerId}/schedule`,
      {
        params: { start_date: startDate, end_date: endDate },
      }
    );
    return response.data;
  },

  getRecurringSchedule: async (siteId: string, providerId: string): Promise<RecurringSchedule[]> => {
    const response = await bookingServiceClient.get(
      `/api/v1/${siteId}/providers/${providerId}/recurring-schedules`
    );
    return response.data;
  },

  // ===== BOOKINGS =====
  getBookings: async (siteId: string, filters?: BookingFilters): Promise<BookingList> => {
    const response = await bookingServiceClient.get(`/api/v1/${siteId}/bookings`, {
      params: filters,
    });
    return response.data;
  },

  getBooking: async (siteId: string, bookingId: string): Promise<Booking> => {
    const response = await bookingServiceClient.get(`/api/v1/${siteId}/bookings/${bookingId}`);
    return response.data;
  },

  getBookingByNumber: async (siteId: string, bookingNumber: string): Promise<Booking> => {
    const response = await bookingServiceClient.get(
      `/api/v1/${siteId}/bookings/number/${bookingNumber}`
    );
    return response.data;
  },

  createBooking: async (siteId: string, bookingData: BookingCreate): Promise<Booking> => {
    const response = await bookingServiceClient.post(`/api/v1/${siteId}/bookings`, bookingData);
    return response.data;
  },

  updateBookingStatus: async (siteId: string, bookingId: string, status: string, notes?: string): Promise<Booking> => {
    const response = await bookingServiceClient.put(
      `/api/v1/${siteId}/bookings/${bookingId}/status`,
      {
        booking_status: status,
        notes,
      }
    );
    return response.data;
  },

  cancelBooking: async (siteId: string, bookingId: string, reason: string): Promise<Booking> => {
    const response = await bookingServiceClient.post(
      `/api/v1/${siteId}/bookings/${bookingId}/cancel`,
      {
        reason,
      }
    );
    return response.data;
  },

  rescheduleBooking: async (
    siteId: string,
    bookingId: string,
    newDate: string,
    newTime: string
  ): Promise<Booking> => {
    const response = await bookingServiceClient.post(
      `/api/v1/${siteId}/bookings/${bookingId}/reschedule`,
      {
        new_booking_date: newDate,
        new_start_time: newTime,
      }
    );
    return response.data;
  },

  getBookingHistory: async (siteId: string, bookingId: string): Promise<any[]> => {
    const response = await bookingServiceClient.get(
      `/api/v1/${siteId}/bookings/${bookingId}/history`
    );
    return response.data;
  },
};
