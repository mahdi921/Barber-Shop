/**
 * API client for app configuration
 */
import client from './client';

export interface AppConfig {
    telegram_bot_username: string;
    telegram_bot_enabled: boolean;
}

export const configApi = {
    getConfig: async (): Promise<AppConfig> => {
        const response = await client.get<AppConfig>('/api/config/');
        return response.data;
    },
};
