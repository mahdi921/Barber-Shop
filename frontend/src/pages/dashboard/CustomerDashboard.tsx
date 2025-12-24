import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { appointmentApi, type Appointment } from '../../api/appointments';
import Button from '../../components/ui/Button';
import { useAuth } from '../../hooks/useAuth';
import CustomerProfileManagement from '../../components/profile/CustomerProfileManagement';
import TelegramStartButton from '../../components/TelegramStartButton';

type TabType = 'appointments' | 'profile';

const CustomerDashboard: React.FC = () => {
    const { user, logout } = useAuth();
    const queryClient = useQueryClient();
    const [activeTab, setActiveTab] = useState<TabType>('appointments');

    const { data, isLoading, error } = useQuery({
        queryKey: ['my-appointments'],
        queryFn: appointmentApi.myAppointments
    });

    const cancelMutation = useMutation({
        mutationFn: appointmentApi.cancelAppointment,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['my-appointments'] });
            alert('نوبت با موفقیت لغو شد');
        },
        onError: () => {
            alert('خطا در لغو نوبت');
        }
    });

    const handleCancel = (id: number) => {
        if (confirm('آیا از لغو این نوبت اطمینان دارید؟')) {
            cancelMutation.mutate(id);
        }
    };

    const appointments = data?.appointments || [];

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">
                        داشبورد کاربری
                    </h1>
                    {user?.customer_profile && (
                        <p className="text-gray-600 mt-1">
                            خوش آمدید، {user.customer_profile.first_name} {user.customer_profile.last_name}
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
                <CustomerProfileManagement />
            ) : (
                <>
                    {/* Telegram Bot - Always Visible on Main Tab */}
                    <TelegramStartButton />

                    {isLoading ? (
                        <div className="p-8 text-center">در حال بارگزاری نوبت‌ها...</div>
                    ) : error ? (
                        <div className="p-8 text-center text-red-500">خطا در دریافت اطلاعات</div>
                    ) : (
                        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
                            <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
                                <div className="flex justify-between items-center">
                                    <h3 className="text-lg leading-6 font-medium text-gray-900">نوبت‌های من</h3>
                                    <Link
                                        to="/"
                                        className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
                                    >
                                        <svg className="ml-2 -mr-1 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                                        </svg>
                                        رزرو نوبت جدید
                                    </Link>
                                </div>
                            </div>

                            {appointments.length === 0 ? (
                                <div className="p-8 text-center text-gray-500">
                                    شما هیچ نوبتی ندارید.
                                    <div className="mt-4">
                                        <Link to="/" className="text-blue-600 hover:text-blue-500 font-medium">رزرو نوبت جدید &larr;</Link>
                                    </div>
                                </div>
                            ) : (
                                <ul className="divide-y divide-gray-200">
                                    {appointments.map((apt: Appointment) => (
                                        <li key={apt.id} className="px-4 py-4 sm:px-6 hover:bg-gray-50 transition">
                                            <div className="flex items-center justify-between">
                                                <div className="flex flex-col">
                                                    <div className="flex items-center text-sm font-medium text-blue-600 truncate">
                                                        {apt.service_name}
                                                        <span className="text-gray-500 mx-2">|</span>
                                                        <span className="text-gray-900">{apt.salon_name}</span>
                                                    </div>
                                                    <div className="mt-2 flex items-center text-sm text-gray-500">
                                                        <svg className="flex-shrink-0 ml-1.5 h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                                        </svg>
                                                        <span className="ml-4">{apt.jalali_date}</span>

                                                        <svg className="flex-shrink-0 ml-1.5 h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                                        </svg>
                                                        <span>{apt.appointment_time.slice(0, 5)}</span>
                                                    </div>
                                                    <div className="mt-1 text-xs text-gray-500">
                                                        آرایشگر: {apt.stylist_name}
                                                    </div>
                                                </div>

                                                <div className="flex flex-col items-end gap-2">
                                                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full
                                                        ${apt.status === 'confirmed' ? 'bg-green-100 text-green-800' :
                                                            apt.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                                                                apt.status === 'cancelled' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'}
                                                    `}>
                                                        {apt.status === 'confirmed' ? 'تایید شده' :
                                                            apt.status === 'pending' ? 'در انتظار تایید' :
                                                                apt.status === 'cancelled' ? 'لغو شده' : 'انجام شده'}
                                                    </span>

                                                    {(apt.status === 'pending' || apt.status === 'confirmed') && (
                                                        <Button
                                                            variant="danger"
                                                            onClick={() => handleCancel(apt.id)}
                                                            className="text-xs px-2 py-1 h-auto"
                                                            isLoading={cancelMutation.isPending}
                                                        >
                                                            لغو نوبت
                                                        </Button>
                                                    )}
                                                </div>
                                            </div>
                                        </li>
                                    ))}
                                </ul>
                            )}
                        </div>
                    )}
                </>
            )}
        </div>
    );
};

export default CustomerDashboard;
