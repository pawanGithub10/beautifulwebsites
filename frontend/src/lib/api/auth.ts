import { authServiceClient, setAuthToken, removeAuthToken } from './client';
import type { User, LoginRequest, SignupRequest, AuthResponse, AuthTokens } from '@/types';

export const authApi = {
  // Login
  login: async (credentials: LoginRequest): Promise<AuthResponse> => {
    const response = await authServiceClient.post('/api/v1/auth/login', credentials);
    const { access_token, refresh_token, user } = response.data;

    // Store tokens
    if (typeof window !== 'undefined') {
      setAuthToken(access_token);
      localStorage.setItem('refresh_token', refresh_token);
    }

    return {
      user,
      tokens: {
        access_token,
        refresh_token,
        token_type: 'Bearer',
        expires_in: 3600,
      },
    };
  },

  // Signup
  signup: async (userData: SignupRequest): Promise<AuthResponse> => {
    const response = await authServiceClient.post('/api/v1/auth/signup', userData);
    const { access_token, refresh_token, user } = response.data;

    // Store tokens
    if (typeof window !== 'undefined') {
      setAuthToken(access_token);
      localStorage.setItem('refresh_token', refresh_token);
    }

    return {
      user,
      tokens: {
        access_token,
        refresh_token,
        token_type: 'Bearer',
        expires_in: 3600,
      },
    };
  },

  // Logout
  logout: async (): Promise<void> => {
    try {
      await authServiceClient.post('/api/v1/auth/logout');
    } finally {
      removeAuthToken();
    }
  },

  // Verify token
  verifyToken: async (token: string): Promise<User> => {
    const response = await authServiceClient.post('/api/v1/auth/verify', { token });
    return response.data.user;
  },

  // Refresh token
  refreshToken: async (refreshToken: string): Promise<AuthTokens> => {
    const response = await authServiceClient.post('/api/v1/auth/refresh', {
      refresh_token: refreshToken,
    });

    const { access_token, refresh_token: new_refresh_token } = response.data;

    // Store new tokens
    if (typeof window !== 'undefined') {
      setAuthToken(access_token);
      if (new_refresh_token) {
        localStorage.setItem('refresh_token', new_refresh_token);
      }
    }

    return {
      access_token,
      refresh_token: new_refresh_token || refreshToken,
      token_type: 'Bearer',
      expires_in: 3600,
    };
  },

  // Get current user
  getCurrentUser: async (): Promise<User> => {
    const response = await authServiceClient.get('/api/v1/auth/me');
    return response.data;
  },

  // Update profile
  updateProfile: async (updates: Partial<User>): Promise<User> => {
    const response = await authServiceClient.put('/api/v1/auth/profile', updates);
    return response.data;
  },

  // Change password
  changePassword: async (currentPassword: string, newPassword: string): Promise<void> => {
    await authServiceClient.post('/api/v1/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
  },

  // Request password reset
  requestPasswordReset: async (email: string): Promise<void> => {
    await authServiceClient.post('/api/v1/auth/forgot-password', { email });
  },

  // Reset password
  resetPassword: async (token: string, newPassword: string): Promise<void> => {
    await authServiceClient.post('/api/v1/auth/reset-password', {
      token,
      new_password: newPassword,
    });
  },
};
