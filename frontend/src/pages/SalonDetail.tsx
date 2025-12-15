import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { salonApi } from '../api/salons';
import BookingWizard from '../components/booking/BookingWizard';
import { useAuth } from '../hooks/useAuth';

const SalonDetail: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const { isAuthenticated } = useAuth();

    const { data: salon, isLoading, error } = useQuery({
        queryKey: ['salon', id],
        queryFn: () => salonApi.getById(Number(id)),
        enabled: !!id
    });

    if (isLoading) return <div className="text-center py-20">در حال دریافت اطلاعات سالن...</div>;
    if (error || !salon) return <div className="text-center py-20 text-red-500">سالن یافت نشد.</div>;

    return (
        <div className="min-h-screen bg-gray-50 py-8">
            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">

                {/* Salon Header */}
                <div className="bg-white rounded-lg shadow overflow-hidden mb-8">
                    <div className="h-64 w-full bg-gray-300 relative">
                        <img src={salon.photo} alt={salon.name} className="w-full h-full object-cover" />
                    </div>
                    <div className="p-6">
                        <div className="flex justify-between items-start">
                            <h1 className="text-3xl font-bold text-gray-900">{salon.name}</h1>
                            <div className="flex items-center bg-yellow-100 px-3 py-1 rounded-full text-yellow-800">
                                <span className="text-xl font-bold ml-1">{salon.average_rating}</span>
                                <span className="text-sm">({salon.total_ratings} نظر)</span>
                            </div>
                        </div>
                        <p className="mt-2 text-gray-600">{salon.address}</p>
                        <p className="mt-1 text-sm text-gray-500">مدیریت: {salon.manager_name}</p>
                    </div>
                </div>

                {/* Booking Wizard or Login Prompt */}
                {isAuthenticated ? (
                    <BookingWizard salon={salon} />
                ) : (
                    <div className="bg-white rounded-lg shadow p-8 text-center">
                        <h2 className="text-xl font-medium mb-4">برای رزرو نوبت وارد شوید</h2>
                        <a href="/login" className="text-blue-600 hover:text-blue-500 font-medium">
                            ورود به حساب کاربری &larr;
                        </a>
                    </div>
                )}
            </div>
        </div>
    );
};

export default SalonDetail;
