import client from './client';

export interface TimeSlotResponse {
    stylist_id: string;
    stylist_name: string;
    jalali_date: string;
    available_slots: string[];
    working_hours: {
        start: string;
        end: string;
    };
}

export interface BookingRequest {
    stylist_id: number;
    service_id: number;
    jalali_date: string; // YYYY/MM/DD
    time_slot: string;   // HH:MM
    customer_notes?: string;
}

export interface Appointment {
    id: number;
    customer_name?: string; // Present for stylists
    stylist_name: string;
    service_name: string;
    salon_name: string;
    salon_address: string;
    appointment_date: string; // Gregorian ISO
    appointment_time: string;
    jalali_date: string;
    status: 'pending' | 'confirmed' | 'cancelled' | 'completed';
    customer_notes?: string;
}

export interface MyAppointmentsResponse {
    count: number;
    appointments: Appointment[];
}

export const appointmentApi = {
    getAvailability: async (stylistId: number, jalaliDate: string) => {
        const response = await client.get<TimeSlotResponse>('/appointments/api/availability/', {
            params: { stylist_id: stylistId, jalali_date: jalaliDate },
        });
        return response.data;
    },

    bookAppointment: async (data: BookingRequest) => {
        const response = await client.post('/appointments/api/book/', data);
        return response.data;
    },

    myAppointments: async () => {
        const response = await client.get<MyAppointmentsResponse>('/appointments/api/my-appointments/');
        return response.data;
    },

    cancelAppointment: async (id: number) => {
        const response = await client.post(`/appointments/api/cancel/${id}/`);
        return response.data;
    }
};
