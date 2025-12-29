import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ClipboardList, Plus } from 'lucide-react';
import api from '../api';

export const WorkOrderList = () => {
    const navigate = useNavigate();
    const [orders, setOrders] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [newOrder, setNewOrder] = useState({ vehicle_plate: '', description: '', technician_id: 1 });

    useEffect(() => {
        fetchOrders();
    }, []);

    const fetchOrders = async () => {
        try {
            setError(null);
            const res = await api.get('/work-orders/');
            setOrders(res.data);
        } catch (err: any) {
            console.error('Error fetching work orders:', err);
            setError(err.message || 'İş emirleri yüklenirken hata oluştu');
            setOrders([]);
        } finally {
            setLoading(false);
        }
    };

    const handleCreate = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await api.post('/work-orders/', newOrder);
            setShowCreateModal(false);
            fetchOrders();
        } catch (err: any) {
            alert('Hata: ' + (err.response?.data?.detail || 'Bilinmiyor'));
        }
    };

    if (loading) return <div className="text-center py-8">Yükleniyor...</div>;

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">İş Emirleri</h1>
                    <p className="text-gray-500">Atölyedeki tüm aktif ve bekleyen işler</p>
                </div>
                <button onClick={() => setShowCreateModal(true)} className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700">
                    <Plus size={20} />
                    Yeni İş Emri Aç
                </button>
            </div>

            {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex justify-between items-center">
                    <span>{error}</span>
                    <button onClick={fetchOrders} className="text-red-600 hover:text-red-800 font-medium">
                        Tekrar Dene
                    </button>
                </div>
            )}

            <div className="grid gap-4">
                {orders.map((wo) => (
                    <div key={wo.id} className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between hover:shadow-md transition-shadow">
                        <div className="flex items-center gap-4">
                            <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg
                                ${wo.status === 'pending' ? 'bg-gray-100 text-gray-600' :
                                    wo.status === 'in_progress' ? 'bg-orange-100 text-orange-600' : 'bg-green-100 text-green-600'}`
                            }>
                                {wo.vehicle_id}
                            </div>
                            <div>
                                <h3 className="font-bold text-gray-900">Araç ID: {wo.vehicle_id}</h3>
                                <p className="text-gray-500">{wo.description}</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-4">
                            <span className="text-sm font-medium px-3 py-1 bg-gray-50 rounded-full capitalize">
                                {wo.status.replace('_', ' ')}
                            </span>
                            <button
                                onClick={() => navigate(`/work-orders/${wo.id}`)}
                                className="bg-blue-50 text-blue-600 px-4 py-2 rounded-lg font-medium hover:bg-blue-100"
                            >
                                Detay / Usta Ekranı
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            {/* Create Modal */}
            {showCreateModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white rounded-xl max-w-md w-full p-6">
                        <h3 className="text-xl font-bold mb-4">Yeni İş Emri</h3>
                        <form onSubmit={handleCreate} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium mb-1">Araç Plakası</label>
                                <input className="w-full border p-2 rounded uppercase" value={newOrder.vehicle_plate} onChange={e => setNewOrder({ ...newOrder, vehicle_plate: e.target.value })} required placeholder="42 ABC 123" />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">Yapılacak İş</label>
                                <textarea className="w-full border p-2 rounded" value={newOrder.description} onChange={e => setNewOrder({ ...newOrder, description: e.target.value })} required rows={3} />
                            </div>
                            <div className="flex justify-end gap-3 mt-6">
                                <button type="button" onClick={() => setShowCreateModal(false)} className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded">İptal</button>
                                <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Oluştur</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};
