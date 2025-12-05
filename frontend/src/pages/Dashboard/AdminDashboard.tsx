"use client"

import type React from "react"
import { useAuth } from "../../contexts/AuthContext"
import { Users, Activity, Calendar, TrendingUp } from "lucide-react"

const AdminDashboard: React.FC = () => {
  const { user } = useAuth()

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard - Welcome, {user?.first_name}</h1>
        <p className="text-gray-600 mt-2">System overview and management</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Users</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">1,234</p>
            </div>
            <div className="bg-blue-100 p-3 rounded-full">
              <Users className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Sessions</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">89</p>
            </div>
            <div className="bg-green-100 p-3 rounded-full">
              <Activity className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Appointments</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">456</p>
            </div>
            <div className="bg-purple-100 p-3 rounded-full">
              <Calendar className="h-6 w-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Growth Rate</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">+12%</p>
            </div>
            <div className="bg-yellow-100 p-3 rounded-full">
              <TrendingUp className="h-6 w-6 text-yellow-600" />
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h2>
          <p className="text-gray-500">System activity logs will appear here</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="space-y-3">
            <button className="w-full text-left px-4 py-3 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100">
              Manage Users
            </button>
            <button className="w-full text-left px-4 py-3 bg-green-50 text-green-700 rounded-lg hover:bg-green-100">
              View Reports
            </button>
            <button className="w-full text-left px-4 py-3 bg-purple-50 text-purple-700 rounded-lg hover:bg-purple-100">
              System Settings
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AdminDashboard
