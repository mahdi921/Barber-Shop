import React from 'react';
import { useConfig } from '../../hooks/useConfig';

interface TelegramSetupCardProps {
    hasTelegramLinked: boolean;
    userPhone?: string;
}

const TelegramSetupCard: React.FC<TelegramSetupCardProps> = ({ hasTelegramLinked, userPhone }) => {
    const { config } = useConfig();

    if (!config || !config.telegram_bot_enabled) {
        return null; // Don't show if bot is disabled
    }

    const botLink = `https://t.me/${config.telegram_bot_username}`;
    const startCommand = userPhone ? `/start ${userPhone}` : '/start شماره_تلفن_شما';

    if (hasTelegramLinked) {
        return (
            <div className="bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200 rounded-xl p-5 shadow-sm">
                <div className="flex items-start gap-4">
                    <div className="flex-shrink-0">
                        <div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center">
                            <span className="text-2xl">✅</span>
                        </div>
                    </div>
                    <div className="flex-1">
                        <h3 className="text-lg font-bold text-green-800 mb-1">
                            تلگرام شما متصل است!
                        </h3>
                        <p className="text-sm text-green-700">
                            شما اعلان‌های نوبت خود را از طریق تلگرام دریافت خواهید کرد.
                        </p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-xl p-5 shadow-md">
            <div className="flex items-start gap-4">
                <div className="flex-shrink-0">
                    <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center animate-pulse-glow">
                        <span className="text-2xl">📱</span>
                    </div>
                </div>
                <div className="flex-1">
                    <h3 className="text-lg font-bold text-blue-900 mb-2">
                        اتصال به ربات تلگرام
                    </h3>
                    <p className="text-sm text-blue-800 mb-3">
                        برای دریافت اعلان‌های نوبت در تلگرام، ربات را استارت کنید:
                    </p>

                    <div className="bg-white rounded-lg p-4 mb-3 border border-blue-200">
                        <p className="text-xs font-semibold text-gray-600 mb-2">مرحله 1: باز کردن ربات</p>
                        <a
                            href={botLink}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="block w-full bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white font-bold py-2.5 px-4 rounded-lg transition-all duration-200 text-center shadow-md hover:shadow-lg text-sm"
                        >
                            <span className="flex items-center justify-center gap-2">
                                <span>🤖</span>
                                باز کردن ربات تلگرام
                            </span>
                        </a>
                    </div>

                    <div className="bg-white rounded-lg p-4 border border-blue-200">
                        <p className="text-xs font-semibold text-gray-600 mb-2">مرحله 2: ارسال دستور</p>
                        <div className="bg-gray-100 rounded-md p-3 font-mono text-sm text-gray-800 border border-gray-300">
                            {startCommand}
                        </div>
                        <p className="text-xs text-gray-600 mt-2">
                            {userPhone
                                ? 'این دستور را در تلگرام ارسال کنید'
                                : 'شماره تلفن خود را جایگزین کنید'
                            }
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default TelegramSetupCard;
