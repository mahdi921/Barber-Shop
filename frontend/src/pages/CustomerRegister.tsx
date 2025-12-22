import React, { useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useNavigate } from 'react-router-dom';
import DatePicker from 'react-multi-date-picker';
import persian from 'react-date-object/calendars/persian';
import persian_fa from 'react-date-object/locales/persian_fa';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';

// Validation schema
const customerRegisterSchema = z.object({
    phone_number: z.string()
        .min(11, 'شماره تلفن باید ۱۱ رقم باشد')
        .max(11, 'شماره تلفن باید ۱۱ رقم باشد')
        .regex(/^09[0-9]{9}$/, 'شماره تلفن باید با ۰۹ شروع شود'),
    password: z.string().min(8, 'رمز عبور باید حداقل ۸ کاراکتر باشد'),
    password_confirm: z.string(),
    first_name: z.string().min(2, 'نام باید حداقل ۲ کاراکتر باشد'),
    last_name: z.string().min(2, 'نام خانوادگی باید حداقل ۲ کاراکتر باشد'),
    gender: z.enum(['male', 'female'], { message: 'انتخاب جنسیت الزامی است' }),
    date_of_birth: z.string().min(1, 'تاریخ تولد الزامی است'),
}).refine((data) => data.password === data.password_confirm, {
    message: 'رمز عبور و تکرار آن باید یکسان باشند',
    path: ['password_confirm'],
});

type CustomerRegisterFormData = z.infer<typeof customerRegisterSchema>;

