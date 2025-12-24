/**
 * Profile API client
 */
import client from './client';

export interface CustomerProfile {
    id: number;
    first_name: string;
    last_name: string;
    gender: 'male' | 'female';
    date_of_birth: string;
    telegram_chat_id: string | null;
}

export interface StylistProfile {
    id: number;
    full_name: string;
    gender: string;
    telegram_chat_id: string | null;
}

export interface ManagerProfile {
    id: number;
    full_name: string;
    telegram_chat_id: string | null;
}

export const profileApi = {
    // Customer profile
    updateCustomerProfile: async (data: Partial<CustomerProfile>) => {
        const response = await client.patch<CustomerProfile>('/accounts/api/profile/customer/', data);
        return response.data;
    },

    // Stylist profile
    updateStylistProfile: async (data: Partial<StylistProfile>) => {
        const response = await client.patch<StylistProfile>('/accounts/api/profile/stylist/', data);
        return response.data;
    },

    // Manager profile
    updateManagerProfile: async (data: Partial<ManagerProfile>) => {
        const response = await client.patch<ManagerProfile>('/accounts/api/profile/manager/', data);
        return response.data;
    },
};
