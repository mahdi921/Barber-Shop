import client from './client';
import type { Salon } from '../types/salon';

export const salonApi = {
    getAll: async () => {
        const response = await client.get<Salon[]>('/salons/api/list/');
        // If backend returns pagination { results: [] }, handle it. 
        // DRF generic ListAPIView handles pagination automatically if set in settings.
        // Based on curl output: {"count":2, "results":[...]}
        // So we need to return .results if paginated, or .data if not.
        // Let's assume pagination is enabled as seen in curl output.
        if ('results' in response.data && Array.isArray((response.data as any).results)) {
            return (response.data as any).results as Salon[];
        }
        return response.data as unknown as Salon[];
    },

    getById: async (id: number) => {
        const response = await client.get<Salon>(`/salons/api/${id}/`);
        return response.data;
    },
};
