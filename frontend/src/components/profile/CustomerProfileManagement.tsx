import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../../hooks/useAuth';
import { profileApi } from '../../api/profile';
import TelegramSetupCard from './TelegramSetupCard';

const CustomerProfileManagement: React.FC = () => {
    const { user } = useAuth();
    const queryClient = useQueryClient();

    const customerProfile = user?.customer_profile;
    const [isEditing, setIsEditing] = useState(false);
    const [formData, setFormData] = useState({
        first_name: customerProfile?.first_name || '',
        last_name: customerProfile?.last_name || '',
    });

    const updateMutation = useMutation({
        mutationFn: (data: typeof formData) => profileApi.updateCustomerProfile(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['auth', 'me'] });
            setIsEditing(false);
            alert('✅ پروفایل با موفقیت بهروزرسانی شد');
        },
        onError: (error: any) => {
            const errorMessage = error?.response?.data?.error || 'خطا در بهروزرسانی پروفایل';
            alert(`❌ ${errorMessage}`);
        },
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        updateMutation.mutate(formData);
    };

    if (!customerProfile) {
        return <div className="text-center text-gray-500">در حال بارگزاری...</div>;
    }

    return (
        <div className="space-y-6">
            {/* Telegram Setup Card */}
            <TelegramSetupCard
                hasTelegramLinked={!!user?.customer_profile?.telegram_chat_id}
                userPhone={user?.phone_number}
            />

            {/* Profile Information Card */}
            <div className="bg-white rounded-xl shadow-md overflow-hidden">
                <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-4 flex justify-between items-center">
                    <h2 className="text-xl font-bold text-white">اطلاعات پروفایل</h2>
                    {!isEditing && (
                        <button
                            onClick={() => setIsEditing(true)}
                            className="bg-white text-indigo-600 px-4 py-2 rounded-lg font-medium hover:bg-gray-100 transition-colors text-sm"
                        >
                            ✏️ ویرایش
                        </button>
                    )}
                </div>

                <div className="p-6">
                    {isEditing ? (
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        نام
                                    </label>
                                    <input
                                        type="text"
                                        value={formData.first_name}
                                        onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                                        className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        نام خانوادگی
                                    </label>
                                    <input
                                        type="text"
                                        value={formData.last_name}
                                        onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                                        className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                                        required
                                    />
                                </div>
                            </div>



                            <div className="flex gap-3 pt-4">
                                <button
                                    type="submit"
                                    disabled={updateMutation.isPending}
                                    className="flex-1 bg-indigo-600 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50"
                                >
                                    {updateMutation.isPending ? 'در حال ذخیره...' : '💾 ذخیره تغییرات'}
                                </button>
                                <button
                                    type="button"
                                    onClick={() => {
                                        setIsEditing(false);
                                        setFormData({
                                            first_name: customerProfile.first_name || '',
                                            last_name: customerProfile.last_name || '',
                                        });
                                    }}
                                    className="px-6 py-2.5 border border-gray-300 rounded-lg font-medium hover:bg-gray-50 transition-colors"
                                >
                                    انصراف
                                </button>
                            </div>
                        </form>
                    ) : (
                        <div className="space-y-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div>
                                    <p className="text-sm font-medium text-gray-500">نام و نام خانوادگی</p>
                                    <p className="text-lg font-semibold text-gray-900 mt-1">
                                        {customerProfile.first_name} {customerProfile.last_name}
                                    </p>
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-gray-500">شماره تلفن</p>
                                    <p className="text-lg font-semibold text-gray-900 mt-1" dir="ltr">
                                        {user?.phone_number}
                                    </p>
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-gray-500">جنسیت</p>
                                    <p className="text-lg font-semibold text-gray-900 mt-1">
                                        {customerProfile.gender === 'male' ? 'مرد' : 'زن'}
                                    </p>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default CustomerProfileManagement;
