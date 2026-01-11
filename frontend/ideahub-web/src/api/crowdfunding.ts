import { apiClient } from './client';

export interface Crowdfunding {
  id: string;
  project_id: string;
  target_amount: number;
  current_amount: number;
  min_investment: number;
  max_investment: number | null;
  investor_count: number;
  status: 'pending' | 'active' | 'success' | 'failed' | 'cancelled';
  start_time: string;
  end_time: string;
  reward_tiers: string | null;
  created_at: string;
  updated_at: string;
  title: string | null;
  description: string | null;
}

export interface CrowdfundingListResponse {
  items: Crowdfunding[];
  total: number;
  page: number;
  page_size: number;
}

export interface CrowdfundingFilters {
  page?: number;
  page_size?: number;
  status?: string;
}

export interface CrowdfundingStats {
  total_raised: number;
  investor_count: number;
  days_remaining: number;
  progress_percentage: number;
}

export interface CrowdfundingCreate {
  project_id: string;
  target_amount: number;
  min_investment?: number;
  max_investment?: number;
  start_time: string;
  end_time: string;
}

export const crowdfundingApi = {
  list: async (filters: CrowdfundingFilters = {}): Promise<CrowdfundingListResponse> => {
    const params = new URLSearchParams();
    if (filters.page) params.set('page', filters.page.toString());
    if (filters.page_size) params.set('page_size', filters.page_size.toString());
    if (filters.status) params.set('status', filters.status);
    const response = await apiClient.get<CrowdfundingListResponse>(`/crowdfunding?${params.toString()}`);
    return response.data;
  },

  listActive: async (): Promise<Crowdfunding[]> => {
    const response = await apiClient.get<Crowdfunding[]>('/crowdfunding/active');
    return response.data;
  },

  getById: async (id: string): Promise<Crowdfunding> => {
    const response = await apiClient.get<Crowdfunding>(`/crowdfunding/${id}`);
    return response.data;
  },

  getByProject: async (projectId: string): Promise<Crowdfunding> => {
    const response = await apiClient.get<Crowdfunding>(`/crowdfunding/project/${projectId}`);
    return response.data;
  },

  getStats: async (id: string): Promise<CrowdfundingStats> => {
    const response = await apiClient.get<CrowdfundingStats>(`/crowdfunding/${id}/stats`);
    return response.data;
  },

  create: async (data: CrowdfundingCreate): Promise<Crowdfunding> => {
    const response = await apiClient.post<Crowdfunding>('/crowdfunding', data);
    return response.data;
  },

  start: async (id: string): Promise<Crowdfunding> => {
    const response = await apiClient.post<Crowdfunding>(`/crowdfunding/${id}/start`);
    return response.data;
  },
};
