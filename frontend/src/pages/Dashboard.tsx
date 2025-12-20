import React from 'react';
import { Truck, AlertCircle, CheckCircle, Clock } from 'lucide-react';

const StatCard = ({ title, value, icon: Icon, color }: any) => (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <div className="flex justify-between items-start">
            <div>
                <p className="text-sm font-medium text-gray-500 mb-1">{title}</p>
                <h3 className="text-2xl font-bold text-gray-900">{value}</h3>
            </div>
            <div className={`p-3 rounded-lg ${color}`}>
                <Icon size={20} className="text-white" />
            </div>
        </div>
    </div>
);

export const Dashboard = () => {
    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold text-gray-900">Atölye Durumu</h1>
                <p className="text-gray-500">Bugünkü atölye özeti</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard title="İşlemdeki Araç" value="12" icon={Truck} color="bg-blue-500" />
                <StatCard title="Bekleyen İş" value="5" icon={Clock} color="bg-orange-500" />
                <StatCard title="Tamamlanan" value="24" icon={CheckCircle} color="bg-green-500" />
                <StatCard title="Kritik Stok" value="3" icon={AlertCircle} color="bg-red-500" />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <h3 className="font-bold mb-4">Son İşlemler</h3>
                    <div className="space-y-4">
                        {[1, 2, 3].map((i) => (
                            <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-bold text-sm">
                                        42
                                    </div>
                                    <div>
                                        <p className="font-medium">42 KNY 123</p>
                                        <p className="text-xs text-gray-500">Periyodik Bakım - Ford Transit</p>
                                    </div>
                                </div>
                                <span className="text-sm text-green-600 font-medium">Tamamlandı</span>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <h3 className="font-bold mb-4">Ustalar</h3>
                    <div className="space-y-3">
                        {[1, 2, 3, 4].map((i) => (
                            <div key={i} className="flex items-center gap-3">
                                <div className="w-2 h-2 rounded-full bg-green-500"></div>
                                <span className="text-sm font-medium">Mehmet Usta</span>
                                <span className="text-xs text-gray-400 ml-auto">Fren Balt.</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};
