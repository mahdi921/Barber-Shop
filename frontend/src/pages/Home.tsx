import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { salonApi } from '../api/salons';
import SalonCard from '../components/salons/SalonCard';

const Home: React.FC = () => {
    const { data: salons, isLoading, error } = useQuery({
        queryKey: ['salons', 'list'],
        queryFn: salonApi.getAll,
    });

    return (
        <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
            {/* Hero Section */}
            <div className="relative overflow-hidden bg-gradient-to-br from-indigo-600 via-purple-700 to-indigo-800">
                <div
                    className="absolute inset-0"
                    style={{
                        backgroundImage: 'url("data:image/svg+xml,%3Csvg width=\'60\' height=\'60\' viewBox=\'0 0 60 60\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cg fill=\'none\' fill-rule=\'evenodd\'%3E%3Cg fill=\'%23ffffff\' fill-opacity=\'0.05\'%3E%3Cpath d=\'M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z\'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")',
                    }}
                />

                <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
                    <div className="text-center">
                        <h1 className="text-5xl md:text-6xl font-extrabold text-white mb-6 animate-fade-in drop-shadow-lg">
                            رزرو آنلاین نوبت آرایشگاه
                        </h1>
                        <p className="text-xl md:text-2xl text-white/90 mb-8 animate-fade-in drop-shadow-md font-medium">
                            بهترین سالن‌های زیبایی را پیدا کنید و نوبت خود را به راحتی رزرو کنید
                        </p>
                        <div className="flex flex-col sm:flex-row gap-4 justify-center animate-fade-in">
                            <div className="bg-white/20 backdrop-blur-md rounded-2xl px-6 py-4 border border-white/30 shadow-xl">
                                <div className="flex items-center space-x-3 space-x-reverse">
                                    <div className="w-12 h-12 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center shadow-lg">
                                        <span className="text-2xl">⚡</span>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-white font-bold text-lg drop-shadow-md">رزرو سریع</p>
                                        <p className="text-white/80 text-sm">در کمتر از 1 دقیقه</p>
                                    </div>
                                </div>
                            </div>
                            <div className="bg-white/20 backdrop-blur-md rounded-2xl px-6 py-4 border border-white/30 shadow-xl">
                                <div className="flex items-center space-x-3 space-x-reverse">
                                    <div className="w-12 h-12 bg-gradient-to-br from-blue-400 to-cyan-500 rounded-full flex items-center justify-center shadow-lg">
                                        <span className="text-2xl">🎯</span>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-white font-bold text-lg drop-shadow-md">پشتیبانی هوشمند</p>
                                        <p className="text-white/80 text-sm">24 ساعته آنلاین</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
                {isLoading ? (
                    <div className="text-center py-20">
                        <div className="inline-block animate-spin rounded-full h-16 w-16 border-b-4 border-indigo-600"></div>
                        <p className="text-gray-600 mt-4 text-lg">در حال بارگذاری سالن‌ها...</p>
                    </div>
                ) : error ? (
                    <div className="text-center py-20 bg-red-50 rounded-2xl border-2 border-red-200">
                        <span className="text-6xl mb-4 block">⚠️</span>
                        <p className="text-red-600 text-lg font-medium">
                            خطا در بارگذاری لیست سالن‌ها. لطفاً دوباره تلاش کنید.
                        </p>
                    </div>
                ) : (
                    <>
                        <div className="mb-8">
                            <h2 className="text-4xl font-extrabold text-gray-900 mb-2">
                                سالن‌های <span className="gradient-text">برگزیده</span>
                            </h2>
                            <p className="text-gray-600 text-lg">بهترین خدمات زیبایی در اطراف شما</p>
                        </div>

                        {salons && salons.length > 0 ? (
                            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                                {salons.map((salon) => (
                                    <div key={salon.id} className="card-hover">
                                        <SalonCard salon={salon} />
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-16 bg-gradient-to-r from-gray-50 to-gray-100 rounded-2xl border-2 border-gray-200">
                                <span className="text-6xl mb-6 block">🔍</span>
                                <p className="text-gray-700 text-xl font-medium mb-2">هنوز هیچ سالنی ثبت نشده است</p>
                                <p className="text-gray-500">به زودی سالن‌های جدیدی اضافه خواهند شد</p>
                            </div>
                        )}
                    </>
                )}
            </main>
        </div>
    );
};

export default Home;
