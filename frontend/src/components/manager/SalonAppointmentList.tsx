import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { managerApi } from '../../api/manager';

interface SalonAppointmentListProps {
    salonId: number;
}

const SalonAppointmentList: React.FC<SalonAppointmentListProps> = ({ salonId }) => {
    const queryClient = useQueryClient();
    const [filterStatus, setFilterStatus] = useState<'all' | 'pending' | 'confirmed' | 'cancelled'>('all');
    const [cancellationId, setCancellationId] = useState<number | null>(null);
    const [cancellationReason, setCancellationReason] = useState('');

    const { data, isLoading } = useQuery({
        queryKey: ['manager', 'appointments', salonId],
        queryFn: () => managerApi.getSalonAppointments(salonId),
    });

    const approveMutation = useMutation({
        mutationFn: (id: number) => managerApi.approveAppointment(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['manager', 'appointments', salonId] });
            alert('نوبت با موفقیت تأیید شد');
        },
        onError: (error: any) => {
            alert(error.response?.data?.error || 'خطا در تأیید نوبت');
        }
    });

    const cancelMutation = useMutation({
        mutationFn: ({ id, reason }: { id: number; reason: string }) => managerApi.cancelAppointment(id, reason),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['manager', 'appointments', salonId] });
            setCancellationId(null);
            setCancellationReason('');
            alert('نوبت با موفقیت لغو شد');
        },
        onError: (error: any) => {
            alert(error.response?.data?.error || 'خطا در لغو نوبت');
        }
    });

    const handleCancelSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (cancellationId && cancellationReason.trim()) {
            cancelMutation.mutate({ id: cancellationId, reason: cancellationReason });
        }
    };

    if (isLoading) return <div className="text-center py-4">در حال بارگزاری نوبت‌ها...</div>;

    const appointments = data?.appointments || [];

    const filteredAppointments = appointments.filter((app: any) => {
        if (filterStatus === 'all') return true;
        return app.status === filterStatus;
    });

    return (
        <div className="bg-white shadow overflow-hidden sm:rounded-lg mb-6">
            <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
                <h3 className="text-lg leading-6 font-medium text-gray-900">مدیریت نوبت‌ها</h3>
                <div className="flex gap-2">
                    <button
                        onClick={() => setFilterStatus('all')}
                        className={`px-3 py-1 rounded-md text-sm ${filterStatus === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'}`}
                    >
                        همه
                    </button>
                    <button
                        onClick={() => setFilterStatus('pending')}
                        className={`px-3 py-1 rounded-md text-sm ${filterStatus === 'pending' ? 'bg-yellow-500 text-white' : 'bg-gray-100 text-gray-700'}`}
                    >
                        در انتظار
                    </button>
                    <button
                        onClick={() => setFilterStatus('confirmed')}
                        className={`px-3 py-1 rounded-md text-sm ${filterStatus === 'confirmed' ? 'bg-green-600 text-white' : 'bg-gray-100 text-gray-700'}`}
                    >
                        تأیید شده
                    </button>
                    <button
                        onClick={() => setFilterStatus('cancelled')}
                        className={`px-3 py-1 rounded-md text-sm ${filterStatus === 'cancelled' ? 'bg-red-600 text-white' : 'bg-gray-100 text-gray-700'}`}
                    >
                        لغو شده
                    </button>
                </div>
            </div>

            <div className="border-t border-gray-200">
                {filteredAppointments.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">نوبتی یافت نشد</div>
                ) : (
                    <ul className="divide-y divide-gray-200">
                        {filteredAppointments.map((app: any) => (
                            <li key={app.id} className="px-4 py-4 sm:px-6 hover:bg-gray-50">
                                <div className="flex items-center justify-between">
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center justify-between mb-2">
                                            <p className="text-sm font-medium text-blue-600 truncate">
                                                {app.customer_name}
                                            </p>
                                            <div className="ml-2 flex-shrink-0 flex">
                                                <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                                                    ${app.status === 'confirmed' ? 'bg-green-100 text-green-800' :
                                                        app.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                                                            app.status === 'cancelled' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'}`}>
                                                    {app.status_display}
                                                </span>
                                            </div>
                                        </div>
                                        <div className="mt-2 text-sm text-gray-500 grid grid-cols-2 gap-2">
                                            <div>
                                                <p>📅 {app.jalali_date}</p>
                                                <p>⏰ {app.appointment_time?.substring(0, 5)}</p>
                                            </div>
                                            <div>
                                                <p>💇 {app.stylist_name}</p>
                                                <p>✂️ {app.service_name}</p>
                                            </div>
                                            {app.customer_notes && (
                                                <div className="col-span-2 mt-1 bg-gray-50 p-2 rounded text-xs">
                                                    📝 یادداشت: {app.customer_notes}
                                                </div>
                                            )}
                                            {app.status === 'cancelled' && app.cancellation_reason && (
                                                <div className="col-span-2 mt-1 bg-red-50 p-2 rounded text-xs text-red-700">
                                                    🛑 دلیل لغو: {app.cancellation_reason}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                    <div className="mr-4 flex flex-col gap-2">
                                        {app.status === 'pending' && (
                                            <button
                                                onClick={() => approveMutation.mutate(app.id)}
                                                disabled={approveMutation.isPending}
                                                className="inline-flex items-center justify-center px-3 py-1 border border-transparent text-xs font-medium rounded text-white bg-green-600 hover:bg-green-700 disabled:opacity-50"
                                            >
                                                تأیید
                                            </button>
                                        )}
                                        {['pending', 'confirmed'].includes(app.status) && (
                                            <button
                                                onClick={() => setCancellationId(app.id)}
                                                className="inline-flex items-center justify-center px-3 py-1 border border-transparent text-xs font-medium rounded text-white bg-red-600 hover:bg-red-700"
                                            >
                                                لغو
                                            </button>
                                        )}
                                    </div>
                                </div>
                            </li>
                        ))}
                    </ul>
                )}
            </div>

            {/* Cancellation Modal */}
            {cancellationId && (
                <div className="fixed z-10 inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
                    <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
                        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" onClick={() => setCancellationId(null)}></div>
                        <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
                        <div className="inline-block align-bottom bg-white rounded-lg text-right overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
                            <form onSubmit={handleCancelSubmit}>
                                <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                                    <h3 className="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                                        لغو نوبت
                                    </h3>
                                    <div className="mt-2">
                                        <p className="text-sm text-gray-500 mb-4">
                                            لطفاً دلیل لغو نوبت را وارد کنید. این متن برای مشتری ارسال خواهد شد.
                                        </p>
                                        <textarea
                                            required
                                            value={cancellationReason}
                                            onChange={(e) => setCancellationReason(e.target.value)}
                                            className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md p-2 border"
                                            rows={3}
                                            placeholder="مثال: بیماری آرایشگر، تعطیلی اضطراری..."
                                        />
                                    </div>
                                </div>
                                <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse gap-2">
                                    <button
                                        type="submit"
                                        disabled={cancelMutation.isPending}
                                        className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50"
                                    >
                                        {cancelMutation.isPending ? 'در حال لغو...' : 'لغو نوبت'}
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => {
                                            setCancellationId(null);
                                            setCancellationReason('');
                                        }}
                                        className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
                                    >
                                        انصراف
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default SalonAppointmentList;
