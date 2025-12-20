import React, { useState } from 'react';
import { Truck, Save, AlertTriangle } from 'lucide-react';
import api from '../api';

export const VehicleReception = () => {
    const [formData, setFormData] = useState({
        plate: '',
        brand: '',
        model: '',
    });
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setMessage(null);

        try {
            await api.post('/vehicles', formData);
            setMessage({ type: 'success', text: 'Araç başarıyla sisteme kaydedildi.' });
            setFormData({ plate: '', brand: '', model: '' });
        } catch (error: any) {
            setMessage({
                type: 'error',
                text: error.response?.data?.detail || 'Bir hata oluştu.'
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-2xl mx-auto">
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-gray-900">Araç Kabul</h1>
                <p className="text-gray-500">Atölyeye yeni araç girişi yapın.</p>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                {message && (
                    <div className={`p-4 mb-6 rounded-lg flex items-center gap-3 ${message.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
                        }`}>
                        {message.type === 'error' && <AlertTriangle size={20} />}
                        {message.text}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Plaka</label>
                        <input
                            type="text"
                            required
                            placeholder="42 ABC 123"
                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none uppercase"
                            value={formData.plate}
                            onChange={(e) => setFormData({ ...formData, plate: e.target.value.toUpperCase() })}
                        />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Marka</label>
                            <input
                                type="text"
                                required
                                placeholder="Ford"
                                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                                value={formData.brand}
                                onChange={(e) => setFormData({ ...formData, brand: e.target.value })}
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Model</label>
                            <input
                                type="text"
                                required
                                placeholder="Transit"
                                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                                value={formData.model}
                                onChange={(e) => setFormData({ ...formData, model: e.target.value })}
                            />
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-lg flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
                    >
                        {loading ? 'Kaydediliyor...' : (
                            <>
                                <Save size={20} />
                                Kaydet ve Giriş Yap
                            </>
                        )}
                    </button>
                </form>
            </div>
        </div>
    );
};
