export interface ServiceCategory {
  category_id: string;
  site_id: string;
  name: string;
  description: string | null;
  display_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Service {
  service_id: string;
  site_id: string;
  category_id: string;
  name: string;
  description: string;
  duration_minutes: number;
  price: string;
  buffer_time_minutes: number;
  is_active: boolean;
  requires_provider: boolean;
  max_capacity: number;
  image_url: string | null;
  created_at: string;
  updated_at: string;
  category?: ServiceCategory;
}

export interface Provider {
  provider_id: string;
  site_id: string;
  name: string;
  email: string;
  phone: string | null;
  bio: string | null;
  avatar_url: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface RecurringSchedule {
  schedule_id: string;
  site_id: string;
  provider_id: string;
  day_of_week: number; // 0 = Monday, 6 = Sunday
  start_time: string;
  end_time: string;
  created_at: string;
  updated_at: string;
}

export interface ProviderSchedule {
  schedule_id: string;
  site_id: string;
  provider_id: string;
  schedule_date: string;
  start_time: string;
  end_time: string;
  is_available: boolean;
  created_at: string;
  updated_at: string;
}

export interface BlockedSlot {
  blocked_id: string;
  site_id: string;
  provider_id: string | null;
  blocked_date: string;
  start_time: string;
  end_time: string;
  reason: string | null;
  created_at: string;
}

export interface Booking {
  booking_id: string;
  site_id: string;
  service_id: string;
  provider_id: string;
  user_id: string | null;
  booking_number: string;
  booking_status:
    | 'confirmed'
    | 'cancelled_by_customer'
    | 'cancelled_by_business'
    | 'completed'
    | 'no_show';
  booking_date: string;
  start_time: string;
  end_time: string;
  customer_name: string;
  customer_email: string;
  customer_phone: string;
  notes: string | null;
  price: string;
  service_snapshot: ServiceSnapshot;
  created_at: string;
  updated_at: string;
  service?: Service;
  provider?: Provider;
  history?: BookingHistory[];
}

export interface ServiceSnapshot {
  name: string;
  duration_minutes: number;
  description: string;
}

export interface BookingHistory {
  history_id: string;
  booking_id: string;
  changed_by: string | null;
  change_type: string;
  old_status: string | null;
  new_status: string;
  notes: string | null;
  created_at: string;
}

export interface TimeSlot {
  start_time: string;
  end_time: string;
  provider_id: string;
  provider_name: string;
  available: boolean;
}

export interface AvailabilityQuery {
  service_id: string;
  booking_date: string;
  provider_id?: string;
}

export interface AvailabilityResponse {
  service_id: string;
  booking_date: string;
  slots: TimeSlot[];
}

export interface BookingCreate {
  service_id: string;
  provider_id: string;
  booking_date: string;
  start_time: string;
  customer_name: string;
  customer_email: string;
  customer_phone: string;
  notes?: string;
}

export interface BookingFilters {
  user_id?: string;
  provider_id?: string;
  status?: string;
  start_date?: string;
  end_date?: string;
  page?: number;
  page_size?: number;
}

export interface BookingList {
  items: Booking[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}
