import React from 'react';
import { Link } from 'react-router-dom';

const Footer: React.FC = () => {
    const currentYear = new Date().getFullYear();
    const persianYear = currentYear; // In production, convert to Persian calendar

    return (
        <footer className="bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 text-gray-300 mt-auto border-t-2 border-indigo-500/20">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                    {/* Brand & Description */}
                    <div className="md:col-span-1">
                        <div className="flex items-center space-x-3 space-x-reverse mb-4">
                            <div className="w-12 h-12 bg-gradient-to-br from-purple-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
                                <span className="text-3xl">💈</span>
                            </div>
                            <div>
                                <h3 className="text-lg font-bold text-white">رزرو آنلاین</h3>
                                <p className="text-xs text-purple-400">سامانه نوبت‌دهی</p>
                            </div>
                        </div>
                        <p className="text-sm text-gray-400 leading-relaxed">
                            سامانه هوشمند رزرو نوبت آرایشگاه و سالن‌های زیبایی با امکانات پیشرفته و پشتیبانی 24 ساعته
                        </p>
                    </div>

                    {/* Quick Links */}
                    <div>
                        <h4 className="text-white font-semibold mb-4 pb-2 border-b border-gray-700">دسترسی سریع</h4>
                        <ul className="space-y-3">
                            <li>
                                <Link to="/" className="text-gray-400 hover:text-purple-400 transition-colors duration-200 text-sm flex items-center">
                                    <span className="ml-2">←</span>
                                    صفحه اصلی
                                </Link>
                            </li>
                            <li>
                                <Link to="/login" className="text-gray-400 hover:text-purple-400 transition-colors duration-200 text-sm flex items-center">
                                    <span className="ml-2">←</span>
                                    ورود / ثبت‌نام
                                </Link>
                            </li>
                            <li>
                                <Link to="/register/manager" className="text-gray-400 hover:text-purple-400 transition-colors duration-200 text-sm flex items-center">
                                    <span className="ml-2">←</span>
                                    ثبت سالن
                                </Link>
                            </li>
                        </ul>
                    </div>

                    {/* Services */}
                    <div>
                        <h4 className="text-white font-semibold mb-4 pb-2 border-b border-gray-700">خدمات</h4>
                        <ul className="space-y-3 text-sm text-gray-400">
                            <li className="flex items-start">
                                <span className="text-purple-500 ml-2">•</span>
                                رزرو آنلاین نوبت
                            </li>
                            <li className="flex items-start">
                                <span className="text-purple-500 ml-2">•</span>
                                پشتیبانی هوشمند
                            </li>
                            <li className="flex items-start">
                                <span className="text-purple-500 ml-2">•</span>
                                مدیریت سالن‌های زیبایی
                            </li>
                            <li className="flex items-start">
                                <span className="text-purple-500 ml-2">•</span>
                                ارسال اعلان تلگرام
                            </li>
                        </ul>
                    </div>

                    {/* Contact */}
                    <div>
                        <h4 className="text-white font-semibold mb-4 pb-2 border-b border-gray-700">ارتباط با ما</h4>
                        <div className="space-y-3 text-sm">
                            <div className="flex items-center space-x-2 space-x-reverse text-gray-400">
                                <svg className="w-5 h-5 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                                </svg>
                                <span>support@barber.shop</span>
                            </div>
                            <div className="flex items-center space-x-2 space-x-reverse text-gray-400">
                                <svg className="w-5 h-5 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                                </svg>
                                <span>021-12345678</span>
                            </div>
                        </div>

                        {/* Social Links */}
                        <div className="mt-4 flex space-x-4 space-x-reverse">
                            <a href="#" className="w-10 h-10 bg-gray-800 hover:bg-purple-600 rounded-full flex items-center justify-center transition-colors duration-200">
                                <span className="text-xl">📱</span>
                            </a>
                            <a href="#" className="w-10 h-10 bg-gray-800 hover:bg-purple-600 rounded-full flex items-center justify-center transition-colors duration-200">
                                <span className="text-xl">✈️</span>
                            </a>
                        </div>
                    </div>
                </div>

                {/* Bottom Bar */}
                <div className="mt-12 pt-8 border-t border-gray-700">
                    <div className="flex flex-col md:flex-row justify-between items-center text-sm text-gray-500">
                        <p className="mb-4 md:mb-0">
                            © {persianYear} سامانه رزرو آنلاین آرایشگاه. تمامی حقوق محفوظ است.
                        </p>
                        <p className="text-purple-400">
                            طراحی شده با{' '}
                            <span className="text-red-500 animate-pulse">❤️</span>
                            {' '}برای آرایشگران ایران
                        </p>
                    </div>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
