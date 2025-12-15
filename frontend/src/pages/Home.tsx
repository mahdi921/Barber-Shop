import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { salonApi } from '../api/salons';
import SalonCard from '../components/salons/SalonCard';
import { useAuth } from '../hooks/useAuth';
import Button from '../components/ui/Button';
import { Link } from 'react-router-dom';

const Home: React.FC = () => {
    const { user, isAuthenticated } = useAuth();
    const { data: salons, isLoading, error } = useQuery({
        queryKey: ['salons', 'list'],
        queryFn: salonApi.getAll,
    });

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header / Hero */}
            <div className="bg-slate-900 text-white py-12 px-4 shadow-lg">
                <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center">
                    <div className="mb-6 md:mb-0">
                        <h1 className="text-4xl font-bold mb-2">رزرو آنلاین آرایشگاه</h1>
                        <p className="text-gray-300 text-lg">بهترین سالن‌های زیبایی در اطراف شما</p>
                    </div>
                    <div>
                        {/* Simple Auth State Display */}
                        {isAuthenticated && user ? (
                            <div className="text-left md:text-right">
                                <p className="font-medium">سلام، {user.user_type === 'customer' ? user.customer_profile?.full_name : user.phone_number}</p>
                                <Link to="/dashboard" className="text-blue-400 hover:text-blue-300 text-sm">ورود به پنل کاربری &larr;</Link>
                            </div>
                        ) : (
                            <div className="space-x-2 space-x-reverse">
                                <Link to="/login">
                                    <Button variant="primary" className="inline-flex w-auto px-6">ورود / ثبت‌نام</Button>
                                </Link>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {isLoading ? (
                    <div className="text-center py-20 text-gray-500">در حال بارگذاری سالن‌ها...</div>
                ) : error ? (
                    <div className="text-center py-20 text-red-500">
                        خطا در بارگذاری لیست سالن‌ها. لطفاً دوباره تلاش کنید.
                    </div>
                ) : (
                    <>
                        <div className="mb-6">
                            <h2 className="text-2xl font-bold text-gray-800">سالن‌های برگزیده</h2>
                        </div>

                        {salons && salons.length > 0 ? (
                            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                                {salons.map((salon) => (
                                    <SalonCard key={salon.id} salon={salon} />
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
                                <p className="text-gray-500 text-lg">هنوز هیچ سالنی ثبت نشده یا با فیلتر شما همخوانی ندارد.</p>
                            </div>
                        )}
                    </>
                )}
            </main>

            {/* Footer Stub */}
            <footer className="bg-gray-800 text-gray-400 py-6 text-center mt-auto">
                <p>&copy; 1403 سیستم رزرو آنلاین. طراحی شده با ❤️</p>
            </footer>
        </div>
    );
};

export default Home;
