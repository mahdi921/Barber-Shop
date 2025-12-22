import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { appointmentApi } from '../../api/appointments';
import type { Appointment } from '../../api/appointments';
import { useAuth } from '../../hooks/useAuth';
// Using standard button for simplicity as Button component import path wasn't verified in this file previously

const StylistDashboard: React.FC = () => {
    const { user, logout } = useAuth();

    // Reuse the same API as it adapts to user_type
    const { data, isLoading, error } = useQuery({
        queryKey: ['stylist-appointments'],
        queryFn: appointmentApi.myAppointments
    });

    if (isLoading) return <div className="p-8 text-center">در حال بارگزاری برنامه کاری...</div>;
    if (error) return <div className="p-8 text-center text-red-500">خطا در دریافت اطلاعات</div>;

    const appointments = data?.appointments || [];

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold text-gray-900">
                    پنل آرایشگر
                    {user?.stylist_profile && <span className="text-gray-500 font-normal text-lg mr-2">({user.stylist_profile.full_name})</span>}
                </h1>

                <div className="flex items-center gap-4">
                    <button
                        onClick={() => logout()}
                        className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 h-8"
                    >
                        خروج
                    </button>
                </div>
            </div>

            <div className="bg-white shadow overflow-hidden sm:rounded-lg">
                <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">نوبت‌های رزرو شده</h3>
                </div>

                {appointments.length === 0 ? (
                    <div className="p-8 text-center text-gray-500">
                        هیچ نوبتی برای شما ثبت نشده است.
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">مشتری</th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">خدمت</th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">تاریخ</th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">ساعت</th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">وضعیت</th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {appointments.map((apt: Appointment) => (
                                    <tr key={apt.id}>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                            {/* Note: Customer name might not be in Appointment interface yet, check serializer */}
                                            {/* Serializer has customer_name, let's update interface later if needed or rely on dynamic */}
                                            {(apt as any).customer_name}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            {apt.service_name}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            {apt.jalali_date}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            {apt.appointment_time.slice(0, 5)}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full
                                                ${apt.status === 'confirmed' ? 'bg-green-100 text-green-800' :
                                                    apt.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                                                        apt.status === 'cancelled' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'}
                                            `}>
                                                {apt.status === 'confirmed' ? 'تایید شده' :
                                                    apt.status === 'pending' ? 'در انتظار' :
                                                        apt.status === 'cancelled' ? 'لغو شده' : 'انجام شده'}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
};

export default StylistDashboard;
