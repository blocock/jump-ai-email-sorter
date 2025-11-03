import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

export interface Category {
  id: number;
  name: string;
  description: string;
  created_at: string;
  email_count: number;
}

export interface Email {
  id: number;
  gmail_message_id: string;
  subject: string;
  sender: string;
  sender_email: string;
  recipient: string;
  received_at: string;
  ai_summary: string;
  is_archived: boolean;
  is_deleted: boolean;
  unsubscribe_link: string | null;
  created_at: string;
  category_id: number;
}

export interface EmailDetail extends Email {
  body_text: string;
  body_html: string | null;
  thread_id: string;
  headers: any;
}

export interface GmailAccount {
  id: number;
  email: string;
  is_primary: boolean;
  created_at: string;
  last_synced: string | null;
}

export const authAPI = {
  login: async () => {
    const response = await api.get('/auth/login');
    return response.data;
  },
  
  connectAccount: async (code: string) => {
    const response = await api.post('/auth/connect-account', { code });
    return response.data;
  },
};

export const categoriesAPI = {
  list: async (): Promise<Category[]> => {
    const response = await api.get('/categories/');
    return response.data;
  },
  
  create: async (data: { name: string; description: string }): Promise<Category> => {
    const response = await api.post('/categories/', data);
    return response.data;
  },
  
  update: async (id: number, data: { name?: string; description?: string }): Promise<Category> => {
    const response = await api.put(`/categories/${id}`, data);
    return response.data;
  },
  
  delete: async (id: number): Promise<void> => {
    await api.delete(`/categories/${id}`);
  },
};

export const emailsAPI = {
  listByCategory: async (categoryId: number): Promise<Email[]> => {
    const response = await api.get(`/emails/category/${categoryId}`);
    return response.data;
  },
  
  get: async (emailId: number): Promise<EmailDetail> => {
    const response = await api.get(`/emails/${emailId}`);
    return response.data;
  },
  
  sync: async (): Promise<void> => {
    await api.post('/emails/sync');
  },
  
  bulkAction: async (emailIds: number[], action: 'delete' | 'unsubscribe'): Promise<void> => {
    await api.post('/emails/bulk-action', { email_ids: emailIds, action });
  },
  
  delete: async (emailId: number): Promise<void> => {
    await api.delete(`/emails/${emailId}`);
  },
};

export const accountsAPI = {
  list: async (): Promise<GmailAccount[]> => {
    const response = await api.get('/accounts/');
    return response.data;
  },
  
  disconnect: async (accountId: number): Promise<void> => {
    await api.delete(`/accounts/${accountId}`);
  },
};

export default api;

