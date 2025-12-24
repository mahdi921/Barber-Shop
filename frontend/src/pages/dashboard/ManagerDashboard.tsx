import { useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import SalonList from '../../components/manager/SalonList';
import ManagerProfileManagement from '../../components/profile/ManagerProfileManagement';

type TabType = 'salons' | 'profile';

const ManagerDashboard: React.FC = () => {
    const { logout } = useAuth();
    const [activeTab, setActiveTab] = useState<TabType>('salons');

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold text-gray-900">
                    پنل مدیریت سالن
                </h1>

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
                        onClick={() => setActiveTab('salons')}
                        className={`pb-4 px-1 border-b-2 font-medium text-sm transition-colors ${activeTab === 'salons'
                                ? 'border-indigo-500 text-indigo-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                    >
                        🏪 سالن‌های من
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
                <ManagerProfileManagement />
            ) : (
                <SalonList />
            )}
        </div>
    );
};

export default ManagerDashboard;
