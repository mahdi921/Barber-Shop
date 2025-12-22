import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { managerApi, type WorkingHours } from '../../api/manager';
import Button from '../ui/Button';
import Modal from '../ui/Modal';

const WEEKDAYS = [
    { value: 0, label: 'شنبه' },
    { value: 1, label: 'یکشنبه' },
    { value: 2, label: 'دوشنبه' },
    { value: 3, label: 'سه‌شنبه' },
    { value: 4, label: 'چهارشنبه' },
    { value: 5, label: 'پنج‌شنبه' },
    { value: 6, label: 'جمعه' },
];

const WorkingHoursManagement: React.FC = () => {
    const queryClient = useQueryClient();
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedDays, setSelectedDays] = useState<number[]>([]);
    const [startTime, setStartTime] = useState('09:00');
    const [endTime, setEndTime] = useState('18:00');

    const { data: workingHours, isLoading } = useQuery({
        queryKey: ['manager', 'working-hours'],
        queryFn: managerApi.getWorkingHours,
    });

    const createMutation = useMutation({
        mutationFn: managerApi.createWorkingHours,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['manager', 'working-hours'] });
        },
        onError: () => alert('خطا در افزودن ساعت کاری'),
    });

    const deleteMutation = useMutation({
        mutationFn: managerApi.deleteWorkingHours,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['manager', 'working-hours'] });
            alert('ساعت کاری حذف شد');
        },
        onError: () => alert('خطا در حذف ساعت کاری'),
    });

    const handleDayToggle = (day: number) => {
        setSelectedDays(prev =>
            prev.includes(day) ? prev.filter(d => d !== day) : [...prev, day]
        );
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (selectedDays.length === 0) {
            alert('لطفاً حداقل یک روز انتخاب کنید');
            return;
        }

        // Create working hours for each selected day
        for (const day of selectedDays) {
            await createMutation.mutateAsync({
                day_of_week: day,
                start_time: startTime,
                end_time: endTime,
                is_active: true,
            });
        }

        setIsModalOpen(false);
        setSelectedDays([]);
        setStartTime('09:00');
        setEndTime('18:00');
        alert('ساعات کاری با موفقیت افزوده شد');
    };

    const handleDelete = (id: number) => {
        if (confirm('آیا از حذف این ساعت کاری اطمینان دارید؟')) {
            deleteMutation.mutate(id);
        }
    };

    const groupedByDay: { [key: number]: WorkingHours[] } = {};
    workingHours?.forEach(wh => {
        if (!groupedByDay[wh.day_of_week]) {
            groupedByDay[wh.day_of_week] = [];
        }
        groupedByDay[wh.day_of_week].push(wh);
    });

    return (
        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
            <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
                <div>
                    <h3 className="text-lg leading-6 font-medium text-gray-900">ساعات کاری</h3>
                    <p className="mt-1 max-w-2xl text-sm text-gray-500">روزها و ساعات کاری سالن</p>
                </div>
                <Button onClick={() => setIsModalOpen(true)}>افزودن ساعت کاری</Button>
            </div>
            <div className="border-t border-gray-200">
                {isLoading ? (
                    <div className="p-6 text-center">در حال بارگزاری...</div>
                ) : workingHours && workingHours.length > 0 ? (
                    <div className="p-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {WEEKDAYS.map(day => (
                                <div key={day.value} className="border rounded-lg p-4">
                                    <h4 className="font-medium text-gray-900 mb-2">{day.label}</h4>
                                    {groupedByDay[day.value] && groupedByDay[day.value].length > 0 ? (
                                        <div className="space-y-2">
                                            {groupedByDay[day.value].map((wh: WorkingHours) => (
                                                <div key={wh.id} className="flex justify-between items-center text-sm">
                                                    <span dir="ltr" className="text-gray-600">{wh.start_time} - {wh.end_time}</span>
                                                    <button
                                                        onClick={() => handleDelete(wh.id)}
                                                        className="text-red-600 hover:text-red-900"
                                                    >
                                                        حذف
                                                    </button>
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <p className="text-sm text-gray-500">تعطیل</p>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                ) : (
                    <div className="p-6 text-center text-gray-500">هیچ ساعت کاری ثبت نشده است</div>
                )}
            </div>

            <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="افزودن ساعت کاری" size="lg">
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">انتخاب روزها (چند انتخابی)</label>
                        <div className="grid grid-cols-2 gap-2">
                            {WEEKDAYS.map(day => (
                                <label key={day.value} className="flex items-center p-2 border rounded cursor-pointer hover:bg-gray-50">
                                    <input
                                        type="checkbox"
                                        checked={selectedDays.includes(day.value)}
                                        onChange={() => handleDayToggle(day.value)}
                                        className="h-4 w-4 text-blue-600 rounded"
                                    />
                                    <span className="mr-2 text-sm">{day.label}</span>
                                </label>
                            ))}
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">ساعت شروع</label>
                            <input
                                type="time"
                                value={startTime}
                                onChange={(e) => setStartTime(e.target.value)}
                                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700">ساعت پایان</label>
                            <input
                                type="time"
                                value={endTime}
                                onChange={(e) => setEndTime(e.target.value)}
                                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
                                required
                            />
                        </div>
                    </div>

                    <div className="flex flex-row-reverse gap-2">
                        <Button type="submit" isLoading={createMutation.isPending}>
                            افزودن
                        </Button>
                        <Button type="button" variant="secondary" onClick={() => setIsModalOpen(false)}>
                            انصراف
                        </Button>
                    </div>
                </form>
            </Modal>
        </div>
    );
};

export default WorkingHoursManagement;
