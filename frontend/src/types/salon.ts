export interface Service {
    id: number;
    service_type: string;
    custom_name: string;
    price: string;
    duration_minutes: number;
    stylist?: number;
    stylist_name?: string;
}

export interface Salon {
    id: number;
    name: string;
    photo: string;
    address: string;
    gender_type: 'male' | 'female';
    average_rating: string;
    total_ratings: number;
    manager_name: string;
    services: Service[];
    stylists: Stylist[];
}

export interface Stylist {
    id: number;
    first_name: string;
    last_name: string;
    full_name: string;
    is_temporary: boolean;
}

export const GENDER_LABELS = {
    male: 'مردانه',
    female: 'زنانه'
};
