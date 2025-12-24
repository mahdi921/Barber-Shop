import { useEffect, useState } from 'react';
import type { AppConfig } from '../api/config';
import { configApi } from '../api/config';

/**
 * Hook to fetch and cache app configuration
 */
export const useConfig = () => {
    const [config, setConfig] = useState<AppConfig | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchConfig = async () => {
            try {
                const data = await configApi.getConfig();
                setConfig(data);
                setError(null);
            } catch (err) {
                console.error('Failed to fetch config:', err);
                setError('Failed to load configuration');
                // Set defaults if API fails
                setConfig({
                    telegram_bot_username: '',
                    telegram_bot_enabled: false,
                });
            } finally {
                setLoading(false);
            }
        };

        fetchConfig();
    }, []);

    return { config, loading, error };
};
