import React from 'react';
import DatePicker, { DateObject } from 'react-multi-date-picker';
import persian from 'react-date-object/calendars/persian';
import persian_fa from 'react-date-object/locales/persian_fa';
import 'react-multi-date-picker/styles/layouts/mobile.css';

// Input component for the DatePicker
const CustomInput = ({ openCalendar, value }: any) => {
    return (
        <div
            onClick={openCalendar}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm cursor-pointer hover:border-blue-400 flex items-center justify-between bg-white"
        >
            <span className={value ? 'text-gray-900' : 'text-gray-400'}>
                {value || 'انتخاب تاریخ...'}
            </span>
            <svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
        </div>
    );
};

interface JalaliDatePickerProps {
    value: string | null; // Expect format YYYY/MM/DD (Persian)
    onChange: (date: string) => void;
    minDate?: Date | string | number;
}

const JalaliDatePicker: React.FC<JalaliDatePickerProps> = ({ value, onChange, minDate = new Date() }) => {

    const handleChange = (date: DateObject | null) => {
        if (date) {
            // Format to YYYY/MM/DD with Persian digits but we want correct API string format
            // Backend expects "1402/09/20" as string. DateObject with persian calendar handles this naturally.
            // We use english logical format for string transmission if needed, but the requirement said 
            // string "YYYY/MM/DD".
            const shamsiString = date.format('YYYY/MM/DD');
            onChange(shamsiString);
        }
    };

    return (
        <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
                تاریخ نوبت
            </label>
            <DatePicker
                value={value}
                onChange={handleChange}
                calendar={persian}
                locale={persian_fa}
                calendarPosition="bottom-right"
                inputClass="custom-input"
                render={<CustomInput />}
                minDate={minDate}
                containerClassName="w-full"
                style={{ fontFamily: 'Vazirmatn' }}
            />
            <p className="text-xs text-gray-500 mt-1">سال / ماه / روز</p>
        </div>
    );
};

export default JalaliDatePicker;
