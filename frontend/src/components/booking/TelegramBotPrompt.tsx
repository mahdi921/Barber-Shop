import React from 'react';

interface TelegramBotPromptProps {
    botUsername: string;
    onContinueWithoutTelegram: () => void;
    onCancel: () => void;
}

const TelegramBotPrompt: React.FC<TelegramBotPromptProps> = ({
    botUsername,
    onContinueWithoutTelegram,
    onCancel,
}) => {
    const telegramLink = `https://t.me/${botUsername}`;

    return (
        <div className="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
            <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
                {/* Background overlay */}
                <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" onClick={onCancel}></div>

                {/* Center modal */}
                <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

                <div className="inline-block align-bottom bg-white rounded-2xl text-right overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full animate-fade-in">
                    <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-5">
                        <h3 className="text-2xl font-bold text-white flex items-center gap-3" id="modal-title">
                            <span className="text-3xl">📱</span>
                            اتصال به تلگرام
                        </h3>
                    </div>

                    <div className="bg-white px-6 py-6">
                        <div className="space-y-4">
                            <div className="bg-blue-50 border-r-4 border-blue-500 p-4 rounded-lg">
                                <p className="text-gray-700 text-lg leading-relaxed">
                                    برای دریافت <span className="font-bold text-blue-600">اعلان‌های تلگرام</span> نوبت خود، لطفاً ابتدا ربات تلگرام ما را استارت کنید.
                                </p>
                            </div>

                            <div className="space-y-3">
                                <h4 className="font-semibold text-gray-900 flex items-center gap-2">
                                    <span>✨</span>
                                    مزایای اتصال به تلگرام:
                                </h4>
                                <ul className="space-y-2 text-gray-700">
                                    <li className="flex items-start gap-2">
                                        <span className="text-green-500 mt-1">✓</span>
                                        <span>دریافت اعلان فوری پس از رزرو</span>
                                    </li>
                                    <li className="flex items-start gap-2">
                                        <span className="text-green-500 mt-1">✓</span>
                                        <span>یادآوری قبل از وقت نوبت</span>
                                    </li>
                                    <li className="flex items-start gap-2">
                                        <span className="text-green-500 mt-1">✓</span>
                                        <span>اطلاع از تأیید یا تغییر وضعیت نوبت</span>
                                    </li>
                                </ul>
                            </div>

                            <div className="bg-purple-50 border border-purple-200 rounded-xl p-4">
                                <p className="text-sm text-gray-600 mb-3">
                                    <span className="font-semibold">مرحله 1:</span> روی دکمه زیر کلیک کنید تا ربات در تلگرام باز شود
                                </p>
                                <a
                                    href={telegramLink}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="block w-full bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white font-bold py-3 px-4 rounded-lg transition-all duration-200 text-center shadow-lg hover:shadow-xl"
                                >
                                    <span className="flex items-center justify-center gap-2">
                                        <span className="text-2xl">🤖</span>
                                        باز کردن ربات تلگرام
                                    </span>
                                </a>

                                <p className="text-sm text-gray-600 mt-3">
                                    <span className="font-semibold">مرحله 2:</span> دستور زیر را ارسال کنید:
                                </p>
                                <div className="bg-white rounded-lg p-3 mt-2 font-mono text-sm text-gray-800 border border-gray-300">
                                    /start شماره_تلفن_شما
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="bg-gray-50 px-6 py-4 sm:flex sm:flex-row-reverse gap-3">
                        <button
                            type="button"
                            onClick={onContinueWithoutTelegram}
                            className="w-full inline-flex justify-center rounded-lg border border-gray-300 shadow-sm px-4 py-2.5 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:w-auto sm:text-sm transition-colors"
                        >
                            ادامه بدون تلگرام
                        </button>
                        <button
                            type="button"
                            onClick={onCancel}
                            className="mt-3 w-full inline-flex justify-center rounded-lg border border-gray-300 shadow-sm px-4 py-2.5 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 sm:mt-0 sm:w-auto sm:text-sm transition-colors"
                        >
                            انصراف
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default TelegramBotPrompt;
