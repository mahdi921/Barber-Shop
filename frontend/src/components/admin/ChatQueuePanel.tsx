import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { chatApi } from '../../api/chat';
import Button from '../ui/Button';

interface QueueEntry {
    session_key: string;
    reason: string;
    priority: number;
    position: number;
    joined_at: string;
    waiting_time: number;
    user_name?: string;
    last_message?: string;
}

interface ChatQueuePanelProps {
    onJoinChat?: (sessionKey: string) => void;
}

const ChatQueuePanel: React.FC<ChatQueuePanelProps> = ({ onJoinChat }) => {
    const queryClient = useQueryClient();
    const [claiming, setClaiming] = useState<string | null>(null);

    // Fetch queue with auto-refresh
    const { data: queue, isLoading, error } = useQuery({
        queryKey: ['admin', 'chat-queue'],
        queryFn: chatApi.getQueue,
        refetchInterval: 5000, // Refresh every 5 seconds
    });

    const handleClaimChat = async (sessionKey: string) => {
        setClaiming(sessionKey);
        try {
            // Call backend to claim/lock the chat
            // Note: This would need a new API endpoint for claiming
            // For now, we'll use the join mechanism
            if (onJoinChat) {
                onJoinChat(sessionKey);
            }

            // Refresh the queue
            queryClient.invalidateQueries({ queryKey: ['admin', 'chat-queue'] });
        } catch (error) {
            console.error('Error claiming chat:', error);
            alert('خطا در انتخاب چت. ممکن است توسط ادمین دیگری انتخاب شده باشد.');
        } finally {
            setClaiming(null);
        }
    };

    const formatWaitTime = (seconds: number) => {
        const minutes = Math.floor(seconds / 60);
        if (minutes < 1) return 'کمتر از ۱ دقیقه';
        if (minutes === 1) return '۱ دقیقه';
        return `${minutes} دقیقه`;
    };

    const getPriorityBadge = (priority: number) => {
        if (priority >= 8) return { text: 'فوری', color: 'bg-red-500' };
        if (priority >= 5) return { text: 'متوسط', color: 'bg-yellow-500' };
        return { text: 'عادی', color: 'bg-green-500' };
    };

    if (isLoading) {
        return (
            <div className="p-8 text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-4 text-gray-600">در حال بارگزاری صف چت...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-8 text-center text-red-500">
                خطا در دریافت صف چت. لطفاً دوباره تلاش کنید.
            </div>
        );
    }

    const queueList = queue || [];

    return (
        <div className="bg-white rounded-lg shadow">
            {/* Header */}
            <div className="p-6 border-b border-gray-200">
                <div className="flex justify-between items-center">
                    <div>
                        <h2 className="text-2xl font-bold text-gray-900">صف چت‌های در انتظار</h2>
                        <p className="text-sm text-gray-600 mt-1">
                            کاربرانی که منتظر پاسخ پشتیبان هستند
                        </p>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="bg-blue-100 text-blue-800 px-4 py-2 rounded-full font-bold">
                            {queueList.length} نفر در صف
                        </div>
                    </div>
                </div>
            </div>

            {/* Queue List */}
            <div className="divide-y divide-gray-200">
                {queueList.length === 0 ? (
                    <div className="p-12 text-center text-gray-500">
                        <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                        </svg>
                        <p className="text-lg font-medium">هیچ چتی در صف نیست</p>
                        <p className="text-sm mt-1">همه کاربران پاسخگری شده‌اند 🎉</p>
                    </div>
                ) : (
                    queueList.map((entry) => {
                        const priorityBadge = getPriorityBadge(entry.priority);

                        return (
                            <div key={entry.session_key} className="p-6 hover:bg-gray-50 transition-colors">
                                <div className="flex justify-between items-start gap-4">
                                    {/* Chat Info */}
                                    <div className="flex-1">
                                        <div className="flex items-center gap-3 mb-3">
                                            {/* Position Badge */}
                                            <div className="bg-gray-200 text-gray-700 w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg">
                                                {entry.position}
                                            </div>

                                            {/* Priority Badge */}
                                            <span className={`${priorityBadge.color} text-white text-xs px-3 py-1 rounded-full font-medium`}>
                                                {priorityBadge.text}
                                            </span>

                                            {/* Wait Time */}
                                            <span className="text-sm text-gray-600">
                                                زمان انتظار: <span className="font-medium">{formatWaitTime(entry.waiting_time)}</span>
                                            </span>
                                        </div>

                                        {/* Reason/Last Message */}
                                        <div className="bg-gray-100 p-3 rounded-lg mb-2">
                                            <p className="text-sm text-gray-700">
                                                <span className="font-medium">دلیل:</span> {entry.reason || 'درخواست کمک'}
                                            </p>
                                            {entry.last_message && (
                                                <p className="text-sm text-gray-600 mt-1">
                                                    <span className="font-medium">آخرین پیام:</span> {entry.last_message}
                                                </p>
                                            )}
                                        </div>

                                        <div className="text-xs text-gray-500">
                                            Session: {entry.session_key.slice(0, 8)}...
                                        </div>
                                    </div>

                                    {/* Action Button */}
                                    <div>
                                        <Button
                                            onClick={() => handleClaimChat(entry.session_key)}
                                            disabled={claiming === entry.session_key}
                                            className="whitespace-nowrap"
                                        >
                                            {claiming === entry.session_key ? (
                                                <>
                                                    <span className="animate-spin mr-2">⏳</span>
                                                    در حال اتصال...
                                                </>
                                            ) : (
                                                <>
                                                    <span className="mr-2">💬</span>
                                                    پاسخ دهم
                                                </>
                                            )}
                                        </Button>
                                    </div>
                                </div>
                            </div>
                        );
                    })
                )}
            </div>

            {/* Auto-refresh indicator */}
            {queueList.length > 0 && (
                <div className="p-4 bg-gray-50 border-t border-gray-200 text-center">
                    <p className="text-xs text-gray-500">
                        🔄 این صف هر ۵ ثانیه به‌روزرسانی می‌شود
                    </p>
                </div>
            )}
        </div>
    );
};

export default ChatQueuePanel;
