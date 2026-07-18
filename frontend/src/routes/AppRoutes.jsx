<<<<<<< HEAD
import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";

// Public Pages
import Landing from "../pages/landing/Landing";
import Login from "../pages/auth/Login";
import Register from "../pages/auth/Register";

// Admin Auth
import AdminLogin from "../pages/auth/AdminLogin";

// Admin Pages
import Dashboard from "../pages/admin/Dashboard";
import ManageEvents from "../pages/admin/ManageEvents";
import ManageQuizzes from "../pages/admin/ManageQuizzes";
import QuizResults from "../pages/admin/QuizResults";
import DashboardLayout from "../layouts/DashboardLayout";

const ProtectedRoute = ({ children, allowedRole }) => {
  const token = localStorage.getItem("token");
  const role = localStorage.getItem("role");

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRole && role !== allowedRole) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

const AppRoutes = () => {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Dedicated Admin Login */}
      <Route path="/admin/login" element={<AdminLogin />} />

      {/* Admin Protected Routes */}
      <Route
        path="/admin"
        element={
          <ProtectedRoute allowedRole="admin">
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="events" element={<ManageEvents />} />
        <Route path="quizzes" element={<ManageQuizzes />} />

        {/* Supporting upstream's route for manage-quizzes */}
        <Route path="manage-quizzes" element={<Navigate to="quizzes" replace />} />

        <Route path="quizzes/:id/results" element={<QuizResults />} />
        <Route
          path="profile"
          element={
            <div className="p-8">
              <h1 className="text-3xl font-extrabold text-[#386641] tracking-tight mb-4">Profile</h1>
              <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm text-gray-500">
                Departmental administrator profile settings and access keys. Coming soon.
              </div>
            </div>
          }
        />
      </Route>

      {/* Catch-all Redirect */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default AppRoutes;
=======
import { BrowserRouter, Routes, Route } from "react-router-dom";

import Landing from "../pages/landing/Landing";
import Login from "../pages/auth/Login";
import ManageQuizzes from "../pages/admin/ManageQuizzes";
import Register from "../pages/auth/Register";


function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
<Route path="/register" element={<Register />} />
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
       <Route path="/admin/manage-quizzes" element={<ManageQuizzes/>} />
      </Routes>
    </BrowserRouter>
  );
}

export default AppRoutes;
>>>>>>> upstream/main
