import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { adminApi } from '../../api/admin';
import type { User } from '../../types/auth'; // Ensure this type exists or use any
import EditUserModal from './EditUserModal';

const UserManagementTable: React.FC = () => {
    const queryClient = useQueryClient();
    const [page, setPage] = useState(1);
    const [userType, setUserType] = useState('');
    const [editingUser, setEditingUser] = useState<User | null>(null);

    const { data, isLoading } = useQuery({
        queryKey: ['admin', 'users', page, userType],
        queryFn: () => adminApi.getUsers(page, userType),
    });

    const updateMutation = useMutation({
        mutationFn: ({ id, data }: { id: number; data: Partial<User> }) => adminApi.updateUser(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin', 'users'] });
            setEditingUser(null);
            alert('کاربر با موفقیت ویرایش شد');
        },
        onError: () => alert('خطا در ویرایش کاربر'),
    });

    const deleteMutation = useMutation({
        mutationFn: adminApi.deleteUser,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin', 'users'] });
            alert('کاربر حذف شد');
        },
        onError: () => alert('خطا در حذف کاربر'),
    });

    const handleToggleActive = (user: User) => {
        if (confirm(`آیا از ${user.is_active ? 'غیرفعال' : 'فعال'} کردن این کاربر اطمینان دارید؟`)) {
            updateMutation.mutate({ id: user.id, data: { is_active: !user.is_active } });
        }
    };

    const handleDelete = (id: number) => {
        if (confirm('آیا از حذف این کاربر اطمینان دارید؟ این عمل غیرقابل بازگشت است.')) {
            deleteMutation.mutate(id);
        }
    };

    const handleEditClick = (user: User) => {
        setEditingUser(user);
    };

    const handleSaveEdit = (id: number, data: Partial<User>) => {
        updateMutation.mutate({ id, data });
    };

    return (
        <div>
            <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold">مدیریت کاربران</h2>
                <select
                    value={userType}
                    onChange={(e) => {
                        setPage(1);
                        setUserType(e.target.value);
                    }}
                    className="border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                >
                    <option value="">همه کاربران</option>
                    <option value="customer">مشتریان</option>
                    <option value="stylist">آرایشگران</option>
                    <option value="salon_manager">مدیران سالن</option>
                </select>
            </div>

            {isLoading ? (
                <div className="text-center p-4">در حال بارگزاری...</div>
            ) : (
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">نام کاربر</th>
                                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">شماره تلفن</th>
                                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">نوع کاربر</th>
                                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">وضعیت</th>
                                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">عملیات</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {data?.results.map((user) => (
                                <tr key={user.id}>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                        {user.user_type === 'customer' ? user.customer_profile?.full_name :
                                            user.user_type === 'stylist' ? user.stylist_profile?.full_name :
                                                user.user_type === 'salon_manager' ? user.manager_profile?.salon_name : 'ناشناس'}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500" dir="ltr">{user.phone_number}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {user.user_type === 'customer' ? 'مشتری' :
                                            user.user_type === 'stylist' ? 'آرایشگر' :
                                                user.user_type === 'salon_manager' ? 'مدیر سالن' : 'ادمین'}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                            {user.is_active ? 'فعال' : 'غیرفعال'}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium flex gap-2">
                                        <button
                                            onClick={() => handleEditClick(user)}
                                            className="text-blue-600 hover:text-blue-900"
                                        >
                                            ویرایش
                                        </button>
                                        <span className="text-gray-300">|</span>
                                        <button
                                            onClick={() => handleToggleActive(user)}
                                            className={`${user.is_active ? 'text-yellow-600 hover:text-yellow-900' : 'text-green-600 hover:text-green-900'}`}
                                        >
                                            {user.is_active ? 'غیرفعال' : 'فعال'}
                                        </button>
                                        <span className="text-gray-300">|</span>
                                        <button
                                            onClick={() => handleDelete(user.id)}
                                            className="text-red-600 hover:text-red-900"
                                        >
                                            حذف
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>

                    <div className="py-3 flex items-center justify-between border-t border-gray-200">
                        <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                            <div>
                                <p className="text-sm text-gray-700">
                                    نمایش صفحه <span className="font-medium">{page}</span>
                                </p>
                            </div>
                            <div>
                                <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                                    <button
                                        onClick={() => setPage(p => Math.max(1, p - 1))}
                                        disabled={!data?.previous}
                                        className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:bg-gray-100"
                                    >
                                        قبلی
                                    </button>
                                    <button
                                        onClick={() => setPage(p => p + 1)}
                                        disabled={!data?.next}
                                        className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:bg-gray-100"
                                    >
                                        بعدی
                                    </button>
                                </nav>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            <EditUserModal
                user={editingUser}
                isOpen={!!editingUser}
                onClose={() => setEditingUser(null)}
                onSave={handleSaveEdit}
                isLoading={updateMutation.isPending}
            />
        </div>
    );
};

export default UserManagementTable;
