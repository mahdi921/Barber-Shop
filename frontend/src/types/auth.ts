// Types matching Django Serializers

export interface CustomerProfile {
    id: number;
    first_name: string;
    last_name: string;
    full_name: string;
    selfie_photo?: string;
    gender: 'M' | 'F';
    jalali_date_of_birth?: string;
}

export interface SalonManagerProfile {
    id: number;
    salon_name: string;
    salon_photo?: string;
    salon_address: string;
    is_approved: boolean;
}

export interface StylistProfile {
    id: number;
    first_name: string;
    last_name: string;
    full_name: string;
    is_temporary: boolean;
    profile_completed_at?: string;
}

export interface User {
    id: number;
    phone_number: string;
    user_type: 'customer' | 'salon_manager' | 'stylist' | 'site_admin';
    is_active: boolean;
    is_staff: boolean;
    customer_profile?: CustomerProfile;
    manager_profile?: SalonManagerProfile;
    stylist_profile?: StylistProfile;

    // Computed helpers from api_current_user enrichment
    is_approved?: boolean;
    is_temporary?: boolean;
    profile_completed?: boolean;
}

export interface AuthResponse {
    detail: string;
    user: User;
}
