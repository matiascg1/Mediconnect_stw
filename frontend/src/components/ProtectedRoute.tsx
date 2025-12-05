"use client"

import type React from "react"
import { Navigate } from "react-router-dom"
import { useAuth } from "../contexts/AuthContext"
import LoadingSpinner from "./Common/LoadingSpinner"

interface ProtectedRouteProps {
  children: React.ReactNode
  requiredRole?: "patient" | "doctor" | "admin"
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, requiredRole }) => {
  const { isAuthenticated, user, isLoading } = useAuth()

  if (isLoading) {
    return <LoadingSpinner />
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (requiredRole && user?.role !== requiredRole) {
    // Redirigir al dashboard según el rol del usuario
    switch (user?.role) {
      case "patient":
        return <Navigate to="/dashboard/patient" replace />
      case "doctor":
        return <Navigate to="/dashboard/doctor" replace />
      case "admin":
        return <Navigate to="/dashboard/admin" replace />
      default:
        return <Navigate to="/" replace />
    }
  }

  return <>{children}</>
}

export default ProtectedRoute
