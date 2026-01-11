import { apiClient } from './client';

export type PartnershipStatus = 'pending' | 'approved' | 'rejected' | 'left';
export type PartnershipRole = 'founder' | 'co_founder' | 'partner' | 'advisor' | 'member';

export interface PartnershipUser {
  id: string;
  nickname: string | null;
  avatar: string | null;
  role: string;
}

export interface Partnership {
  id: string;
  project_id: string;
  user_id: string;
  role: PartnershipRole;
  position: string | null;
  responsibilities: string | null;
  equity_share: string | null;
  application_message: string | null;
  status: PartnershipStatus;
  created_at: string;
  user: PartnershipUser | null;
}

export interface PartnershipApply {
  project_id: string;
  role?: PartnershipRole;
  position?: string;
  application_message?: string;
}

export interface PartnershipList {
  items: Partnership[];
  total: number;
}

export const partnershipsApi = {
  apply: async (data: PartnershipApply): Promise<Partnership> => {
    const response = await apiClient.post<Partnership>('/partnerships', data);
    return response.data;
  },

  getMyApplications: async (page = 1, pageSize = 20): Promise<PartnershipList> => {
    const response = await apiClient.get<PartnershipList>('/partnerships/my', {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },

  getProjectPartnerships: async (
    projectId: string,
    status?: PartnershipStatus,
    page = 1,
    pageSize = 20
  ): Promise<PartnershipList> => {
    const response = await apiClient.get<PartnershipList>(`/partnerships/project/${projectId}`, {
      params: { status_filter: status, page, page_size: pageSize },
    });
    return response.data;
  },

  approve: async (partnershipId: string): Promise<Partnership> => {
    const response = await apiClient.post<Partnership>(`/partnerships/${partnershipId}/approve`);
    return response.data;
  },

  reject: async (partnershipId: string): Promise<Partnership> => {
    const response = await apiClient.post<Partnership>(`/partnerships/${partnershipId}/reject`);
    return response.data;
  },

  cancel: async (partnershipId: string): Promise<void> => {
    await apiClient.delete(`/partnerships/${partnershipId}`);
  },

  leave: async (partnershipId: string): Promise<Partnership> => {
    const response = await apiClient.post<Partnership>(`/partnerships/${partnershipId}/leave`);
    return response.data;
  },
};

export const roleLabels: Record<PartnershipRole, string> = {
  founder: '创始人',
  co_founder: '联合创始人',
  partner: '合伙人',
  advisor: '顾问',
  member: '团队成员',
};

export const statusLabels: Record<PartnershipStatus, string> = {
  pending: '申请中',
  approved: '已加入',
  rejected: '已拒绝',
  left: '已退出',
};
