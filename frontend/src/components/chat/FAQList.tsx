import React from 'react';

export interface FAQ {
    id: number;
    question: string;
    answer: string;
    category: string;
    priority: number;
}

interface FAQListProps {
    faqs: FAQ[];
    onSelectFAQ: (faq: FAQ) => void;
    onEscalate: () => void;
}

const FAQList: React.FC<FAQListProps> = ({ faqs, onSelectFAQ, onEscalate }) => {
    return (
        <div className="flex flex-col h-full">
            {/* Header */}
            <div className="p-4 border-b border-gray-200 bg-blue-50">
                <h3 className="text-lg font-bold text-gray-900">سوالات متداول</h3>
                <p className="text-sm text-gray-600 mt-1">یکی از سوالات زیر را انتخاب کنید:</p>
            </div>

            {/* FAQ List */}
            <div className="flex-1 overflow-y-auto p-4 space-y-2">
                {Array.isArray(faqs) && faqs.length > 0 ? (
                    faqs.map((faq) => (
                        <button
                            key={faq.id}
                            onClick={() => onSelectFAQ(faq)}
                            className="w-full text-right p-4 border border-gray-200 rounded-lg hover:bg-blue-50 hover:border-blue-300 transition-colors duration-200 group"
                        >
                            <div className="flex items-start gap-3">
                                <span className="text-blue-600 mt-1 text-xl group-hover:scale-110 transition-transform">▸</span>
                                <span className="text-gray-900 font-medium">{faq.question}</span>
                            </div>
                        </button>
                    ))
                ) : (
                    <div className="text-center py-8 text-gray-500">
                        <p>در حال بارگذاری سوالات...</p>
                    </div>
                )}
            </div>

            {/* Escalation Button */}
            <div className="p-4 border-t border-gray-200 bg-gray-50">
                <button
                    onClick={onEscalate}
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg transition-colors duration-200 flex items-center justify-center gap-2"
                >
                    <span className="text-xl">💬</span>
                    <span>گفتگو با پشتیبان</span>
                </button>
                <p className="text-xs text-gray-500 text-center mt-2">
                    برای سوالات خاص با پشتیبان ما در تماس باشید
                </p>
            </div>
        </div>
    );
};

export default FAQList;
