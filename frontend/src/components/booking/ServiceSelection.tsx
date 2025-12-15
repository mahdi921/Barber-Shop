import React from 'react';
import type { Service } from '../../types/salon';

interface ServiceSelectionProps {
    services: Service[];
    selectedServices: number[];
    onToggleService: (serviceId: number) => void;
}

const ServiceSelection: React.FC<ServiceSelectionProps> = ({
    services,
    selectedServices,
    onToggleService
}) => {
    return (
        <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900">انتخاب خدمات</h3>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                {services.map((service) => {
                    const isSelected = selectedServices.includes(service.id);
                    return (
                        <div
                            key={service.id}
                            onClick={() => onToggleService(service.id)}
                            className={`
                relative flex items-center px-6 py-5 border rounded-lg cursor-pointer transition-colors
                ${isSelected ? 'border-blue-500 ring-1 ring-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400'}
              `}
                        >
                            <div className="flex-1 min-w-0">
                                <div className="flex justify-between">
                                    <span className="text-sm font-medium text-gray-900 line-clamp-1" title={service.custom_name}>
                                        {service.custom_name}
                                    </span>
                                    <span className="inline-block text-xs text-gray-500 bg-gray-100 rounded px-2 py-0.5">
                                        {parseInt(service.price).toLocaleString()} ت
                                    </span>
                                </div>
                                {service.stylist_name && (
                                    <p className="text-xs text-gray-500 mt-1">توسط: {service.stylist_name}</p>
                                )}
                                <p className="text-xs text-gray-400 mt-0.5">{service.duration_minutes} دقیقه</p>
                            </div>
                            <div className={`mr-4 flex-shrink-0 h-5 w-5 rounded-full border flex items-center justify-center ${isSelected ? 'bg-blue-600 border-transparent' : 'border-gray-300'}`}>
                                {isSelected && (
                                    <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                    </svg>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default ServiceSelection;
