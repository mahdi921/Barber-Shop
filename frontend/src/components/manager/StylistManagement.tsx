import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { managerApi, type Stylist } from '../../api/manager';

interface StylistManagementProps {
    salonId: number;
}

const StylistManagement: React.FC<StylistManagementProps> = ({ salonId }) => {
    const queryClient = useQueryClient();
    const [showAddModal, setShowAddModal] = useState(false);
    const [newStylist, setNewStylist] = useState({ full_name: '', phone_number: '', password: '' });

    const { data: stylists, isLoading } = useQuery({
        queryKey: ['manager', 'stylists', salonId],
        queryFn: () => managerApi.getStylists(salonId),
    });

    const createMutation = useMutation({
        mutationFn: (data: typeof newStylist) => managerApi.createStylist(salonId, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['manager', 'stylists', salonId] });
            setShowAddModal(false);
            setNewStylist({ full_name: '', phone_number: '', password: '' });
        },
    });

    const deleteMutation = useMutation({
        mutationFn: managerApi.deleteStylist,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['manager', 'stylists', salonId] });
        },
    });

    if (isLoading) {
        return <div className="text-center py-4">در حال بارگزاری...</div>;
    }

    return (
        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
            <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
                <h3 className="text-lg leading-6 font-medium text-gray-900">مدیریت آرایشگران</h3>
                <button
                    onClick={() => setShowAddModal(true)}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm"
                >
                    + افزودن آرایشگر
                </button>
            </div>
            <div className="border-t border-gray-200">
                {stylists && stylists.length > 0 ? (
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">نام</th>
                                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">شماره تلفن</th>
                                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">عملیات</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {stylists.map((stylist: Stylist) => (
                                <tr key={stylist.id}>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                        {stylist.full_name}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500" dir="ltr">
                                        {stylist.phone_number}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                                        <button
                                            onClick={() => {
                                                if (confirm('آیا از حذف این آرایشگر مطمئن هستید؟')) {
                                                    deleteMutation.mutate(stylist.id);
                                                }
                                            }}
                                            className="text-red-600 hover:text-red-900"
                                        >
                                            حذف
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                ) : (
                    <div className="px-6 py-12 text-center text-gray-500">
                        هنوز آرایشگری اضافه نشده است
                    </div>
                )}
            </div>

            {/* Add Stylist Modal */}
            {showAddModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-6 max-w-md w-full">
                        <h3 className="text-xl font-bold mb-4">افزودن آرایشگر جدید</h3>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium mb-1">نام کامل</label>
                                <input
                                    type="text"
                                    value={newStylist.full_name}
                                    onChange={(e) => setNewStylist({ ...newStylist, full_name: e.target.value })}
                                    className="w-full border rounded px-3 py-2"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">شماره تلفن</label>
                                <input
                                    type="text"
                                    value={newStylist.phone_number}
                                    onChange={(e) => setNewStylist({ ...newStylist, phone_number: e.target.value })}
                                    className="w-full border rounded px-3 py-2"
                                    dir="ltr"
                                    placeholder="09123456789"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">رمز عبور</label>
                                <input
                                    type="password"
                                    value={newStylist.password}
                                    onChange={(e) => setNewStylist({ ...newStylist, password: e.target.value })}
                                    className="w-full border rounded px-3 py-2"
                                    placeholder="اختیاری (پیش‌فرض: default123)"
                                />
                            </div>
                        </div>
                        <div className="flex gap-2 mt-6">
                            <button
                                onClick={() => createMutation.mutate(newStylist)}
                                disabled={!newStylist.full_name || !newStylist.phone_number || createMutation.isPending}
                                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                            >
                                {createMutation.isPending ? 'در حال افزودن...' : 'افزودن'}
                            </button>
                            <button
                                onClick={() => setShowAddModal(false)}
                                className="px-4 py-2 border rounded hover:bg-gray-50"
                            >
                                انصراف
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default StylistManagement;
