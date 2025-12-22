/**
 * API endpoints for Salon Manager Dashboard
 */
import client from './client';

export interface Service {
    id: number;
    service_type: string;
    service_type_display: string;
    custom_name: string;
    price: number;
    duration_minutes: number;
    is_active: boolean;
    stylist: number | null;
    stylist_name?: string;
}

export interface WorkingHours {
    id: number;
    day_of_week: number;
    day_of_week_display: string;
    start_time: string;
    end_time: string;
    is_active: boolean;
}

export interface Stylist {
    id: number;
    full_name: string;
    phone_number: string;
    user: number;
}

export interface SalonDetails {
    id: number;
    name: string;
    address: string;
    gender_type: 'male' | 'female';
    photo: string;
    average_rating: number;
    total_ratings: number;
    services: Service[];
    working_hours: WorkingHours[];
    stylists: Stylist[];
}

export const managerApi = {
    // Multi-Salon Management
    getSalons: async () => {
        const response = await client.get<SalonDetails[]>('/salons/api/manager/salons/');
        return response.data;
    },

    createSalon: async (data: { name: string; address: string; gender_type: 'male' | 'female' }) => {
        const response = await client.post<SalonDetails>('/salons/api/manager/salons/', data);
        return response.data;
    },

    getSalonById: async (salonId: number) => {
        const response = await client.get<SalonDetails>(`/salons/api/manager/salons/${salonId}/`);
        return response.data;
    },

    updateSalonById: async (salonId: number, data: Partial<SalonDetails>) => {
        const response = await client.patch<SalonDetails>(`/salons/api/manager/salons/${salonId}/`, data);
        return response.data;
    },

    deleteSalon: async (salonId: number) => {
        await client.delete(`/salons/api/manager/salons/${salonId}/`);
    },

    // Stylist Management
    getStylists: async (salonId: number) => {
        const response = await client.get<Stylist[]>(`/salons/api/manager/salons/${salonId}/stylists/`);
        return response.data;
    },

    createStylist: async (salonId: number, data: { full_name: string; phone_number: string; password?: string }) => {
        const response = await client.post<Stylist>(`/salons/api/manager/salons/${salonId}/stylists/`, data);
        return response.data;
    },

    updateStylist: async (stylistId: number, data: Partial<Stylist>) => {
        const response = await client.patch<Stylist>(`/salons/api/manager/stylists/${stylistId}/`, data);
        return response.data;
    },

    deleteStylist: async (stylistId: number) => {
        await client.delete(`/salons/api/manager/stylists/${stylistId}/`);
    },

    // Legacy - Single Salon (backward compatibility)
    // Get salon details
    getSalon: async () => {
        const response = await client.get<SalonDetails>('/salons/api/manager/salon/');
        return response.data;
    },

    // Update salon details
    updateSalon: async (data: Partial<SalonDetails>) => {
        const response = await client.patch<SalonDetails>('/salons/api/manager/salon/', data);
        return response.data;
    },

    // Services
    getServices: async () => {
        const response = await client.get<Service[]>('/salons/api/manager/services/');
        return response.data;
    },

    createService: async (data: Partial<Service>) => {
        const response = await client.post<Service>('/salons/api/manager/services/', data);
        return response.data;
    },

    updateService: async (id: number, data: Partial<Service>) => {
        const response = await client.patch<Service>(`/salons/api/manager/services/${id}/`, data);
        return response.data;
    },

    deleteService: async (id: number) => {
        await client.delete(`/salons/api/manager/services/${id}/`);
    },

    // Working Hours
    getWorkingHours: async () => {
        const response = await client.get<WorkingHours[]>('/salons/api/manager/working-hours/');
        return response.data;
    },

    createWorkingHours: async (data: Partial<WorkingHours>) => {
        const response = await client.post<WorkingHours>('/salons/api/manager/working-hours/', data);
        return response.data;
    },

    updateWorkingHours: async (id: number, data: Partial<WorkingHours>) => {
        const response = await client.patch<WorkingHours>(`/salons/api/manager/working-hours/${id}/`, data);
        return response.data;
    },

    deleteWorkingHours: async (id: number) => {
        await client.delete(`/salons/api/manager/working-hours/${id}/`);
    },
};
