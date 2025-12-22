import React from 'react';
import Modal from './ui/Modal';
import Button from './ui/Button';

interface TelegramModalProps {
    isOpen: boolean;
    onClose: () => void;
    registeredPhone: string;
}

const TelegramModal: React.FC<TelegramModalProps> = ({ isOpen, onClose, registeredPhone }) => {
    const handleConnectTelegram = () => {
        window.open(`https://t.me/BarberShopBot?start=${registeredPhone}`, '_blank');
        onClose();
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} size="sm">
            <div>
                <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100">
                    <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                </div>
                <div className="mt-3 text-center sm:mt-5">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">
                        ثبت‌نام موفقیت‌آمیز بود!
                    </h3>
                    <div className="mt-2">
                        <p className="text-sm text-gray-500">
                            برای دریافت نوبت‌ها و اعلان‌ها، لطفاً به ربات تلگرام متصل شوید.
                        </p>
                    </div>
                </div>
            </div>
            <div className="mt-5 sm:mt-6 space-y-3">
                <Button
                    onClick={handleConnectTelegram}
                    className="w-full"
                >
                    اتصال به تلگرام 🚀
                </Button>
                <Button
                    variant="secondary"
                    onClick={onClose}
                    className="w-full"
                >
                    بعداً
                </Button>
            </div>
        </Modal>
    );
};

export default TelegramModal;
