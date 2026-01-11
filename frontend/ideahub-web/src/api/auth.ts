import { apiClient } from './client';

export interface LoginData {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  nickname?: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface UserResponse {
  id: string;
  email: string;
  nickname: string | null;
  avatar: string | null;
  bio: string | null;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export const authApi = {
  register: async (data: RegisterData): Promise<UserResponse> => {
    const response = await apiClient.post<UserResponse>('/auth/register', data);
    return response.data;
  },

  login: async (data: LoginData): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>('/auth/login', data);
    return response.data;
  },

  me: async (token?: string): Promise<UserResponse> => {
    const config = token
      ? { headers: { Authorization: `Bearer ${token}` } }
      : {};
    const response = await apiClient.get<UserResponse>('/auth/me', config);
    return response.data;
  },

  logout: async (): Promise<void> => {
    await apiClient.post('/auth/logout');
  },
};
