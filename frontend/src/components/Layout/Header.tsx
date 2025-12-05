"use client"

import type React from "react"
import { useState } from "react"
import { Link, useNavigate, useLocation } from "react-router-dom"
import { useAuth } from "../../contexts/AuthContext"
import { Menu, X, User, LogOut, ChevronDown, Activity } from "lucide-react"

const Header: React.FC = () => {
  const { user, logout, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const [isProfileOpen, setIsProfileOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate("/login")
  }

  const isActive = (path: string) => {
    return location.pathname === path
  }

  const navLinkClass = (path: string) =>
    `px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 ${
      isActive(path)
        ? "text-primary-600 bg-primary-50"
        : "text-secondary-600 hover:text-primary-600 hover:bg-secondary-50"
    }`

  return (
    <header className="sticky top-0 z-50 w-full glass shadow-sm transition-all duration-200">
      <div className="container-custom">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center gap-2 group">
              <div className="bg-primary-600 text-white p-1.5 rounded-lg group-hover:bg-primary-700 transition-colors">
                <Activity className="h-6 w-6" />
              </div>
              <span className="text-xl font-bold text-secondary-900 tracking-tight">
                Medi<span className="text-primary-600">Connect</span>
              </span>
            </Link>

            {/* Desktop Navigation */}
            {isAuthenticated && (
              <nav className="hidden md:ml-10 md:flex md:space-x-2">
                <Link to="/dashboard" className={navLinkClass("/dashboard")}>
                  Dashboard
                </Link>
                <Link to="/appointments" className={navLinkClass("/appointments")}>
                  Appointments
                </Link>
                {user?.role === "doctor" && (
                  <Link to="/ehr" className={navLinkClass("/ehr")}>
                    EHR
                  </Link>
                )}
                {user?.role === "admin" && (
                  <Link to="/admin" className={navLinkClass("/admin")}>
                    Admin
                  </Link>
                )}
              </nav>
            )}
          </div>

          {/* Right Side Actions */}
          <div className="hidden md:flex items-center space-x-4">
            {isAuthenticated ? (
              <div className="relative">
                <button
                  onClick={() => setIsProfileOpen(!isProfileOpen)}
                  className="flex items-center gap-3 px-3 py-2 rounded-full border border-secondary-200 hover:bg-secondary-50 transition-all"
                >
                  <div className="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center text-primary-700 font-semibold">
                    {user?.first_name?.charAt(0) || "U"}
                  </div>
                  <div className="text-left hidden lg:block">
                    <p className="text-sm font-medium text-secondary-900 leading-none">
                      {user?.first_name} {user?.last_name}
                    </p>
                    <p className="text-xs text-secondary-500 capitalize mt-0.5">{user?.role}</p>
                  </div>
                  <ChevronDown className={`h-4 w-4 text-secondary-400 transition-transform ${isProfileOpen ? 'rotate-180' : ''}`} />
                </button>

                {/* Dropdown Menu */}
                {isProfileOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-card-hover border border-secondary-100 py-1 animate-in fade-in zoom-in-95 duration-200">
                    <div className="px-4 py-2 border-b border-secondary-100 lg:hidden">
                      <p className="text-sm font-medium text-secondary-900">
                        {user?.first_name} {user?.last_name}
                      </p>
                      <p className="text-xs text-secondary-500 capitalize">{user?.role}</p>
                    </div>
                    <Link
                      to="/profile"
                      className="flex items-center px-4 py-2 text-sm text-secondary-700 hover:bg-secondary-50"
                      onClick={() => setIsProfileOpen(false)}
                    >
                      <User className="mr-2 h-4 w-4" /> Profile
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="flex w-full items-center px-4 py-2 text-sm text-danger-600 hover:bg-danger-50"
                    >
                      <LogOut className="mr-2 h-4 w-4" /> Logout
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <Link
                  to="/login"
                  className="text-secondary-600 hover:text-primary-600 font-medium text-sm transition-colors"
                >
                  Log in
                </Link>
                <Link to="/register" className="btn-primary text-sm py-2 px-4">
                  Get Started
                </Link>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="flex md:hidden">
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="text-secondary-500 hover:text-secondary-900 p-2"
            >
              {isMobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden bg-white border-t border-secondary-100 shadow-lg absolute w-full">
          <div className="px-4 pt-2 pb-4 space-y-1">
            {isAuthenticated ? (
              <>
                <Link
                  to="/dashboard"
                  className="block px-3 py-2 rounded-md text-base font-medium text-secondary-700 hover:text-primary-600 hover:bg-secondary-50"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  Dashboard
                </Link>
                <Link
                  to="/appointments"
                  className="block px-3 py-2 rounded-md text-base font-medium text-secondary-700 hover:text-primary-600 hover:bg-secondary-50"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  Appointments
                </Link>
                {user?.role === "doctor" && (
                  <Link
                    to="/ehr"
                    className="block px-3 py-2 rounded-md text-base font-medium text-secondary-700 hover:text-primary-600 hover:bg-secondary-50"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    EHR
                  </Link>
                )}
                <div className="border-t border-secondary-100 my-2 pt-2">
                  <div className="px-3 py-2 flex items-center gap-3">
                    <div className="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center text-primary-700 font-semibold">
                      {user?.first_name?.charAt(0)}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-secondary-900">
                        {user?.first_name} {user?.last_name}
                      </p>
                      <p className="text-xs text-secondary-500 capitalize">{user?.role}</p>
                    </div>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="w-full text-left block px-3 py-2 rounded-md text-base font-medium text-danger-600 hover:bg-danger-50"
                  >
                    Logout
                  </button>
                </div>
              </>
            ) : (
              <div className="space-y-2 pt-2">
                <Link
                  to="/login"
                  className="block w-full text-center px-4 py-2 border border-secondary-200 rounded-lg text-secondary-700 font-medium hover:bg-secondary-50"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  Log in
                </Link>
                <Link
                  to="/register"
                  className="block w-full text-center px-4 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  Get Started
                </Link>
              </div>
            )}
          </div>
        </div>
      )}
    </header>
  )
}

export default Header