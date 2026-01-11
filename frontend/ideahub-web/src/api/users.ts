import { apiClient } from './client';
import type { Project } from './projects';
import type { Investment } from './investments';

export interface User {
  id: string;
  email: string;
  nickname: string | null;
  avatar: string | null;
  bio: string | null;
  skills: string | null;
  experience: string | null;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export interface UserUpdate {
  nickname?: string;
  avatar?: string;
  bio?: string;
  skills?: string[];
  experience?: string;
}

export const usersApi = {
  getMe: async (): Promise<User> => {
    const response = await apiClient.get<User>('/users/me');
    return response.data;
  },

  getUser: async (userId: string): Promise<User> => {
    const response = await apiClient.get<User>(`/users/${userId}`);
    return response.data;
  },

  updateMe: async (data: UserUpdate): Promise<User> => {
    const response = await apiClient.put<User>('/users/me', data);
    return response.data;
  },

  getMyProjects: async (): Promise<{ items: Project[]; total: number }> => {
    const response = await apiClient.get<{ items: Project[]; total: number }>('/users/me/projects');
    return response.data;
  },

  getMyInvestments: async (): Promise<{ items: Investment[]; total: number }> => {
    const response = await apiClient.get<{ items: Investment[]; total: number }>('/users/me/investments');
    return response.data;
  },
};
