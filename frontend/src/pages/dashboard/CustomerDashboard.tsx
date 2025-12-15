import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { appointmentApi } from '../../api/appointments';
import type { Appointment } from '../../api/appointments';
import Button from '../../components/ui/Button';
import { useAuth } from '../../hooks/useAuth';

const CustomerDashboard: React.FC = () => {
    const { user } = useAuth();
    const queryClient = useQueryClient();

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

    if (isLoading) return <div className="p-8 text-center">در حال بارگزاری نوبت‌ها...</div>;
    if (error) return <div className="p-8 text-center text-red-500">خطا در دریافت اطلاعات</div>;

    const appointments = data?.appointments || [];

    // Simple logic to separate upcoming vs past, though backend sort order helps
    // We'll trust backend order (descending date) for now and just render them.
    // Ideally we might split them by status or date.

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <h1 className="text-2xl font-bold text-gray-900 mb-6">
                داشبورد کاربری
                {user?.customer_profile && <span className="text-gray-500 font-normal text-lg mr-2">({user.customer_profile.full_name})</span>}
            </h1>

            <div className="bg-white shadow overflow-hidden sm:rounded-lg">
                <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">نوبت‌های من</h3>
                </div>

                {appointments.length === 0 ? (
                    <div className="p-8 text-center text-gray-500">
                        شما هیچ نوبتی ندارید.
                        <div className="mt-4">
                            <a href="/" className="text-blue-600 hover:text-blue-500">رزرو نوبت جدید &larr;</a>
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
        </div>
    );
};

export default CustomerDashboard;
