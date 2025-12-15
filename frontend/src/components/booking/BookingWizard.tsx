import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import type { Salon, Stylist } from '../../types/salon';
import ServiceSelection from './ServiceSelection';
import JalaliDatePicker from './JalaliDatePicker';
import TimeSlotPicker from './TimeSlotPicker';
import Button from '../ui/Button';
import { appointmentApi } from '../../api/appointments';
import { useNavigate } from 'react-router-dom';

interface BookingWizardProps {
    salon: Salon;
}

const BookingWizard: React.FC<BookingWizardProps> = ({ salon }) => {
    const navigate = useNavigate();
    const [step, setStep] = useState(1);
    const [selectedServiceId, setSelectedServiceId] = useState<number | null>(null);
    const [selectedStylistId, setSelectedStylistId] = useState<number | null>(null);
    const [selectedDate, setSelectedDate] = useState<string | null>(null);
    const [selectedTime, setSelectedTime] = useState<string | null>(null);

    const selectedService = salon.services.find(s => s.id === selectedServiceId);

    // Fetch availability when date/stylist changes
    const { data: availabilityData, isLoading: isLoadingSlots } = useQuery({
        queryKey: ['availability', selectedStylistId, selectedDate],
        queryFn: () => appointmentApi.getAvailability(selectedStylistId!, selectedDate!),
        enabled: step === 3 && !!selectedStylistId && !!selectedDate,
    });

    // Booking Mutation
    const bookingMutation = useMutation({
        mutationFn: appointmentApi.bookAppointment,
        onSuccess: () => {
            alert('نوبت شما با موفقیت ثبت شد!');
            navigate('/dashboard');
        },
        onError: (err: any) => {
            alert('خطا در ثبت نوبت: ' + (err.response?.data?.error || err.message));
        }
    });

    const handleNext = () => {
        if (step === 1 && selectedService) {
            // If service is tied to a stylist, auto-select
            if (selectedService.stylist) {
                setSelectedStylistId(selectedService.stylist);
                setStep(3); // Skip stylist selection
            } else {
                setStep(2); // Go to stylist selection
            }
        } else {
            setStep(prev => prev + 1);
        }
    };

    const handleConfirm = () => {
        if (selectedStylistId && selectedServiceId && selectedDate && selectedTime) {
            bookingMutation.mutate({
                stylist_id: selectedStylistId,
                service_id: selectedServiceId,
                jalali_date: selectedDate,
                time_slot: selectedTime
            });
        }
    };

    return (
        <div className="bg-white rounded-lg shadow p-6">
            <div className="mb-6">
                <div className="flex items-center justify-between text-sm text-gray-500 mb-2">
                    <span>انتخاب خدمت</span>
                    <span>انتخاب زمان</span>
                    <span>تایید</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                    <div className="bg-blue-600 h-2.5 rounded-full" style={{ width: `${(step / 3) * 100}%` }}></div>
                </div>
            </div>

            <div className="min-h-[300px]">
                {step === 1 && (
                    <ServiceSelection
                        services={salon.services}
                        selectedServices={selectedServiceId ? [selectedServiceId] : []}
                        onToggleService={(id) => setSelectedServiceId(id)}
                    />
                )}

                {step === 2 && (
                    <div>
                        <h3 className="text-lg font-medium mb-4">انتخاب آرایشگر</h3>
                        <div className="grid grid-cols-1 gap-4">
                            {salon.stylists.map((stylist: Stylist) => (
                                <div
                                    key={stylist.id}
                                    onClick={() => setSelectedStylistId(stylist.id)}
                                    className={`p-4 border rounded cursor-pointer flex justify-between items-center ${selectedStylistId === stylist.id ? 'border-blue-500 bg-blue-50' : 'hover:border-gray-400'}`}
                                >
                                    <span className="font-medium">{stylist.full_name}</span>
                                    {selectedStylistId === stylist.id && <span className="text-blue-600">✓</span>}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {step === 3 && (
                    <div className="space-y-6">
                        <JalaliDatePicker
                            value={selectedDate}
                            onChange={setSelectedDate}
                        />

                        {selectedDate && (
                            <TimeSlotPicker
                                slots={availabilityData?.available_slots || []}
                                selectedSlot={selectedTime}
                                onSelectSlot={setSelectedTime}
                                isLoading={isLoadingSlots}
                            />
                        )}
                    </div>
                )}
            </div>

            <div className="mt-8 flex justify-between">
                {step > 1 && (
                    <Button variant="outline" onClick={() => setStep(prev => prev - 1)} className="w-auto">
                        بازگشت
                    </Button>
                )}

                <div className="mr-auto">
                    {step < 3 ? (
                        <Button
                            onClick={handleNext}
                            disabled={
                                (step === 1 && !selectedServiceId) ||
                                (step === 2 && !selectedStylistId)
                            }
                            className="w-auto px-8"
                        >
                            مرحله بعد
                        </Button>
                    ) : (
                        <Button
                            onClick={handleConfirm}
                            disabled={!selectedTime || bookingMutation.isPending}
                            isLoading={bookingMutation.isPending}
                            className="w-auto px-8"
                        >
                            تایید و رزرو
                        </Button>
                    )}
                </div>
            </div>
        </div>
    );
};

export default BookingWizard;
