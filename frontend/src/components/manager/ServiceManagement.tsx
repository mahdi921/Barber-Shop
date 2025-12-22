import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { managerApi, type Service } from '../../api/manager';
import Button from '../ui/Button';
import Modal from '../ui/Modal';

interface ServiceManagementProps {
    salonGenderType: 'male' | 'female';
}

const ServiceManagement: React.FC<ServiceManagementProps> = ({ salonGenderType }) => {
    const queryClient = useQueryClient();
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingService, setEditingService] = useState<Service | null>(null);
    const [formData, setFormData] = useState({
        service_type: '',
        custom_name: '',
        price: 0,
        duration_minutes: 30,
        is_active: true,
    });

    const { data: services, isLoading } = useQuery({
        queryKey: ['manager', 'services'],
        queryFn: managerApi.getServices,
    });

    const createMutation = useMutation({
        mutationFn: managerApi.createService,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['manager', 'services'] });
            setIsModalOpen(false);
            resetForm();
            alert('خدمت با موفقیت اضافه شد');
        },
        onError: () => alert('خطا در افزودن خدمت'),
    });

    const updateMutation = useMutation({
        mutationFn: ({ id, data }: { id: number; data: Partial<Service> }) =>
            managerApi.updateService(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['manager', 'services'] });
            setIsModalOpen(false);
            setEditingService(null);
            resetForm();
            alert('خدمت با موفقیت ویرایش شد');
        },
        onError: () => alert('خطا در ویرایش خدمت'),
    });

    const deleteMutation = useMutation({
        mutationFn: managerApi.deleteService,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['manager', 'services'] });
            alert('خدمت حذف شد');
        },
        onError: () => alert('خطا در حذف خدمت'),
    });

    const serviceTypes = salonGenderType === 'male'
        ? [
            { value: 'haircut', label: 'کوتاهی مو' },
            { value: 'shave', label: 'اصلاح' },
            { value: 'beard_trim', label: 'اصلاح ریش' },
            { value: 'facial', label: 'مراقبت از پوست' },
        ]
        : [
            { value: 'haircut', label: 'کوتاهی مو' },
            { value: 'hair_color', label: 'رنگ مو' },
            { value: 'nails', label: 'خدمات ناخن' },
            { value: 'makeup', label: 'آرایش' },
            { value: 'eyelashes', label: 'خدمات مژه' },
            { value: 'lips', label: 'خدمات لب' },
            { value: 'piercing', label: 'سوراخ کردن' },
            { value: 'facial', label: 'مراقبت از پوست' },
            { value: 'facial_hair', label: 'اصلاح ابرو و صورت' },
        ];

    const resetForm = () => {
        setFormData({
            service_type: '',
            custom_name: '',
            price: 0,
            duration_minutes: 30,
            is_active: true,
        });
        setEditingService(null);
    };

    const handleAdd = () => {
        resetForm();
        setIsModalOpen(true);
    };

    const handleEdit = (service: Service) => {
        setEditingService(service);
        setFormData({
            service_type: service.service_type,
            custom_name: service.custom_name || '',
            price: service.price,
            duration_minutes: service.duration_minutes,
            is_active: service.is_active,
        });
        setIsModalOpen(true);
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (editingService) {
            updateMutation.mutate({ id: editingService.id, data: formData });
        } else {
            createMutation.mutate(formData);
        }
    };

    const handleDelete = (id: number) => {
        if (confirm('آیا از حذف این خدمت اطمینان دارید؟')) {
            deleteMutation.mutate(id);
        }
    };

    return (
        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
            <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
                <div>
                    <h3 className="text-lg leading-6 font-medium text-gray-900">مدیریت خدمات</h3>
                    <p className="mt-1 max-w-2xl text-sm text-gray-500">خدمات ارائه شده توسط سالن</p>
                </div>
                <Button onClick={handleAdd}>افزودن خدمت جدید</Button>
            </div>
            <div className="border-t border-gray-200">
                {isLoading ? (
                    <div className="p-6 text-center">در حال بارگزاری...</div>
                ) : services && services.length > 0 ? (
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">نوع خدمت</th>
                                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">نام سفارشی</th>
                                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">قیمت (تومان)</th>
                                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">مدت (دقیقه)</th>
                                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">وضعیت</th>
                                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">عملیات</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {services.map((service: Service) => (
                                <tr key={service.id}>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm">{service.service_type_display}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm">{service.custom_name || '-'}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm" dir="ltr">{service.price.toLocaleString()}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm">{service.duration_minutes}</td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${service.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                                            {service.is_active ? 'فعال' : 'غیرفعال'}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                        <button onClick={() => handleEdit(service)} className="text-blue-600 hover:text-blue-900 ml-4">ویرایش</button>
                                        <button onClick={() => handleDelete(service.id)} className="text-red-600 hover:text-red-900">حذف</button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                ) : (
                    <div className="p-6 text-center text-gray-500">هیچ خدمتی ثبت نشده است</div>
                )}
            </div>

            <Modal isOpen={isModalOpen} onClose={() => { setIsModalOpen(false); resetForm(); }} title={editingService ? 'ویرایش خدمت' : 'افزودن خدمت جدید'}>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700">نوع خدمت</label>
                        <select
                            value={formData.service_type}
                            onChange={(e) => setFormData({ ...formData, service_type: e.target.value })}
                            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
                            required
                        >
                            <option value="">انتخاب کنید</option>
                            {serviceTypes.map((type) => (
                                <option key={type.value} value={type.value}>{type.label}</option>
                            ))}
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700">نام سفارشی (اختیاری)</label>
                        <input
                            type="text"
                            value={formData.custom_name}
                            onChange={(e) => setFormData({ ...formData, custom_name: e.target.value })}
                            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700">قیمت (تومان)</label>
                        <input
                            type="number"
                            value={formData.price}
                            onChange={(e) => setFormData({ ...formData, price: parseInt(e.target.value) || 0 })}
                            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
                            required
                            min="0"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700">مدت زمان (دقیقه)</label>
                        <input
                            type="number"
                            value={formData.duration_minutes}
                            onChange={(e) => setFormData({ ...formData, duration_minutes: parseInt(e.target.value) || 30 })}
                            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
                            required
                            min="15"
                            step="15"
                        />
                    </div>

                    <div className="flex items-center">
                        <input
                            type="checkbox"
                            checked={formData.is_active}
                            onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                            className="h-4 w-4 text-blue-600 rounded"
                        />
                        <label className="mr-2 block text-sm text-gray-900">خدمت فعال است</label>
                    </div>

                    <div className="flex flex-row-reverse gap-2">
                        <Button type="submit" isLoading={createMutation.isPending || updateMutation.isPending}>
                            {editingService ? 'ذخیره تغییرات' : 'افزودن'}
                        </Button>
                        <Button type="button" variant="secondary" onClick={() => { setIsModalOpen(false); resetForm(); }}>
                            انصراف
                        </Button>
                    </div>
                </form>
            </Modal>
        </div>
    );
};

export default ServiceManagement;
