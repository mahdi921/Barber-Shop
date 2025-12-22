import React, { useState, useEffect } from 'react';
import type { User } from '../../types/auth';
import Button from '../ui/Button';
import Modal from '../ui/Modal';

interface EditUserModalProps {
    user: User | null;
    isOpen: boolean;
    onClose: () => void;
    onSave: (id: number, data: Partial<User>) => void;
    isLoading?: boolean;
}

const EditUserModal: React.FC<EditUserModalProps> = ({ user, isOpen, onClose, onSave, isLoading }) => {
    const [isActive, setIsActive] = useState(false);
    const [phoneNumber, setPhoneNumber] = useState('');

    useEffect(() => {
        if (user) {
            setIsActive(user.is_active);
            setPhoneNumber(user.phone_number);
        }
    }, [user]);

    if (!user) return null;

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSave(user.id, {
            is_active: isActive,
            phone_number: phoneNumber
        });
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} title="ویرایش کاربر" size="md">
            <div className="text-sm text-gray-500 mb-4">
                <div>شناسه: {user.id}</div>
                <div>نوع: {user.user_type === 'customer' ? 'مشتری' :
                    user.user_type === 'stylist' ? 'آرایشگر' :
                        user.user_type === 'salon_manager' ? 'مدیر سالن' : 'ادمین'}</div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label htmlFor="phone" className="block text-sm font-medium text-gray-700">شماره تلفن</label>
                    <input
                        type="text"
                        name="phone"
                        id="phone"
                        value={phoneNumber}
                        onChange={(e) => setPhoneNumber(e.target.value)}
                        className="mt-1 focus:ring-blue-500 focus:border-blue-500 block w-full shadow-sm sm:text-sm border border-gray-300 rounded-md p-2"
                        dir="ltr"
                    />
                </div>

                <div className="flex items-center">
                    <input
                        id="is_active"
                        name="is_active"
                        type="checkbox"
                        checked={isActive}
                        onChange={(e) => setIsActive(e.target.checked)}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor="is_active" className="mr-2 block text-sm text-gray-900">
                        حساب کاربری فعال است
                    </label>
                </div>

                <div className="mt-5 sm:mt-4 flex flex-row-reverse gap-2">
                    <Button
                        type="submit"
                        isLoading={isLoading}
                        className="w-full sm:w-auto"
                    >
                        ذخیره
                    </Button>
                    <Button
                        type="button"
                        variant="secondary"
                        onClick={onClose}
                        className="w-full sm:w-auto"
                    >
                        انصراف
                    </Button>
                </div>
            </form>
        </Modal>
    );
};

export default EditUserModal;
