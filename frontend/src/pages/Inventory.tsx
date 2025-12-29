import React, { useEffect, useState } from 'react';
import { Package, Plus, Search, AlertTriangle } from 'lucide-react';
import api from '../api';

export const Inventory = () => {
    const [items, setItems] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showAddModal, setShowAddModal] = useState(false);
    const [newItem, setNewItem] = useState({ name: '', sku: '', quantity: 0, critical_level: 5 });

    useEffect(() => {
        fetchInventory();
    }, []);

    const fetchInventory = async () => {
        try {
            setError(null);
            const res = await api.get('/inventory/');
            setItems(res.data);
        } catch (err: any) {
            console.error('Error fetching inventory:', err);
            setError(err.message || 'Envanter yüklenirken hata oluştu');
            setItems([]);
        } finally {
            setLoading(false);
        }
    };

    const handleAddItem = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await api.post('/inventory/', newItem);
            setShowAddModal(false);
            setNewItem({ name: '', sku: '', quantity: 0, critical_level: 5 });
            await fetchInventory();
        } catch (err: any) {
            console.error('Error adding item:', err);
            alert('Malzeme eklenirken hata oluştu: ' + (err.message || 'Bilinmeyen hata'));
        }
    };

    if (loading) return <div className="text-center py-8">Yükleniyor...</div>;

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Stok & Ambar</h1>
                    <p className="text-gray-500">Yedek parça ve malzeme yönetimi</p>
                </div>
                <button
                    onClick={() => setShowAddModal(true)}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700"
                >
                    <Plus size={20} />
                    Yeni Malzeme
                </button>
            </div>

            {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex justify-between items-center">
                    <span>{error}</span>
                    <button onClick={fetchInventory} className="text-red-600 hover:text-red-800 font-medium">
                        Tekrar Dene
                    </button>
                </div>
            )}

            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                <div className="p-4 border-b border-gray-100 flex gap-4">
                    <div className="relative flex-1">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
                        <input
                            type="text"
                            placeholder="Parça ara..."
                            className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg outline-none focus:ring-2 focus:ring-blue-100"
                        />
                    </div>
                </div>

                <table className="w-full text-left">
                    <thead className="bg-gray-50 text-gray-500 text-sm">
                        <tr>
                            <th className="p-4 font-medium">Parça Adı</th>
                            <th className="p-4 font-medium">SKU / Barkod</th>
                            <th className="p-4 font-medium">Miktar</th>
                            <th className="p-4 font-medium">Durum</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {items.map((item) => (
                            <tr key={item.id} className="hover:bg-gray-50">
                                <td className="p-4 font-medium text-gray-900">
                                    <div className="flex items-center gap-3">
                                        <div className="p-2 bg-blue-50 rounded-lg text-blue-600">
                                            <Package size={18} />
                                        </div>
                                        {item.name}
                                    </div>
                                </td>
                                <td className="p-4 text-gray-500 font-mono text-sm">{item.sku}</td>
                                <td className="p-4 font-bold text-gray-900">{item.quantity} Adet</td>
                                <td className="p-4">
                                    {item.quantity <= item.critical_level ? (
                                        <span className="inline-flex items-center gap-1 px-2 py-1 bg-red-100 text-red-700 rounded text-xs font-medium">
                                            <AlertTriangle size={12} /> Kritik
                                        </span>
                                    ) : (
                                        <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-medium">
                                            Yeterli
                                        </span>
                                    )}
                                </td>
                            </tr>
                        ))}
                        {items.length === 0 && !loading && (
                            <tr>
                                <td colSpan={4} className="p-8 text-center text-gray-500">Henüz kayıtlı malzeme yok.</td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>

            {/* Add Modal */}
            {showAddModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white rounded-xl max-w-md w-full p-6">
                        <h3 className="text-xl font-bold mb-4">Yeni Malzeme Ekle</h3>
                        <form onSubmit={handleAddItem} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium mb-1">Parça Adı</label>
                                <input
                                    className="w-full border p-2 rounded"
                                    value={newItem.name}
                                    onChange={e => setNewItem({ ...newItem, name: e.target.value })}
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">SKU / Barkod</label>
                                <input
                                    className="w-full border p-2 rounded"
                                    value={newItem.sku}
                                    onChange={e => setNewItem({ ...newItem, sku: e.target.value })}
                                    required
                                />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium mb-1">Miktar</label>
                                    <input
                                        type="number"
                                        className="w-full border p-2 rounded"
                                        value={newItem.quantity}
                                        onChange={e => setNewItem({ ...newItem, quantity: parseInt(e.target.value) })}
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-1">Kritik Seviye</label>
                                    <input
                                        type="number"
                                        className="w-full border p-2 rounded"
                                        value={newItem.critical_level}
                                        onChange={e => setNewItem({ ...newItem, critical_level: parseInt(e.target.value) })}
                                        required
                                    />
                                </div>
                            </div>
                            <div className="flex justify-end gap-3 mt-6">
                                <button
                                    type="button"
                                    onClick={() => setShowAddModal(false)}
                                    className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded"
                                >
                                    İptal
                                </button>
                                <button
                                    type="submit"
                                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                                >
                                    Kaydet
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};
