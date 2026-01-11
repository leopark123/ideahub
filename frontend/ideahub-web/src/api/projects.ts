import { apiClient } from './client';

export interface ProjectOwner {
  id: string;
  nickname: string | null;
  avatar: string | null;
  role: string;
}

export interface Project {
  id: string;
  owner_id: string;
  title: string;
  subtitle: string | null;
  description: string;
  category: string;
  cover_image: string | null;
  cover_url: string | null;
  images: string | null;
  video_url: string | null;
  required_skills: string | null;
  looking_for: string | null;
  team_size: number;
  status: string;
  view_count: number;
  like_count: number;
  created_at: string;
  updated_at: string;
  owner?: ProjectOwner;
}

export interface ProjectList {
  items: Project[];
  total: number;
  page: number;
  page_size: number;
}

export interface CreateProjectData {
  title: string;
  subtitle?: string;
  description: string;
  category: string;
  cover_image?: string;
  images?: string[];
  video_url?: string;
  required_skills?: string[];
  team_size?: number;
}

export interface ProjectFilters {
  page?: number;
  page_size?: number;
  category?: string;
  status?: string;
  keyword?: string;
}

export const projectsApi = {
  list: async (filters: ProjectFilters = {}): Promise<ProjectList> => {
    const params = new URLSearchParams();
    if (filters.page) params.set('page', filters.page.toString());
    if (filters.page_size) params.set('page_size', filters.page_size.toString());
    if (filters.category) params.set('category', filters.category);
    if (filters.status) params.set('status', filters.status);
    if (filters.keyword) params.set('keyword', filters.keyword);

    const response = await apiClient.get<ProjectList>(`/projects?${params.toString()}`);
    return response.data;
  },

  get: async (id: string): Promise<Project> => {
    const response = await apiClient.get<Project>(`/projects/${id}`);
    return response.data;
  },

  getById: async (id: string): Promise<Project> => {
    const response = await apiClient.get<Project>(`/projects/${id}`);
    return response.data;
  },

  create: async (data: CreateProjectData): Promise<Project> => {
    const response = await apiClient.post<Project>('/projects', data);
    return response.data;
  },

  update: async (id: string, data: Partial<CreateProjectData>): Promise<Project> => {
    const response = await apiClient.put<Project>(`/projects/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/projects/${id}`);
  },

  publish: async (id: string): Promise<Project> => {
    const response = await apiClient.post<Project>(`/projects/${id}/publish`);
    return response.data;
  },

  like: async (id: string): Promise<Project> => {
    const response = await apiClient.post<Project>(`/projects/${id}/like`);
    return response.data;
  },
};