const CustomerRegister: React.FC = () => {
    const navigate = useNavigate();
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [showTelegramModal, setShowTelegramModal] = useState(false);
    const [registeredPhone, setRegisteredPhone] = useState('');

    const {
        register,
        handleSubmit,
        control,
        formState: { errors },
    } = useForm<CustomerRegisterFormData>({
        resolver: zodResolver(customerRegisterSchema),
    });

    const onSubmit = async (data: CustomerRegisterFormData) => {
        setIsSubmitting(true);
        setError(null);

        try {
            const formData = new FormData();
            formData.append('phone_number', data.phone_number);
            formData.append('password', data.password);
            formData.append('password_confirm', data.password_confirm);
            formData.append('first_name', data.first_name);
            formData.append('last_name', data.last_name);
            formData.append('gender', data.gender);
            formData.append('date_of_birth', data.date_of_birth);

            const response = await fetch('http://localhost:8000/accounts/api/register/customer/', {
                method: 'POST',
                body: formData,
            });

            const result = await response.json();

            if (response.ok) {
                // Show Telegram bot prompt modal
                setRegisteredPhone(data.phone_number);
                setShowTelegramModal(true);
            } else {
                // Handle field-specific errors
                if (typeof result === 'object' && result !== null) {
                    const errorValues = Object.values(result);
                    if (errorValues.length > 0) {
                        const firstError = errorValues[0];
                        if (Array.isArray(firstError)) {
                            setError(firstError[0]);
                        } else if (typeof firstError === 'string') {
                            setError(firstError);
                        } else {
                            setError('خطا در داده‌های ارسالی. لطفاً موارد را بررسی کنید.');
                        }
                    } else {
                        setError('خطا در ثبت‌نام. لطفاً دوباره تلاش کنید.');
                    }
                } else {
                    setError('خطا در ثبت‌نام. لطفاً دوباره تلاش کنید.');
                }
            }
        } catch (err) {
            setError('خطا در ارتباط با سرور. لطفاً دوباره تلاش کنید.');
        } finally {
            setIsSubmitting(false);
        }
    };


    return (
        <>
            <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
                <div className="sm:mx-auto sm:w-full sm:max-w-md">
                    <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
                        ثبت‌نام مشتری
                    </h2>
                    <p className="mt-2 text-center text-sm text-gray-600">
                        از قبل حساب کاربری دارید؟{' '}
                        <Link to="/login" className="font-medium text-indigo-600 hover:text-indigo-500">
                            ورود به حساب
                        </Link>
                    </p>
                </div>

                <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
                    <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
                        <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>

                            <Input
                                label="شماره تلفن"
                                type="text"
                                placeholder="09123456789"
                                {...register('phone_number')}
                                error={errors.phone_number?.message}
                                dir="ltr"
                            />

                            <Input
                                label="نام"
                                type="text"
                                placeholder="علی"
                                {...register('first_name')}
                                error={errors.first_name?.message}
                            />

                            <Input
                                label="نام خانوادگی"
                                type="text"
                                placeholder="محمدی"
                                {...register('last_name')}
                                error={errors.last_name?.message}
                            />

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    جنسیت
                                </label>
                                <div className="mt-2 space-y-2">
                                    <label className="inline-flex items-center ml-6">
                                        <input
                                            type="radio"
                                            value="male"
                                            {...register('gender')}
                                            className="form-radio h-4 w-4 text-indigo-600"
                                        />
                                        <span className="mr-2">مرد</span>
                                    </label>
                                    <label className="inline-flex items-center">
                                        <input
                                            type="radio"
                                            value="female"
                                            {...register('gender')}
                                            className="form-radio h-4 w-4 text-indigo-600"
                                        />
                                        <span className="mr-2">زن</span>
                                    </label>
                                </div>
                                {errors.gender && (
                                    <p className="mt-1 text-sm text-red-600">{errors.gender.message}</p>
                                )}
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    تاریخ تولد (شمسی)
                                </label>
                                <Controller
                                    name="date_of_birth"
                                    control={control}
                                    render={({ field }) => (
                                        <DatePicker
                                            value={field.value || new Date()}
                                            onChange={(date) => {
                                                if (date) {
                                                    // Convert Persian date to Gregorian YYYY-MM-DD
                                                    const gregorianDate = date.toDate();
                                                    const year = gregorianDate.getFullYear();
                                                    const month = String(gregorianDate.getMonth() + 1).padStart(2, '0');
                                                    const day = String(gregorianDate.getDate()).padStart(2, '0');
                                                    field.onChange(`${year}-${month}-${day}`);
                                                }
                                            }}
                                            calendar={persian}
                                            locale={persian_fa}
                                            format="YYYY/MM/DD"
                                            placeholder="انتخاب تاریخ تولد"
                                            inputClass="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md p-2 border"
                                            containerClassName="w-full"
                                            style={{
                                                width: '100%',
                                            }}
                                            maxDate={new Date()}
                                        />
                                    )}
                                />
                                {errors.date_of_birth && (
                                    <p className="mt-1 text-sm text-red-600">{errors.date_of_birth.message}</p>
                                )}
                            </div>



                            <Input
                                label="رمز عبور"
                                type="password"
                                {...register('password')}
                                error={errors.password?.message}
                            />

                            <Input
                                label="تکرار رمز عبور"
                                type="password"
                                {...register('password_confirm')}
                                error={errors.password_confirm?.message}
                            />

                            {error && (
                                <div className="rounded-md bg-red-50 p-4">
                                    <div className="flex">
                                        <div className="ml-3">
                                            <h3 className="text-sm font-medium text-red-800">
                                                خطا در ثبت‌نام
                                            </h3>
                                            <div className="mt-2 text-sm text-red-700">
                                                <p>{error}</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}

                            <div>
                                <Button type="submit" isLoading={isSubmitting}>
                                    ثبت‌نام
                                </Button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>

            {/* Success Message with Telegram Bot Button */}
            {showTelegramModal && (
                <div className="fixed inset-0 z-50 overflow-y-auto bg-gray-900 bg-opacity-75 flex items-center justify-center p-4">
                    <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
                        <div className="text-center">
                            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100 mb-4">
                                <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                                </svg>
                            </div>
                            <h3 className="text-lg font-medium text-gray-900 mb-2">
                                ثبت‌نام با موفقیت انجام شد!
                            </h3>
                            <p className="text-sm text-gray-500 mb-6">
                                برای دریافت اعلان‌های نوبت و یادآوری‌ها، به ربات تلگرام ما متصل شوید.
                            </p>

                            <div className="space-y-3">
                                <a
                                    href={`https://t.me/BarberShopBot?start=${registeredPhone}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="w-full inline-flex justify-center items-center px-4 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                                >
                                    <span className="ml-2">🚀</span>
                                    اتصال به ربات تلگرام
                                </a>

                                <button
                                    onClick={() => navigate('/login')}
                                    className="w-full inline-flex justify-center px-4 py-2 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                                >
                                    ادامه به ورود
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
};

export default CustomerRegister;
