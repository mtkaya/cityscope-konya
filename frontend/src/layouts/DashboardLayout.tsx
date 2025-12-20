import React from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import { LayoutDashboard, Truck, ClipboardList, Package, Menu } from 'lucide-react';
import clsx from 'clsx';

const SidebarItem = ({ to, icon: Icon, label }: { to: string; icon: any; label: string }) => {
    const location = useLocation();
    const isActive = location.pathname === to;

    return (
        <Link
            to={to}
            className={clsx(
                "flex items-center gap-3 px-4 py-3 rounded-lg transition-colors",
                isActive
                    ? "bg-blue-600 text-white"
                    : "text-gray-600 hover:bg-gray-100"
            )}
        >
            <Icon size={20} />
            <span className="font-medium">{label}</span>
        </Link>
    );
};

export const DashboardLayout = () => {
    return (
        <div className="flex h-screen bg-gray-50">
            {/* Sidebar */}
            <aside className="w-64 bg-white border-r border-gray-200 hidden md:flex flex-col">
                <div className="p-6 border-b border-gray-100">
                    <h1 className="text-2xl font-bold text-blue-800">Akıllı Atölye</h1>
                    <p className="text-xs text-gray-500">Konya Büyükşehir Bld.</p>
                </div>

                <nav className="flex-1 p-4 space-y-2">
                    <SidebarItem to="/" icon={LayoutDashboard} label="Genel Bakış" />
                    <SidebarItem to="/reception" icon={Truck} label="Araç Kabul" />
                    <SidebarItem to="/work-orders" icon={ClipboardList} label="İş Emirleri" />
                    <SidebarItem to="/inventory" icon={Package} label="Stok & Ambar" />
                </nav>

                <div className="p-4 border-t border-gray-100">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold">
                            A
                        </div>
                        <div>
                            <p className="text-sm font-medium">Ahmet Yılmaz</p>
                            <p className="text-xs text-gray-500">Atölye Şefi</p>
                        </div>
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-auto">
                <header className="bg-white border-b border-gray-200 p-4 md:hidden flex justify-between items-center">
                    <span className="font-bold">Akıllı Atölye</span>
                    <button className="p-2"><Menu size={20} /></button>
                </header>
                <div className="p-4 md:p-8 max-w-7xl mx-auto">
                    <Outlet />
                </div>
            </main>
        </div>
    );
};
