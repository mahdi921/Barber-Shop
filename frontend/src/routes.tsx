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
import ManagerDashboard from './pages/dashboard/ManagerDashboard';
import SalonDetailManagement from './pages/dashboard/SalonDetailManagement';
import Layout from './components/ui/Layout';
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
            {/* Public routes with layout */}
            <Route path="/login" element={<Layout><Login /></Layout>} />
            <Route path="/register/customer" element={<Layout><CustomerRegister /></Layout>} />
            <Route path="/register/manager" element={<Layout><ManagerRegister /></Layout>} />
            <Route path="/" element={<Layout><Home /></Layout>} />
            <Route path="/salon/:id" element={<Layout><SalonDetail /></Layout>} />

            {/* Protected routes with layout */}
            <Route path="/dashboard" element={
                <Layout>
                    <ProtectedRoute allowedRoles={['customer']}>
                        <CustomerDashboard />
                    </ProtectedRoute>
                </Layout>
            } />

            <Route path="/stylist-dashboard" element={
                <Layout>
                    <ProtectedRoute allowedRoles={['stylist']}>
                        <StylistDashboard />
                    </ProtectedRoute>
                </Layout>
            } />

            <Route path="/manager/dashboard" element={
                <Layout>
                    <ProtectedRoute allowedRoles={['salon_manager']}>
                        <ManagerDashboard />
                    </ProtectedRoute>
                </Layout>
            } />

            <Route path="/manager/dashboard/salons/:salonId" element={
                <Layout>
                    <ProtectedRoute allowedRoles={['salon_manager']}>
                        <SalonDetailManagement />
                    </ProtectedRoute>
                </Layout>
            } />

            <Route path="/admin" element={
                <Layout>
                    <ProtectedRoute allowedRoles={['site_admin']}>
                        <AdminDashboard />
                    </ProtectedRoute>
                </Layout>
            } />

            {/* Default redirect */}
            <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
    );
};

export default AppRoutes;
