import React from 'react';
import type { FAQ } from './FAQList';

interface FAQAnswerProps {
    faq: FAQ;
    onBack: () => void;
    onEscalate: () => void;
}

const FAQAnswer: React.FC<FAQAnswerProps> = ({ faq, onBack, onEscalate }) => {
    return (
        <div className="flex flex-col h-full">
            {/* Back Button Header */}
            <div className="p-4 border-b border-gray-200 bg-gray-50">
                <button
                    onClick={onBack}
                    className="flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium transition-colors"
                >
                    <span className="text-xl">←</span>
                    <span>بازگشت به سوالات</span>
                </button>
            </div>

            {/* FAQ Content */}
            <div className="flex-1 overflow-y-auto p-6">
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    {/* Question */}
                    <div className="mb-4">
                        <h4 className="text-sm font-semibold text-gray-500 mb-2">سوال:</h4>
                        <p className="text-lg font-bold text-gray-900">{faq.question}</p>
                    </div>

                    {/* Answer */}
                    <div>
                        <h4 className="text-sm font-semibold text-gray-500 mb-2">پاسخ:</h4>
                        <div className="prose prose-blue max-w-none">
                            <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">{faq.answer}</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Action Buttons */}
            <div className="p-4 border-t border-gray-200 bg-gray-50 space-y-2">
                <button
                    onClick={onBack}
                    className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-3 px-4 rounded-lg transition-colors duration-200"
                >
                    بازگشت به سوالات
                </button>
                <button
                    onClick={onEscalate}
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg transition-colors duration-200 flex items-center justify-center gap-2"
                >
                    <span className="text-xl">💬</span>
                    <span>همچنان نیاز به کمک دارم</span>
                </button>
            </div>
        </div>
    );
};

export default FAQAnswer;
