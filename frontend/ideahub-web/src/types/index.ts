export interface User {
  id: string;
  email: string;
  nickname: string;
  avatar?: string;
  bio?: string;
  role: 'user' | 'creator' | 'investor' | 'admin';
  skills: string[];
  isVerified: boolean;
  createdAt: string;
}

export interface Project {
  id: string;
  title: string;
  slogan?: string;
  coverImage?: string;
  category: string;
  stage: 'idea' | 'building' | 'funding' | 'launched';
  content?: string;
  tags: string[];
  viewCount: number;
  likeCount: number;
  owner: Pick<User, 'id' | 'nickname' | 'avatar'>;
  createdAt: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  pages: number;
}
