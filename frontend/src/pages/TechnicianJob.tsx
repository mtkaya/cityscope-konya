import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Play, Pause, CheckCircle, Plus, ArrowLeft } from 'lucide-react';
import api from '../api';

export const TechnicianJob = () => {
    const { id } = useParams(); // Work Order ID
    const navigate = useNavigate();
    const [job, setJob] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [parts, setParts] = useState<any[]>([]); // Available parts
    const [showPartModal, setShowPartModal] = useState(false);

    // Timer state for display (local simulation)
    const [elapsed, setElapsed] = useState(0);

    useEffect(() => {
        fetchJob();
        fetchInventory();
    }, [id]);

    useEffect(() => {
        // Simple timer ticker if status is IN_PROGRESS
        let interval: any;
        if (job?.status === 'in_progress') {
            interval = setInterval(() => {
                setElapsed(prev => prev + 1);
            }, 1000);
        }
        return () => clearInterval(interval);
    }, [job?.status]);

    const fetchJob = async () => {
        try {
            const res = await api.get('/work-orders/');
            // In a real app we'd fetch specific ID, but our API list is small
            const found = res.data.find((w: any) => w.id === parseInt(id || '0'));
            setJob(found);
            if (found) setElapsed(found.total_labor_seconds);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const fetchInventory = async () => {
        try {
            const res = await api.get('/inventory/');
            setParts(res.data);
        } catch (err: any) {
            console.error('Error fetching inventory:', err);
            alert('Envanter yüklenirken hata oluştu: ' + (err.message || 'Bilinmeyen hata'));
            setParts([]);
        }
    };

    const handleStart = async () => {
        try {
            await api.post(`/work-orders/${id}/start`);
            await fetchJob(); // Refresh
        } catch (err: any) {
            console.error('Error starting work order:', err);
            alert('İş başlatılamadı: ' + (err.message || 'Bilinmeyen hata'));
        }
    };

    const handleStop = async () => {
        try {
            await api.post(`/work-orders/${id}/stop`);
            await fetchJob();
        } catch (err: any) {
            console.error('Error stopping work order:', err);
            alert('İş durdurulamadı: ' + (err.message || 'Bilinmeyen hata'));
        }
    };

    const handleFinish = async () => {
        if (confirm('İşi tamamlamak istediğinize emin misiniz?')) {
            try {
                await api.put(`/work-orders/${id}/status?status=completed`);
                navigate('/work-orders');
            } catch (err: any) {
                console.error('Error completing work order:', err);
                alert('İş tamamlanamadı: ' + (err.message || 'Bilinmeyen hata'));
            }
        }
    };

    const handleAddPart = async (itemId: number, qty: number) => {
        try {
            await api.post(`/work-orders/${id}/parts`, {
                inventory_item_id: itemId,
                quantity: qty
            });
            setShowPartModal(false);
            alert('Parça eklendi');
            fetchJob();
        } catch (err: any) {
            alert('Hata: ' + (err.response?.data?.detail || 'Bilinmiyor'));
        }
    };

    if (loading) return <div>Yükleniyor...</div>;
    if (!job) return <div>İş bulunamadı.</div>;

    const formatTime = (seconds: number) => {
        const h = Math.floor(seconds / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        const s = seconds % 60;
        return `${h}s ${m}d ${s}sn`;
    };

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            <button onClick={() => navigate('/work-orders')} className="flex items-center text-gray-500 hover:text-gray-900">
                <ArrowLeft size={20} className="mr-2" /> Geri Dön
            </button>

            <div className="bg-white p-6 rounded-xl shadow-sm border border-blue-100 flex justify-between items-start">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Araç Bakım İşlemi</h1>
                    <p className="text-xl text-gray-600 mt-2">Plaka: <span className="font-mono font-bold text-black">{job.vehicle_id}</span> (ID)</p>
                    <p className="text-gray-500 mt-1">{job.description}</p>
                </div>
                <div className="text-right">
                    <div className="text-4xl font-mono font-bold text-blue-600 tabular-nums">
                        {formatTime(elapsed)}
                    </div>
                    <div className="text-sm text-gray-400 mt-1">Toplam Süre</div>
                </div>
            </div>

            {/* Action Buttons */}
            <div className="grid grid-cols-3 gap-4 h-32">
                {job.status !== 'in_progress' ? (
                    <button
                        onClick={handleStart}
                        className="bg-green-600 hover:bg-green-700 text-white rounded-xl flex flex-col items-center justify-center gap-2 text-xl font-bold shadow-lg transition-transform active:scale-95"
                    >
                        <Play size={40} />
                        BAŞLAT
                    </button>
                ) : (
                    <button
                        onClick={handleStop}
                        className="bg-orange-500 hover:bg-orange-600 text-white rounded-xl flex flex-col items-center justify-center gap-2 text-xl font-bold shadow-lg"
                    >
                        <Pause size={40} />
                        DURAKLAT
                    </button>
                )}

                <button
                    onClick={() => setShowPartModal(true)}
                    className="bg-blue-600 hover:bg-blue-700 text-white rounded-xl flex flex-col items-center justify-center gap-2 text-xl font-bold shadow-lg"
                >
                    <Plus size={40} />
                    PARÇA EKLE
                </button>

                <button
                    onClick={handleFinish}
                    className="bg-gray-800 hover:bg-black text-white rounded-xl flex flex-col items-center justify-center gap-2 text-xl font-bold shadow-lg"
                >
                    <CheckCircle size={40} />
                    İŞİ BİTİR
                </button>
            </div>

            {/* Part Selection Modal (Simplified) */}
            {showPartModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white rounded-xl max-w-lg w-full p-6 h-96 overflow-auto">
                        <h3 className="text-xl font-bold mb-4">Parça Seçimi</h3>
                        <div className="space-y-2">
                            {parts.map(p => (
                                <div key={p.id} className="flex items-center justify-between p-3 border rounded hover:bg-gray-50">
                                    <div>
                                        <p className="font-bold">{p.name}</p>
                                        <p className="text-sm text-gray-500">Stok: {p.quantity}</p>
                                    </div>
                                    <button
                                        onClick={() => handleAddPart(p.id, 1)}
                                        className="bg-blue-100 text-blue-700 px-3 py-1 rounded font-bold hover:bg-blue-200"
                                    >
                                        + Ekle
                                    </button>
                                </div>
                            ))}
                        </div>
                        <button onClick={() => setShowPartModal(false)} className="mt-4 w-full py-3 bg-gray-100 rounded text-gray-600">İptal</button>
                    </div>
                </div>
            )}
        </div>
    );
};
