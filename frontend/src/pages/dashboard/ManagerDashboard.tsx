import { useAuth } from '../../hooks/useAuth';
import SalonList from '../../components/manager/SalonList';

const ManagerDashboard: React.FC = () => {
    const { logout } = useAuth();

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold text-gray-900">
                    پنل مدیریت سالن
                </h1>

                <button
                    onClick={() => logout()}
                    className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 h-8"
                >
                    خروج
                </button>
            </div>

            <SalonList />
        </div>
    );
};

export default ManagerDashboard;
