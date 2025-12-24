import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { appointmentApi, type Appointment } from '../../api/appointments';
import { useAuth } from '../../hooks/useAuth';
import StylistProfileManagement from '../../components/profile/StylistProfileManagement';

type TabType = 'appointments' | 'profile';

const StylistDashboard: React.FC = () => {
    const { user, logout } = useAuth();
    const [activeTab, setActiveTab] = useState<TabType>('appointments');

    const { data, isLoading, error } = useQuery({
        queryKey: ['stylist-appointments'],
        queryFn: appointmentApi.myAppointments
    });

    const appointments = data?.appointments || [];

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">
                        پنل آرایشگر
                    </h1>
                    {user?.stylist_profile && (
                        <p className="text-gray-600 mt-1">
                            خوش آمدید، {user.stylist_profile.full_name}
                        </p>
                    )}
                </div>

                <button
                    onClick={() => logout()}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                >
                    خروج
                </button>
            </div>

            {/* Tabs */}
            <div className="border-b border-gray-200 mb-6">
                <nav className="-mb-px flex gap-8">
                    <button
                        onClick={() => setActiveTab('appointments')}
                        className={`pb-4 px-1 border-b-2 font-medium text-sm transition-colors ${activeTab === 'appointments'
                                ? 'border-indigo-500 text-indigo-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                    >
                        📅 نوبت‌های من
                    </button>
                    <button
                        onClick={() => setActiveTab('profile')}
                        className={`pb-4 px-1 border-b-2 font-medium text-sm transition-colors ${activeTab === 'profile'
                                ? 'border-indigo-500 text-indigo-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                    >
                        👤 پروفایل من
                    </button>
                </nav>
            </div>

            {/* Tab Content */}
            {activeTab === 'profile' ? (
                <StylistProfileManagement />
            ) : (
                <>
                    {isLoading ? (
                        <div className="p-8 text-center">در حال بارگزاری برنامه کاری...</div>
                    ) : error ? (
                        <div className="p-8 text-center text-red-500">خطا در دریافت اطلاعات</div>
                    ) : (
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
                    )}
                </>
            )}
        </div>
    );
};

export default StylistDashboard;
