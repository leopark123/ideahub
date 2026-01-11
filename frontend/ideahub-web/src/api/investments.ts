import { apiClient } from './client';

export interface Investment {
  id: string;
  investor_id: string;
  crowdfunding_id: string;
  amount: number;
  reward_tier_id: string | null;
  payment_method: 'alipay' | 'wechat' | 'bank' | null;
  transaction_id: string | null;
  status: 'pending' | 'paid' | 'confirmed' | 'refunded' | 'cancelled';
  notes: string | null;
  created_at: string;
}

export interface InvestmentCreate {
  crowdfunding_id: string;
  amount: number;
  reward_tier_id?: string;
  payment_method: 'alipay' | 'wechat' | 'bank';
}

export interface InvestmentList {
  items: Investment[];
  total: number;
  page: number;
  page_size: number;
}

export const investmentsApi = {
  create: async (data: InvestmentCreate): Promise<Investment> => {
    const response = await apiClient.post<Investment>('/investments', data);
    return response.data;
  },

  getMyInvestments: async (page = 1, pageSize = 10): Promise<InvestmentList> => {
    const response = await apiClient.get<InvestmentList>('/investments/my', {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },

  getById: async (id: string): Promise<Investment> => {
    const response = await apiClient.get<Investment>(`/investments/${id}`);
    return response.data;
  },

  confirm: async (id: string, transactionId: string): Promise<Investment> => {
    const response = await apiClient.post<Investment>(
      `/investments/${id}/confirm`,
      null,
      { params: { transaction_id: transactionId } }
    );
    return response.data;
  },
};
