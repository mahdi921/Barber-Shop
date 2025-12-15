import React from 'react';

interface TimeSlotPickerProps {
    slots: string[];
    selectedSlot: string | null;
    onSelectSlot: (slot: string) => void;
    isLoading?: boolean;
}

const TimeSlotPicker: React.FC<TimeSlotPickerProps> = ({
    slots,
    selectedSlot,
    onSelectSlot,
    isLoading
}) => {
    if (isLoading) {
        return <div className="text-gray-500 text-sm">در حال دریافت ساعت‌های خالی...</div>;
    }

    if (slots.length === 0) {
        return (
            <div className="text-red-500 text-sm bg-red-50 p-3 rounded">
                هیچ ساعت خالی برای این روز موجود نیست.
            </div>
        );
    }

    return (
        <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
                ساعت مراجعه
            </label>
            <div className="grid grid-cols-4 gap-2">
                {slots.map((slot) => (
                    <button
                        key={slot}
                        type="button"
                        onClick={() => onSelectSlot(slot)}
                        className={`
               px-3 py-2 text-sm font-medium rounded-md border focus:outline-none focus:ring-2 focus:ring-offset-2
               ${selectedSlot === slot
                                ? 'bg-blue-600 text-white border-transparent ring-blue-500'
                                : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'}
             `}
                    >
                        {slot}
                    </button>
                ))}
            </div>
        </div>
    );
};

export default TimeSlotPicker;
