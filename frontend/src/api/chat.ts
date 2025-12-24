/**
 * Chat API client for FAQ and chat operations
 */
import client from './client';

export interface FAQ {
    id: number;
    question: string;
    answer: string;
    keywords: string[];
    category: string;
    is_active: boolean;
    priority: number;
    view_count: number;
}

export interface ChatMessage {
    id?: number;
    sender_type: 'user' | 'bot' | 'admin' | 'ai' | 'system';
    sender_name?: string;
    content: string;
    metadata?: any;
    created_at?: string;
}

export interface ChatSession {
    id: number;
    session_key: string;
    status: 'bot' | 'queued' | 'admin' | 'closed';
    created_at: string;
    last_activity: string;
    messages: ChatMessage[];
    queue_position?: number;
}

export const chatApi = {
    // FAQ endpoints
    // Get initial FAQs for display on chat open
    getInitialFAQs: async (): Promise<FAQ[]> => {
        try {
            // Remove limit to get all active FAQs
            const response = await client.get<FAQ[]>('/chat/api/faqs/');
            console.log('FAQ API Response:', response.data);
            return Array.isArray(response.data) ? response.data : [];
        } catch (error) {
            console.error('Error fetching FAQs:', error);
            return []; // Return empty array on error
        }
    },

    getFAQs: async (category?: string) => {
        const params = category ? { category } : {};
        const response = await client.get<FAQ[]>('/chat/api/faqs/', { params });
        return response.data;
    },

    // Chat history
    getChatHistory: async (sessionKey: string) => {
        const response = await await client.get(`/chat/api/history/${sessionKey}/`);
        return response.data;
    },

    // Admin endpoints
    getDetailedQueue: async () => {
        const response = await client.get('/chat/api/admin/queue/detailed/');
        return response.data;
    },

    claimChat: async (sessionKey: string) => {
        const response = await client.post(`/chat/api/admin/claim/${sessionKey}/`);
        return response.data;
    },

    releaseChat: async (sessionKey: string, close: boolean = false) => {
        const response = await client.post(`/chat/api/admin/release/${sessionKey}/`, { close });
        return response.data;
    },

    getActiveChats: async () => {
        const response = await client.get('/chat/api/admin/active-chats/');
        return response.data;
    },

    getQueue: async () => {
        const response = await client.get('/chat/api/admin/queue/');
        return response.data;
    },

    closeChat: async (sessionKey: string) => {
        const response = await client.post(`/chat/api/admin/close/${sessionKey}/`);
        return response.data;
    },
};
