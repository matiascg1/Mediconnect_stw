"use client"

import type React from "react"
import { useAuth } from "../../contexts/AuthContext"
import { Calendar, Users, FileText, Activity } from "lucide-react"

const DoctorDashboard: React.FC = () => {
  const { user } = useAuth()

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome, Dr. {user?.first_name} {user?.last_name}
        </h1>
        <p className="text-gray-600 mt-2">Manage your patients and appointments</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Today's Appointments</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">8</p>
            </div>
            <div className="bg-blue-100 p-3 rounded-full">
              <Calendar className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Patients</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">127</p>
            </div>
            <div className="bg-green-100 p-3 rounded-full">
              <Users className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Pending Records</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">5</p>
            </div>
            <div className="bg-purple-100 p-3 rounded-full">
              <FileText className="h-6 w-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Cases</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">42</p>
            </div>
            <div className="bg-yellow-100 p-3 rounded-full">
              <Activity className="h-6 w-6 text-yellow-600" />
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Upcoming Appointments</h2>
        <p className="text-gray-500">No appointments scheduled for today</p>
      </div>
    </div>
  )
}

export default DoctorDashboard
