import React, { useState, useRef, useEffect } from 'react';
import FAQList, { type FAQ } from './FAQList';
import FAQAnswer from './FAQAnswer';
import { chatApi } from '../../api/chat';

interface Message {
    type: string;
    message: string;
    sender?: string;
    timestamp: string;
}

interface ChatWindowProps {
    messages: Message[];
    onSend: (message: string) => void;
    onClose: () => void;
    status: 'bot' | 'queued' | 'admin' | 'closed';
    isConnected: boolean;
}

type ViewMode = 'faq-list' | 'faq-answer' | 'chat';

const ChatWindow: React.FC<ChatWindowProps> = ({
    messages,
    onSend,
    onClose,
    status,
    isConnected,
}) => {
    const [input, setInput] = useState('');
    const [viewMode, setViewMode] = useState<ViewMode>('faq-list');
    const [faqs, setFaqs] = useState<FAQ[]>([]);
    const [selectedFAQ, setSelectedFAQ] = useState<FAQ | null>(null);
    const [faqsLoading, setFaqsLoading] = useState(true);
    const [faqsError, setFaqsError] = useState<string | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Load FAQs on mount
    useEffect(() => {
        const loadFAQs = async () => {
            try {
                setFaqsLoading(true);
                setFaqsError(null);
                console.log('Loading FAQs...');
                const data = await chatApi.getInitialFAQs();
                console.log('Loaded FAQs:', data);
                setFaqs(Array.isArray(data) ? data : []);
            } catch (error) {
                console.error('Failed to load FAQs:', error);
                setFaqsError('خطا در بارگذاری سوالات متداول');
                setFaqs([]); // Ensure faqs is always an array
            } finally {
                setFaqsLoading(false);
            }
        };

        loadFAQs();
    }, []);

    // Auto-switch to chat mode when messages arrive or status changes
    useEffect(() => {
        if (status === 'queued' || status === 'admin' || messages.length > 1) {
            setViewMode('chat');
        }
    }, [status, messages.length]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        if (viewMode === 'chat') {
            scrollToBottom();
        }
    }, [messages, viewMode]);

    const handleSend = () => {
        if (input.trim()) {
            onSend(input);
            setInput('');
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const handleSelectFAQ = (faq: FAQ) => {
        setSelectedFAQ(faq);
        setViewMode('faq-answer');
    };

    const handleBackToFAQs = () => {
        setSelectedFAQ(null);
        setViewMode('faq-list');
    };

    const handleEscalate = () => {
        setViewMode('chat');
        onSend('من نیاز به کمک پشتیبان دارم');
    };

    const getStatusBadge = () => {
        const statusConfig = {
            bot: { text: 'ربات هوشمند', color: 'bg-green-500' },
            queued: { text: 'در صف انتظار', color: 'bg-yellow-500' },
            admin: { text: 'پشتیبانی آنلاین', color: 'bg-blue-500' },
            closed: { text: 'بسته شده', color: 'bg-gray-500' },
        };
        const config = statusConfig[status];
        return (
            <span className={`${config.color} text-white text-xs px-2 py-1 rounded-full`}>
                {config.text}
            </span>
        );
    };

    return (
        <div className="fixed bottom-6 left-6 z-50 w-96 h-[600px] bg-white rounded-lg shadow-2xl flex flex-col">
            {/* Header */}
            <div className="bg-blue-600 text-white p-4 rounded-t-lg flex justify-between items-center">
                <div>
                    <h3 className="font-bold">پشتیبانی آنلاین</h3>
                    <div className="flex items-center gap-2 mt-1">
                        {viewMode === 'chat' && getStatusBadge()}
                        {viewMode === 'chat' && !isConnected && (
                            <span className="text-xs text-red-200">در حال اتصال...</span>
                        )}
                        {viewMode === 'faq-list' && (
                            <span className="text-xs">سوالات متداول</span>
                        )}
                    </div>
                </div>
                <button
                    onClick={onClose}
                    className="hover:bg-blue-700 rounded p-1 transition"
                >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>

            {/* Content - FAQ List, FAQ Answer, or Chat */}
            {viewMode === 'faq-list' && (
                <FAQList
                    faqs={faqs}
                    loading={faqsLoading}
                    error={faqsError}
                    onSelectFAQ={handleSelectFAQ}
                    onEscalate={handleEscalate}
                />
            )}

            {viewMode === 'faq-answer' && selectedFAQ && (
                <FAQAnswer
                    faq={selectedFAQ}
                    onBack={handleBackToFAQs}
                    onEscalate={handleEscalate}
                />
            )}

            {viewMode === 'chat' && (
                <>
                    {/* Back to FAQs button */}
                    {status === 'bot' && messages.length <= 1 && (
                        <div className="p-2 border-b bg-gray-50">
                            <button
                                onClick={handleBackToFAQs}
                                className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
                            >
                                <span>←</span>
                                <span>بازگشت به سوالات متداول</span>
                            </button>
                        </div>
                    )}

                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50">
                        {messages.map((msg, idx) => (
                            <div
                                key={idx}
                                className={`flex ${msg.sender === 'user' || msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
                            >
                                <div
                                    className={`max-w-[80%] p-3 rounded-lg ${msg.sender === 'user' || msg.type === 'user'
                                        ? 'bg-blue-600 text-white'
                                        : msg.type === 'system'
                                            ? 'bg-yellow-100 text-gray-800 border border-yellow-300'
                                            : 'bg-white text-gray-800 shadow'
                                        }`}
                                >
                                    <p className="text-sm whitespace-pre-wrap">{msg.message}</p>
                                    <span className="text-xs opacity-75 mt-1 block">
                                        {new Date(msg.timestamp).toLocaleTimeString('fa-IR', {
                                            hour: '2-digit',
                                            minute: '2-digit',
                                        })}
                                    </span>
                                </div>
                            </div>
                        ))}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input */}
                    <div className="border-t p-4">
                        <div className="flex gap-2">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyPress={handleKeyPress}
                                placeholder="پیام خود را بنویسید..."
                                className="flex-1 border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                disabled={!isConnected || status === 'closed'}
                            />
                            <button
                                onClick={handleSend}
                                disabled={!input.trim() || !isConnected || status === 'closed'}
                                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
                            >
                                ارسال
                            </button>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
};

export default ChatWindow;
