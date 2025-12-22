import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { managerApi, type SalonDetails } from '../../api/manager';
import { useNavigate } from 'react-router-dom';

const SalonList: React.FC = () => {
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [newSalon, setNewSalon] = useState({ name: '', address: '', gender_type: 'male' as 'male' | 'female' });

    const { data: salons, isLoading } = useQuery({
        queryKey: ['manager', 'salons'],
        queryFn: managerApi.getSalons,
    });

    const createMutation = useMutation({
        mutationFn: managerApi.createSalon,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['manager', 'salons'] });
            setShowCreateModal(false);
            setNewSalon({ name: '', address: '', gender_type: 'male' });
        },
    });

    const deleteMutation = useMutation({
        mutationFn: managerApi.deleteSalon,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['manager', 'salons'] });
        },
    });

    if (isLoading) {
        return <div className="text-center py-8">در حال بارگزاری...</div>;
    }

    return (
        <div>
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold">سالن‌های من</h2>
                <button
                    onClick={() => setShowCreateModal(true)}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                    + ایجاد سالن جدید
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {salons?.map((salon: SalonDetails) => (
                    <div key={salon.id} className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
                        <h3 className="text-xl font-bold mb-2">{salon.name}</h3>
                        <p className="text-sm text-gray-600 mb-1">{salon.address}</p>
                        <p className="text-sm text-gray-500 mb-4">
                            {salon.gender_type === 'male' ? 'آقایان' : 'بانوان'} • {Number(salon.average_rating || 0).toFixed(1)} امتیاز
                        </p>
                        <div className="flex gap-2">
                            <button
                                onClick={() => navigate(`/manager/dashboard/salons/${salon.id}`)}
                                className="flex-1 px-3 py-2 bg-green-600 text-white rounded text-sm hover:bg-green-700"
                            >
                                مدیریت
                            </button>
                            <button
                                onClick={() => {
                                    if (confirm('آیا مطمئن هستید؟')) {
                                        deleteMutation.mutate(salon.id);
                                    }
                                }}
                                className="px-3 py-2 bg-red-600 text-white rounded text-sm hover:bg-red-700"
                            >
                                حذف
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            {salons?.length === 0 && (
                <div className="text-center py-12 text-gray-500">
                    شما هنوز سالنی ندارید. برای شروع یک سالن جدید ایجاد کنید.
                </div>
            )}

            {/* Create Salon Modal */}
            {showCreateModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-6 max-w-md w-full">
                        <h3 className="text-xl font-bold mb-4">ایجاد سالن جدید</h3>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium mb-1">نام سالن</label>
                                <input
                                    type="text"
                                    value={newSalon.name}
                                    onChange={(e) => setNewSalon({ ...newSalon, name: e.target.value })}
                                    className="w-full border rounded px-3 py-2"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">آدرس</label>
                                <input
                                    type="text"
                                    value={newSalon.address}
                                    onChange={(e) => setNewSalon({ ...newSalon, address: e.target.value })}
                                    className="w-full border rounded px-3 py-2"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">نوع سالن</label>
                                <select
                                    value={newSalon.gender_type}
                                    onChange={(e) => setNewSalon({ ...newSalon, gender_type: e.target.value as 'male' | 'female' })}
                                    className="w-full border rounded px-3 py-2"
                                >
                                    <option value="male">آقایان</option>
                                    <option value="female">بانوان</option>
                                </select>
                            </div>
                        </div>
                        <div className="flex gap-2 mt-6">
                            <button
                                onClick={() => createMutation.mutate(newSalon)}
                                disabled={!newSalon.name || !newSalon.address || createMutation.isPending}
                                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                            >
                                {createMutation.isPending ? 'در حال ایجاد...' : 'ایجاد'}
                            </button>
                            <button
                                onClick={() => setShowCreateModal(false)}
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

export default SalonList;
