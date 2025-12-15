import client from './client';
import type { User } from '../types/auth';

export interface AdminStats {
    total_users: number;
    total_customers: number;
    total_stylists: number;
    total_managers: number;
    pending_managers: number;
    total_salons: number;
    active_salons: number;
    total_appointments: number;
    today_appointments: number;
}

export interface PaginatedUsers {
    count: number;
    next: string | null;
    previous: string | null;
    results: User[];
}

export const adminApi = {
    getStats: async () => {
        const response = await client.get<AdminStats>('/accounts/api/admin/stats/');
        return response.data;
    },

    getUsers: async (page = 1, userType = '') => {
        const response = await client.get<PaginatedUsers>('/accounts/api/admin/users/', {
            params: { page, user_type: userType },
        });
        return response.data;
    },
};
