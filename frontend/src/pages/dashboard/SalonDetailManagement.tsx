import { useQuery } from '@tanstack/react-query';
import { useParams, useNavigate } from 'react-router-dom';
import { managerApi } from '../../api/manager';
import ServiceManagement from '../../components/manager/ServiceManagement';
import WorkingHoursManagement from '../../components/manager/WorkingHoursManagement';
import StylistManagement from '../../components/manager/StylistManagement';

const SalonDetailManagement: React.FC = () => {
    const { salonId } = useParams<{ salonId: string }>();
    const navigate = useNavigate();

    const { data: salon, isLoading } = useQuery({
        queryKey: ['manager', 'salon', salonId],
        queryFn: () => managerApi.getSalonById(Number(salonId)),
        enabled: !!salonId,
    });

    if (isLoading) {
        return <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 text-center">در حال بارگزاری...</div>;
    }

    if (!salon) {
        return <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 text-center text-red-600">سالن یافت نشد</div>;
    }

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex items-center gap-4 mb-6">
                <button
                    onClick={() => navigate('/manager/dashboard')}
                    className="text-blue-600 hover:text-blue-800"
                >
                    ← بازگشت به لیست سالن‌ها
                </button>
            </div>

            <h1 className="text-2xl font-bold text-gray-900 mb-6">
                مدیریت سالن: {salon.name}
            </h1>

            {/* Salon Info Card */}
            <div className="bg-white shadow overflow-hidden sm:rounded-lg mb-6">
                <div className="px-4 py-5 sm:px-6">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">اطلاعات سالن</h3>
                </div>
                <div className="border-t border-gray-200 px-4 py-5 sm:px-6">
                    <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
                        <div>
                            <dt className="text-sm font-medium text-gray-500">نام سالن</dt>
                            <dd className="mt-1 text-sm text-gray-900">{salon.name}</dd>
                        </div>
                        <div>
                            <dt className="text-sm font-medium text-gray-500">نوع سالن</dt>
                            <dd className="mt-1 text-sm text-gray-900">{salon.gender_type === 'male' ? 'مردانه' : 'زنانه'}</dd>
                        </div>
                        <div className="sm:col-span-2">
                            <dt className="text-sm font-medium text-gray-500">آدرس</dt>
                            <dd className="mt-1 text-sm text-gray-900">{salon.address}</dd>
                        </div>
                        <div>
                            <dt className="text-sm font-medium text-gray-500">میانگین امتیاز</dt>
                            <dd className="mt-1 text-sm text-gray-900">{Number(salon.average_rating || 0).toFixed(1)} ({salon.total_ratings || 0} نظر)</dd>
                        </div>
                        <div>
                            <dt className="text-sm font-medium text-gray-500">تعداد آرایشگران</dt>
                            <dd className="mt-1 text-sm text-gray-900">{salon.stylists.length} نفر</dd>
                        </div>
                    </dl>
                </div>
            </div>

            {/* Stylist Management */}
            <div className="mb-6">
                <StylistManagement salonId={Number(salonId)} />
            </div>

            {/* Services Management */}
            <div className="mb-6">
                <ServiceManagement salonGenderType={salon.gender_type} />
            </div>

            {/* Working Hours Management */}
            <div className="mb-6">
                <WorkingHoursManagement />
            </div>
        </div>
    );
};

export default SalonDetailManagement;
