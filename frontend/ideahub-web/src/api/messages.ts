import { apiClient } from './client';

export interface Message {
  id: string;
  sender_id: string;
  receiver_id: string;
  content: string;
  message_type: 'text' | 'image' | 'file' | 'system';
  attachment_url: string | null;
  attachment_name: string | null;
  is_read: boolean;
  read_at: string | null;
  project_id: string | null;
  created_at: string;
}

export interface MessageList {
  items: Message[];
  total: number;
  unread_count: number;
}

export interface MessageCreate {
  receiver_id: string;
  content: string;
  message_type?: 'text' | 'image' | 'file';
  attachment_url?: string;
  attachment_name?: string;
  project_id?: string;
}

export interface ConversationUser {
  id: string;
  username: string;
  nickname: string | null;
  avatar: string | null;
}

export interface ConversationSummary {
  user_id: string;
  user: ConversationUser | null;
  last_message: Message | null;
  unread_count: number;
}

export interface ConversationList {
  conversations: ConversationSummary[];
  total_unread: number;
}

export const messagesApi = {
  getConversations: async (): Promise<ConversationList> => {
    const response = await apiClient.get<ConversationList>('/messages/conversations');
    return response.data;
  },

  sendMessage: async (data: MessageCreate): Promise<Message> => {
    const response = await apiClient.post<Message>('/messages', data);
    return response.data;
  },

  getConversation: async (
    userId: string,
    page = 1,
    pageSize = 50
  ): Promise<MessageList> => {
    const response = await apiClient.get<MessageList>(
      `/messages/conversation/${userId}`,
      { params: { page, page_size: pageSize } }
    );
    return response.data;
  },

  getUnreadCount: async (): Promise<{ unread_count: number }> => {
    const response = await apiClient.get<{ unread_count: number }>('/messages/unread/count');
    return response.data;
  },

  markConversationRead: async (userId: string): Promise<{ marked_count: number }> => {
    const response = await apiClient.post<{ marked_count: number }>(
      `/messages/conversation/${userId}/read`
    );
    return response.data;
  },

  markMessageRead: async (messageId: string): Promise<Message> => {
    const response = await apiClient.post<Message>(`/messages/${messageId}/read`);
    return response.data;
  },
};
