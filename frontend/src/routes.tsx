import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import CustomerRegister from './pages/CustomerRegister';
import ManagerRegister from './pages/ManagerRegister';
import AdminDashboard from './pages/admin/AdminDashboard';
import Home from './pages/Home';
import SalonDetail from './pages/SalonDetail';
import CustomerDashboard from './pages/dashboard/CustomerDashboard';
import StylistDashboard from './pages/dashboard/StylistDashboard';
import { useAuth } from './hooks/useAuth';

// Protected Route Wrapper
const ProtectedRoute = ({ children, allowedRoles }: { children: React.ReactNode, allowedRoles?: string[] }) => {
    const { user, isLoading, isAuthenticated } = useAuth();

    if (isLoading) {
        return <div className="flex justify-center items-center h-screen">در حال بارگذاری...</div>;
    }

    if (!isAuthenticated || !user) {
        return <Navigate to="/login" replace />;
    }

    if (allowedRoles && !allowedRoles.includes(user.user_type)) {
        return <div className="p-4 text-center text-red-600">دسترسی غیرمجاز</div>;
    }

    return children;
};

const AppRoutes = () => {
    return (
        <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/" element={<Home />} />
            <Route path="/salon/:id" element={<SalonDetail />} />

            {/* Dasboard placeholders */}
            <Route path="/dashboard" element={
                <ProtectedRoute allowedRoles={['customer']}>
                    <CustomerDashboard />
                </ProtectedRoute>
            } />

            <Route path="/stylist-dashboard" element={
                <ProtectedRoute allowedRoles={['stylist']}>
                    <StylistDashboard />
                </ProtectedRoute>
            } />

            <Route path="/admin" element={
                <ProtectedRoute allowedRoles={['site_admin']}>
                    <AdminDashboard />
                </ProtectedRoute>
            } />

            {/* Default redirect */}
            <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
    );
};

export default AppRoutes;
