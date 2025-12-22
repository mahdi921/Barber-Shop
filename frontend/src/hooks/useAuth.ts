import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { authApi } from '../api/auth';
import { useNavigate } from 'react-router-dom';

export function useAuth() {
    const queryClient = useQueryClient();
    const navigate = useNavigate();

    // Fetch current user
    const { data: user, isLoading, isError } = useQuery({
        queryKey: ['auth', 'user'],
        queryFn: async () => {
            // Ensure we have CSRF token
            try {
                await authApi.getCsrf();
            } catch (e) {
                // ignore error
            }
            return authApi.getCurrentUser();
        },
        retry: false, // Don't retry if 401
        staleTime: 1000 * 60 * 5, // 5 minutes
    });

    // Login mutation
    const loginMutation = useMutation({
        mutationFn: authApi.login,
        onSuccess: (data) => {
            // Invalidate user query to refetch
            queryClient.setQueryData(['auth', 'user'], data.user);

            // Redirect based on user type
            const userType = data.user.user_type;
            if (userType === 'site_admin') {
                navigate('/admin');
            } else if (userType === 'stylist') {
                if (data.user.is_temporary) {
                    navigate('/complete-profile');
                } else {
                    navigate('/stylist/dashboard');
                }
            } else if (userType === 'salon_manager') {
                navigate('/manager/dashboard');
            } else {
                navigate('/dashboard'); // Customer
            }
        },
    });

    // Logout mutation
    const logoutMutation = useMutation({
        mutationFn: authApi.logout,
        onSuccess: () => {
            queryClient.setQueryData(['auth', 'user'], null);
            navigate('/login');
        },
    });

    return {
        user,
        isLoading,
        isAuthenticated: !!user,
        isUserError: isError, // Renamed to avoid confusion
        login: loginMutation.mutate,
        logout: logoutMutation.mutate,
        isLoggingIn: loginMutation.isPending,
        isLoggingOut: logoutMutation.isPending,
        loginError: loginMutation.error,
        isLoginError: loginMutation.isError,
    };
}
