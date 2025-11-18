import axios, { AxiosInstance, AxiosRequestConfig, AxiosError } from 'axios';

// Token management
export const getAuthToken = (): string | null => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('access_token');
};

export const setAuthToken = (token: string): void => {
  if (typeof window === 'undefined') return;
  localStorage.setItem('access_token', token);
};

export const removeAuthToken = (): void => {
  if (typeof window === 'undefined') return;
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};

export const getRefreshToken = (): string | null => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('refresh_token');
};

// Base API client
const createApiClient = (baseURL: string): AxiosInstance => {
  const client = axios.create({
    baseURL,
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Request interceptor - add auth token
  client.interceptors.request.use(
    (config) => {
      const token = getAuthToken();
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // Response interceptor - handle errors
  client.interceptors.response.use(
    (response) => {
      return response;
    },
    async (error: AxiosError) => {
      const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };

      // Handle 401 - try to refresh token
      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;

        try {
          const refreshToken = getRefreshToken();
          if (!refreshToken) {
            throw new Error('No refresh token');
          }

          // Call refresh endpoint
          const response = await axios.post(
            `${process.env.NEXT_PUBLIC_AUTH_SERVICE_URL}/api/v1/auth/refresh`,
            { refresh_token: refreshToken }
          );

          const { access_token } = response.data;
          setAuthToken(access_token);

          // Retry original request
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
          }
          return client(originalRequest);
        } catch (refreshError) {
          // Refresh failed - logout user
          removeAuthToken();
          if (typeof window !== 'undefined') {
            window.location.href = '/auth/login';
          }
          return Promise.reject(refreshError);
        }
      }

      return Promise.reject(error);
    }
  );

  return client;
};

// Service clients
export const apiGateway = createApiClient(
  process.env.NEXT_PUBLIC_API_GATEWAY_URL || 'http://localhost'
);

export const siteServiceClient = createApiClient(
  process.env.NEXT_PUBLIC_SITE_SERVICE_URL || 'http://localhost:8010'
);

export const storefrontServiceClient = createApiClient(
  process.env.NEXT_PUBLIC_STOREFRONT_SERVICE_URL || 'http://localhost:8011'
);

export const bookingServiceClient = createApiClient(
  process.env.NEXT_PUBLIC_BOOKING_SERVICE_URL || 'http://localhost:8012'
);

export const leadServiceClient = createApiClient(
  process.env.NEXT_PUBLIC_LEAD_SERVICE_URL || 'http://localhost:8013'
);

export const contentServiceClient = createApiClient(
  process.env.NEXT_PUBLIC_CONTENT_SERVICE_URL || 'http://localhost:8014'
);

export const widgetServiceClient = createApiClient(
  process.env.NEXT_PUBLIC_WIDGET_SERVICE_URL || 'http://localhost:8015'
);

export const authServiceClient = createApiClient(
  process.env.NEXT_PUBLIC_AUTH_SERVICE_URL || 'http://localhost:8000'
);

// Generic error handler
export const handleApiError = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    if (error.response?.data?.detail) {
      return error.response.data.detail;
    }
    if (error.response?.statusText) {
      return error.response.statusText;
    }
    if (error.message) {
      return error.message;
    }
  }
  return 'An unexpected error occurred';
};
