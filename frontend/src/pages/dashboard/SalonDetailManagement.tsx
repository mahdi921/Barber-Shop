import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useParams, useNavigate } from 'react-router-dom';
import { managerApi } from '../../api/manager';
import ServiceManagement from '../../components/manager/ServiceManagement';
import WorkingHoursManagement from '../../components/manager/WorkingHoursManagement';
import StylistManagement from '../../components/manager/StylistManagement';
import SalonAppointmentList from '../../components/manager/SalonAppointmentList';

const SalonDetailManagement: React.FC = () => {
    const { salonId } = useParams<{ salonId: string }>();
    const navigate = useNavigate();
    const queryClient = useQueryClient();

    const { data: salon, isLoading } = useQuery({
        queryKey: ['manager', 'salon', salonId],
        queryFn: () => managerApi.getSalonById(Number(salonId)),
        enabled: !!salonId,
    });

    const updateSalonMutation = useMutation({
        mutationFn: (data: any) => managerApi.updateSalonById(Number(salonId), data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['manager', 'salon', salonId] });
            alert('تنظیمات با موفقیت ذخیره شد');
        },
        onError: () => {
            alert('خطا در ذخیره تنظیمات');
        }
    });

    const handleAutoApproveToggle = () => {
        if (!salon) return;
        updateSalonMutation.mutate({
            auto_approve_appointments: !salon.auto_approve_appointments
        });
    };

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

            {/* Salon Info & Settings Card */}
            <div className="bg-white shadow overflow-hidden sm:rounded-lg mb-6">
                <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">اطلاعات و تنظیمات سالن</h3>
                    <div className="flex items-center gap-2">
                        <span className="text-sm text-gray-700">تأیید خودکار نوبت‌ها:</span>
                        <button
                            onClick={handleAutoApproveToggle}
                            className={`relative inline-flex flex-shrink-0 h-6 w-11 border-2 border-transparent rounded-full cursor-pointer transition-colors ease-in-out duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${salon.auto_approve_appointments ? 'bg-green-600' : 'bg-gray-200'}`}
                        >
                            <span className="sr-only">Toggle Auto Approve</span>
                            <span
                                aria-hidden="true"
                                className={`pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow transform ring-0 transition ease-in-out duration-200 ${salon.auto_approve_appointments ? 'translate-x-0' : '-translate-x-5'}`} // RTL translate fix: 'translate-x-5' in LTR is right, in RTL might behave differently. 
                            // Actually 'translate-x-5' moves right. '-translate-x-5' moves left? No wait.
                            // In LTR: 0 is left, 5 is right.
                            // In RTL: direction is swapped? No transform translate is physical.
                            // Let's try standard classes. usually 0 is left.
                            ></span>
                        </button>
                    </div>
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

            {/* Appointment List with Management */}
            <SalonAppointmentList salonId={Number(salonId)} />

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
