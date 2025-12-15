import client from './client';
import type { User, AuthResponse } from '../types/auth';

export const authApi = {
    login: async (credentials: { phone_number: string; password: string }) => {
        const response = await client.post<AuthResponse>('/accounts/api/login/', credentials);
        return response.data;
    },

    logout: async () => {
        const response = await client.post('/accounts/api/logout/');
        return response.data;
    },

    registerCustomer: async (data: FormData) => {
        const response = await client.post('/accounts/api/register/customer/', data, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
        return response.data;
    },

    registerManager: async (data: FormData) => {
        const response = await client.post('/accounts/api/register/manager/', data, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
        return response.data;
    },

    getCurrentUser: async () => {
        const response = await client.get<User>('/accounts/api/me/');
        return response.data;
    },

    getCsrf: async () => {
        await client.get('/accounts/api/csrf/');
    }
};
