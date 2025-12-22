import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';

// Validation schema
const loginSchema = z.object({
    phone_number: z.string().min(11, 'شماره تلفن باید ۱۱ رقم باشد').max(11, 'شماره تلفن باید ۱۱ رقم باشد'),
    password: z.string().min(8, 'رمز عبور باید حداقل ۸ کاراکتر باشد'),
});

type LoginFormData = z.infer<typeof loginSchema>;

const Login: React.FC = () => {
    const { login, isLoggingIn, isLoginError } = useAuth();

    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<LoginFormData>({
        resolver: zodResolver(loginSchema),
    });

    const onSubmit = (data: LoginFormData) => {
        login(data);
    };

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
            <div className="sm:mx-auto sm:w-full sm:max-w-md">
                <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
                    ورود به حساب کاربری
                </h2>
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
                            dir="ltr" // Phone numbers are LTR
                        />

                        <Input
                            label="رمز عبور"
                            type="password"
                            {...register('password')}
                            error={errors.password?.message}
                        />

                        {isLoginError && (
                            <div className="rounded-md bg-red-50 p-4">
                                <div className="flex">
                                    <div className="ml-3">
                                        <h3 className="text-sm font-medium text-red-800">
                                            خطا در ورود
                                        </h3>
                                        <div className="mt-2 text-sm text-red-700">
                                            <p>شماره تلفن یا رمز عبور اشتباه است.</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        <div>
                            <Button type="submit" isLoading={isLoggingIn}>
                                ورود
                            </Button>
                        </div>
                    </form>

                    <div className="mt-6">
                        <div className="relative">
                            <div className="absolute inset-0 flex items-center">
                                <div className="w-full border-t border-gray-300" />
                            </div>
                            <div className="relative flex justify-center text-sm">
                                <span className="px-2 bg-white text-gray-500">
                                    حساب کاربری ندارید؟
                                </span>
                            </div>
                        </div>

                        <div className="mt-6 grid grid-cols-1 gap-3">
                            <Link
                                to="/register/customer"
                                className="w-full inline-flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50"
                            >
                                ثبت‌نام مشتری
                            </Link>
                            <Link
                                to="/register/manager"
                                className="w-full inline-flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50"
                            >
                                ثبت‌نام مدیر سالن
                            </Link>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Login;

