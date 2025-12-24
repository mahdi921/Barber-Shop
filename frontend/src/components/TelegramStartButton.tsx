import { useState } from 'react';
import { useAuth } from '../hooks/useAuth';

const TelegramStartButton = () => {
    const { user } = useAuth();
    const [isLinked, setIsLinked] = useState(false);
    const [showInstructions, setShowInstructions] = useState(false);

    // Check if user has telegram linked
    const hasTelegram = user?.customer_profile?.telegram_chat_id ||
        user?.stylist_profile?.telegram_chat_id ||
        user?.manager_profile?.telegram_chat_id;

    // If already linked, show success message
    if (hasTelegram || isLinked) {
        return (
            <div className="bg-green-50 border-2 border-green-200 rounded-lg p-4 mb-4">
                <div className="flex items-center gap-3">
                    <span className="text-2xl">✅</span>
                    <span className="text-green-800 font-semibold">
                        ربات تلگرام فعال شد
                    </span>
                </div>
            </div>
        );
    }

    const handleClick = () => {
        setShowInstructions(true);
    };

    const telegramLink = `https://t.me/${user?.telegram_bot_username}?start=${user?.phone_number || ''}`;

    if (showInstructions) {
        return (
            <div className="bg-blue-50 border-2 border-blue-300 rounded-lg p-6 mb-4">
                <h3 className="text-lg font-bold text-blue-900 mb-4">
                    📱 راه‌اندازی ربات تلگرام
                </h3>

                <div className="space-y-4">
                    <div className="bg-white rounded-lg p-4 border border-blue-200">
                        <p className="text-sm text-gray-700 mb-3">
                            <strong>مرحله 1:</strong> روی دکمه زیر کلیک کنید تا تلگرام باز شود
                        </p>
                        <a
                            href={telegramLink}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-block w-full bg-blue-600 text-white px-6 py-3 rounded-lg font-bold text-center hover:bg-blue-700 transition"
                        >
                            🤖 باز کردن ربات در تلگرام
                        </a>
                    </div>

                    <div className="bg-white rounded-lg p-4 border border-blue-200">
                        <p className="text-sm text-gray-700 mb-2">
                            <strong>مرحله 2:</strong> بعد از باز شدن تلگرام، دکمه START را بزنید
                        </p>
                        <code className="block bg-gray-100 p-2 rounded text-sm" dir="ltr">
                            /start {user?.phone_number}
                        </code>
                    </div>

                    <button
                        onClick={() => {
                            setIsLinked(true);
                            // Optionally refresh user data here
                        }}
                        className="text-sm text-blue-600 hover:text-blue-800"
                    >
                        ربات را فعال کردم ✓
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-300 rounded-lg p-4 mb-4">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <span className="text-2xl">📱</span>
                    <div>
                        <h3 className="font-bold text-gray-900">
                            دریافت اعلان‌های نوبت در تلگرام
                        </h3>
                        <p className="text-sm text-gray-600">
                            برای دریافت یادآوری نوبت، ربات تلگرام را فعال کنید
                        </p>
                    </div>
                </div>
                <button
                    onClick={handleClick}
                    className="bg-blue-600 text-white px-6 py-3 rounded-lg font-bold hover:bg-blue-700 transition whitespace-nowrap"
                >
                    فعال‌سازی ربات تلگرام
                </button>
            </div>
        </div>
    );
};

export default TelegramStartButton;
