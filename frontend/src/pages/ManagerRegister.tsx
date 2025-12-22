import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useNavigate } from 'react-router-dom';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';

// Validation schema
const managerRegisterSchema = z.object({
    phone_number: z.string()
        .min(11, 'شماره تلفن باید ۱۱ رقم باشد')
        .max(11, 'شماره تلفن باید ۱۱ رقم باشد')
        .regex(/^09[0-9]{9}$/, 'شماره تلفن باید با ۰۹ شروع شود'),
    password: z.string().min(8, 'رمز عبور باید حداقل ۸ کاراکتر باشد'),
    confirm_password: z.string(),
    salon_name: z.string().min(2, 'نام سالن باید حداقل ۲ کاراکتر باشد'),
    salon_address: z.string().min(10, 'آدرس باید حداقل ۱۰ کاراکتر باشد'),
    salon_gender_type: z.enum(['male', 'female'], { required_error: 'انتخاب نوع سالن الزامی است' }),
    salon_photo: z.any(),
}).refine((data) => data.password === data.confirm_password, {
    message: 'رمز عبور و تکرار آن باید یکسان باشند',
    path: ['confirm_password'],
});

type ManagerRegisterFormData = z.infer<typeof managerRegisterSchema>;

const ManagerRegister: React.FC = () => {
    const navigate = useNavigate();
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [selectedFile, setSelectedFile] = useState<File | null>(null);

    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<ManagerRegisterFormData>({
        resolver: zodResolver(managerRegisterSchema),
    });

    const onSubmit = async (data: ManagerRegisterFormData) => {
        setIsSubmitting(true);
        setError(null);

        try {
            const formData = new FormData();
            formData.append('phone_number', data.phone_number);
            formData.append('password', data.password);
            formData.append('salon_name', data.salon_name);
            formData.append('salon_address', data.salon_address);
            formData.append('salon_gender_type', data.salon_gender_type);

            if (selectedFile) {
                formData.append('salon_photo', selectedFile);
            }

            const response = await fetch('http://localhost:8000/accounts/api/register/manager/', {
                method: 'POST',
                body: formData,
            });

            const result = await response.json();

            if (response.ok) {
                alert('ثبت‌نام با موفقیت انجام شد! حساب شما در انتظار تأیید مدیر سایت است.');
                navigate('/login');
            } else {
                setError(result.error || 'خطا در ثبت‌نام. لطفاً دوباره تلاش کنید.');
            }
        } catch (err) {
            setError('خطا در ارتباط با سرور. لطفاً دوباره تلاش کنید.');
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setSelectedFile(e.target.files[0]);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
            <div className="sm:mx-auto sm:w-full sm:max-w-md">
                <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
                    ثبت‌نام مدیر سالن
                </h2>
                <p className="mt-2 text-center text-sm text-gray-600">
                    از قبل حساب کاربری دارید؟{' '}
                    <Link to="/login" className="font-medium text-indigo-600 hover:text-indigo-500">
                        ورود به حساب
                    </Link>
                </p>
                <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-md">
                    <p className="text-sm text-yellow-800 text-center">
                        ⚠️ حساب شما پس از ثبت‌نام نیاز به تأیید مدیر سایت دارد
                    </p>
                </div>
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
                            label="نام سالن"
                            type="text"
                            placeholder="آرایشگاه مدرن"
                            {...register('salon_name')}
                            error={errors.salon_name?.message}
                        />

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                آدرس سالن
                            </label>
                            <textarea
                                {...register('salon_address')}
                                rows={3}
                                className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md p-2 border"
                                placeholder="تهران، خیابان ولیعصر، پلاک ۱۲۳"
                            />
                            {errors.salon_address && (
                                <p className="mt-1 text-sm text-red-600">{errors.salon_address.message}</p>
                            )}
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                نوع سالن
                            </label>
                            <div className="flex gap-4">
                                <label className="flex items-center">
                                    <input
                                        type="radio"
                                        value="male"
                                        {...register('salon_gender_type')}
                                        className="ml-2"
                                    />
                                    مردانه
                                </label>
                                <label className="flex items-center">
                                    <input
                                        type="radio"
                                        value="female"
                                        {...register('salon_gender_type')}
                                        className="ml-2"
                                    />
                                    زنانه
                                </label>
                            </div>
                            {errors.salon_gender_type && (
                                <p className="mt-1 text-sm text-red-600">{errors.salon_gender_type.message}</p>
                            )}
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                عکس سالن
                            </label>
                            <input
                                type="file"
                                accept="image/*"
                                onChange={handleFileChange}
                                className="block w-full text-sm text-gray-500
                                    file:ml-4 file:py-2 file:px-4
                                    file:rounded-md file:border-0
                                    file:text-sm file:font-semibold
                                    file:bg-indigo-50 file:text-indigo-700
                                    hover:file:bg-indigo-100"
                            />
                            {selectedFile && (
                                <p className="mt-2 text-sm text-gray-600">
                                    فایل انتخاب شده: {selectedFile.name}
                                </p>
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
                            {...register('confirm_password')}
                            error={errors.confirm_password?.message}
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
    );
};

export default ManagerRegister;
