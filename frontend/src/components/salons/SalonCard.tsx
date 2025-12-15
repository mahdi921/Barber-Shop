import type { Salon } from '../../types/salon';
import { GENDER_LABELS } from '../../types/salon';
import Button from '../ui/Button';
import { Link } from 'react-router-dom';

interface SalonCardProps {
    salon: Salon;
}

const SalonCard: React.FC<SalonCardProps> = ({ salon }) => {
    return (
        <div className="bg-white overflow-hidden shadow rounded-lg hover:shadow-lg transition-shadow duration-300 flex flex-col h-full">
            <div className="h-48 w-full bg-gray-200 relative">
                <img
                    src={salon.photo}
                    alt={salon.name}
                    className="w-full h-full object-cover"
                />
                <div className="absolute top-2 right-2 bg-white px-2 py-1 rounded-full text-xs font-semibold shadow">
                    {GENDER_LABELS[salon.gender_type]}
                </div>
            </div>

            <div className="px-4 py-4 flex-grow flex flex-col justify-between">
                <div>
                    <div className="flex justify-between items-start">
                        <h3 className="text-lg font-medium text-gray-900 truncate" title={salon.name}>
                            {salon.name}
                        </h3>
                        <div className="flex items-center bg-yellow-100 px-1.5 py-0.5 rounded text-yellow-800 text-sm">
                            <span>{salon.average_rating}</span>
                            <svg className="w-3 h-3 mr-1 fill-current" viewBox="0 0 24 24">
                                <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z" />
                            </svg>
                        </div>
                    </div>

                    <p className="mt-1 text-sm text-gray-500 line-clamp-2" title={salon.address}>
                        {salon.address}
                    </p>

                    <div className="mt-3 flex flex-wrap gap-1">
                        {salon.services.slice(0, 3).map(service => (
                            <span key={service.id} className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                                {service.custom_name}
                            </span>
                        ))}
                        {salon.services.length > 3 && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                                +{salon.services.length - 3}
                            </span>
                        )}
                    </div>
                </div>

                <div className="mt-4">
                    <Link to={`/salon/${salon.id}`} className="block w-full">
                        <Button variant="primary" className="w-full">
                            رزرو نوبت
                        </Button>
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default SalonCard;
