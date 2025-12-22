import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { adminApi } from '../../api/admin';
import { useAuth } from '../../hooks/useAuth';
import Button from '../../components/ui/Button';
import UserManagementTable from '../../components/admin/UserManagementTable';
import ChatQueuePanel from '../../components/admin/ChatQueuePanel';

const StatCard = ({ title, value, color = 'blue' }: { title: string, value: number, color?: string }) => (
    <div className={`bg-white overflow-hidden shadow rounded-lg border-l-4 border-${color}-500`}>
        <div className="px-4 py-5 sm:p-6">
            <dt className="text-sm font-medium text-gray-500 truncate">{title}</dt>
            <dd className="mt-1 text-3xl font-semibold text-gray-900">{value}</dd>
        </div>
    </div>
);

type TabType = 'overview' | 'users' | 'chat-queue';

const AdminDashboard: React.FC = () => {
    const { logout } = useAuth();
    const [activeTab, setActiveTab] = useState<TabType>('overview');

    const { data: stats, isLoading, error } = useQuery({
        queryKey: ['admin', 'stats'],
        queryFn: adminApi.getStats,
    });

    if (isLoading) return <div className="p-8 text-center">در حال بارگذاری آمار...</div>;
    if (error) return <div className="p-8 text-center text-red-500">خطا در دریافت اطلاعات</div>;

    return (
        <div className="min-h-screen bg-gray-100 p-8" dir="rtl">
            <div className="max-w-7xl mx-auto">
                <div className="flex justify-between items-center mb-8">
                    <h1 className="text-3xl font-bold text-gray-900">داشبورد مدیریت سیستم</h1>
                    <Button variant="secondary" onClick={() => logout()} className="w-auto">
                        خروج
                    </Button>
                </div>

                {/* Tabs */}
                <div className="mb-6 border-b border-gray-200">
                    <nav className="-mb-px flex space-x-8 space-x-reverse">
                        <button
                            onClick={() => setActiveTab('overview')}
                            className={`${activeTab === 'overview' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'} whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
                        >
                            نمای کلی
                        </button>
                        <button
                            onClick={() => setActiveTab('users')}
                            className={`${activeTab === 'users' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'} whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
                        >
                            مدیریت کاربران
                        </button>
                        <button
                            onClick={() => setActiveTab('chat-queue')}
                            className={`${activeTab === 'chat-queue' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'} whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
                        >
                            صف چت پشتیبانی
                        </button>
                    </nav>
                </div>

                {/* Tab Content */}
                {activeTab === 'overview' && stats && (
                    <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
                        <StatCard title="کل کاربران" value={stats.total_users} />
                        <StatCard title="مشتریان" value={stats.total_customers} color="green" />
                        <StatCard title="آرایشگران" value={stats.total_stylists} color="purple" />
                        <StatCard title="مدیران سالن" value={stats.total_managers} color="yellow" />
                        <StatCard title="سالن‌های فعال" value={stats.active_salons} color="indigo" />
                        <StatCard title="نوبت‌های امروز" value={stats.today_appointments} color="red" />
                    </div>
                )}

                {activeTab === 'users' && (
                    <div className="bg-white shadow rounded-lg p-6">
                        <UserManagementTable />
                    </div>
                )}

                {activeTab === 'chat-queue' && (
                    <ChatQueuePanel />
                )}
            </div>
        </div>
    );
};

export default AdminDashboard;
