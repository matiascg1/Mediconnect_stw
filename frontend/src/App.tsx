"use client"

import type React from "react"
import { Routes, Route, Navigate } from "react-router-dom"
import { useAuth } from "./contexts/AuthContext"

// Layout components
import Layout from "./components/Layout/Layout"
import LoadingSpinner from "./components/Common/LoadingSpinner"

// Public pages
import HomePage from "./pages/Public/HomePage"
import LoginPage from "./pages/LoginPage"
import RegisterPage from "./pages/RegisterPage"
import AboutPage from "./pages/Public/AboutPage"
import ContactPage from "./pages/Public/ContactPage"
import NotFound from "./pages/NotFound"

// Dashboard pages
import PatientDashboard from "./pages/Dashboard/PatientDashboard"
import DoctorDashboard from "./pages/Dashboard/DoctorDashboard"
import AdminDashboard from "./pages/Dashboard/AdminDashboard"

// Protected route component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return <LoadingSpinner />
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" />
  }

  return <>{children}</>
}

// Role-based route component
const RoleRoute: React.FC<{
  children: React.ReactNode
  allowedRoles: string[]
}> = ({ children, allowedRoles }) => {
  const { user } = useAuth()

  if (!user || !allowedRoles.includes(user.role)) {
    return <Navigate to="/dashboard" />
  }

  return <>{children}</>
}

function App() {
  const { user } = useAuth()

  const getDashboardComponent = () => {
    if (!user) return <Navigate to="/login" />

    switch (user.role) {
      case "patient":
        return <PatientDashboard />
      case "doctor":
        return <DoctorDashboard />
      case "admin":
        return <AdminDashboard />
      default:
        return <Navigate to="/login" />
    }
  }

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<HomePage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/about" element={<AboutPage />} />
      <Route path="/contact" element={<ContactPage />} />

      {/* Protected routes */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Layout>{getDashboardComponent()}</Layout>
          </ProtectedRoute>
        }
      />

      {/* Admin routes */}
      <Route
        path="/admin/*"
        element={
          <ProtectedRoute>
            <RoleRoute allowedRoles={["admin"]}>
              <Layout>
                <Routes>
                  <Route path="users" element={<div>Users Management</div>} />
                  <Route path="metrics" element={<div>System Metrics</div>} />
                  <Route path="settings" element={<div>Settings</div>} />
                </Routes>
              </Layout>
            </RoleRoute>
          </ProtectedRoute>
        }
      />

      {/* Catch-all route */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}

export default App
