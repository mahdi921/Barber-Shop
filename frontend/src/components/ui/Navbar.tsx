import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

const Navbar: React.FC = () => {
    const { user, isAuthenticated, logout } = useAuth();
    const navigate = useNavigate();
    const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

    const handleLogout = async () => {
        await logout();
        navigate('/login');
    };

    const getNavigationItems = () => {
        if (!isAuthenticated || !user) {
            return [
                { label: 'خانه', path: '/' },
                { label: 'ورود', path: '/login', highlight: true },
            ];
        }

        const baseItems = [{ label: 'خانه', path: '/' }];

        switch (user.user_type) {
            case 'customer':
                return [
                    ...baseItems,
                    { label: 'داشبورد', path: '/dashboard' },
                    { label: 'رزروهای من', path: '/dashboard' },
                ];
            case 'stylist':
                return [
                    ...baseItems,
                    { label: 'داشبورد', path: '/stylist-dashboard' },
                    { label: 'برنامه کاری', path: '/stylist-dashboard' },
                ];
            case 'salon_manager':
                return [
                    ...baseItems,
                    { label: 'داشبورد', path: '/manager/dashboard' },
                    { label: 'مدیریت سالن', path: '/manager/dashboard' },
                ];
            case 'site_admin':
                return [
                    ...baseItems,
                    { label: ' پنل مدیریت', path: '/admin' },
                ];
            default:
                return baseItems;
        }
    };

    const navItems = getNavigationItems();

    return (
        <nav className="bg-gradient-to-r from-indigo-900 via-purple-900 to-indigo-900 text-white shadow-xl sticky top-0 z-50 border-b-2 border-indigo-500/30">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16">
                    {/* Logo/Brand */}
                    <Link to="/" className="flex items-center space-x-3 space-x-reverse group">
                        <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-lg flex items-center justify-center shadow-lg group-hover:shadow-purple-500/50 transition-shadow duration-300">
                            <span className="text-2xl">💈</span>
                        </div>
                        <div className="hidden md:block">
                            <h1 className="text-xl font-bold bg-gradient-to-r from-white to-purple-200 bg-clip-text text-transparent">
                                رزرو آنلاین آرایشگاه
                            </h1>
                            <p className="text-xs text-purple-200">سامانه هوشمند نوبت‌دهی</p>
                        </div>
                    </Link>

                    {/* Desktop Navigation */}
                    <div className="hidden md:flex items-center space-x-6 space-x-reverse">
                        {navItems.map((item, index) => (
                            <Link
                                key={index}
                                to={item.path}
                                className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${item.highlight
                                        ? 'bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 shadow-lg hover:shadow-purple-500/50'
                                        : 'hover:bg-white/10 hover:text-purple-200'
                                    }`}
                            >
                                {item.label}
                            </Link>
                        ))}

                        {isAuthenticated && user && (
                            <div className="flex items-center space-x-4 space-x-reverse border-r border-white/20 pr-4 mr-2">
                                <div className="text-right">
                                    <p className="text-sm font-medium text-purple-100">
                                        {user.user_type === 'customer' && user.customer_profile?.full_name}
                                        {user.user_type !== 'customer' && user.phone_number}
                                    </p>
                                    <p className="text-xs text-purple-300">
                                        {user.user_type === 'customer' && 'مشتری'}
                                        {user.user_type === 'stylist' && 'آرایشگر'}
                                        {user.user_type === 'salon_manager' && 'مدیر سالن'}
                                        {user.user_type === 'site_admin' && 'مدیر سیستم'}
                                    </p>
                                </div>
                                <div className="w-10 h-10 bg-gradient-to-br from-purple-400 to-pink-500 rounded-full flex items-center justify-center font-bold shadow-lg">
                                    {user.customer_profile?.first_name?.charAt(0) || user.phone_number?.charAt(0) || 'U'}
                                </div>
                                <button
                                    onClick={handleLogout}
                                    className="px-4 py-2 text-sm bg-red-600/80 hover:bg-red-700 rounded-lg transition-colors duration-200"
                                >
                                    خروج
                                </button>
                            </div>
                        )}
                    </div>

                    {/* Mobile Menu Button */}
                    <button
                        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                        className="md:hidden p-2 rounded-lg hover:bg-white/10 transition-colors"
                    >
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            {mobileMenuOpen ? (
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            ) : (
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                            )}
                        </svg>
                    </button>
                </div>
            </div>

            {/* Mobile Menu */}
            {mobileMenuOpen && (
                <div className="md:hidden bg-indigo-900/95 backdrop-blur-lg border-t border-white/10 animate-slide-in-right">
                    <div className="px-4 py-3 space-y-2">
                        {navItems.map((item, index) => (
                            <Link
                                key={index}
                                to={item.path}
                                onClick={() => setMobileMenuOpen(false)}
                                className={`block px-4 py-3 rounded-lg font-medium transition-all ${item.highlight
                                        ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-lg'
                                        : 'hover:bg-white/10'
                                    }`}
                            >
                                {item.label}
                            </Link>
                        ))}

                        {isAuthenticated && user && (
                            <div className="pt-3 mt-3 border-t border-white/20 space-y-2">
                                <div className="px-4 py-2">
                                    <p className="text-sm font-medium text-purple-100">
                                        {user.user_type === 'customer' && user.customer_profile?.full_name}
                                        {user.user_type !== 'customer' && user.phone_number}
                                    </p>
                                    <p className="text-xs text-purple-300">
                                        {user.user_type === 'customer' && 'مشتری'}
                                        {user.user_type === 'stylist' && 'آرایشگر'}
                                        {user.user_type === 'salon_manager' && 'مدیر سالن'}
                                        {user.user_type === 'site_admin' && 'مدیر سیستم'}
                                    </p>
                                </div>
                                <button
                                    onClick={() => {
                                        handleLogout();
                                        setMobileMenuOpen(false);
                                    }}
                                    className="w-full px-4 py-3 text-sm bg-red-600/80 hover:bg-red-700 rounded-lg transition-colors"
                                >
                                    خروج
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </nav>
    );
};

export default Navbar;
