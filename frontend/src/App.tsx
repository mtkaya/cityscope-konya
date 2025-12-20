import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { DashboardLayout } from './layouts/DashboardLayout';
import { Dashboard } from './pages/Dashboard';
import { VehicleReception } from './pages/VehicleReception';
import { WorkOrderList } from './pages/WorkOrderList';
import { TechnicianJob } from './pages/TechnicianJob';
import { Inventory } from './pages/Inventory';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<DashboardLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="reception" element={<VehicleReception />} />

          <Route path="reception" element={<VehicleReception />} />
          <Route path="work-orders" element={<WorkOrderList />} />
          <Route path="work-orders/:id" element={<TechnicianJob />} />
          <Route path="inventory" element={<Inventory />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
