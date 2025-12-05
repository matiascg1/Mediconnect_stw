"use client"

import type React from "react"
import { useAuth } from "../../contexts/AuthContext"
import { Calendar, Users, FileText, Activity, Clock, TrendingUp, AlertCircle, CheckCircle } from "lucide-react"

const DoctorDashboard: React.FC = () => {
  const { user } = useAuth()

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* Welcome Header */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-indigo-900 via-purple-900 to-indigo-800 p-8 text-white shadow-xl">
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -mr-32 -mt-32"></div>
        <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/5 rounded-full -ml-24 -mb-24"></div>

        <div className="relative z-10">
          <h1 className="text-3xl md:text-4xl font-bold mb-2">
            Welcome, Dr. {user?.first_name} {user?.last_name} 👨‍⚕️
          </h1>
          <p className="text-purple-100 text-lg">You have 8 appointments scheduled for today</p>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card p-6 border-l-4 border-blue-500">
          <div className="flex items-start justify-between mb-4">
            <div className="p-3 bg-blue-50 rounded-xl">
              <Calendar className="h-6 w-6 text-blue-600" />
            </div>
            <div className="px-3 py-1 bg-blue-50 text-blue-700 text-sm font-semibold rounded-full">Today</div>
          </div>
          <div className="text-3xl font-bold text-secondary-900 mb-1">8</div>
          <div className="text-sm font-medium text-secondary-600">Today's Appointments</div>
          <div className="mt-3 flex items-center gap-1 text-sm text-green-600">
            <TrendingUp className="h-4 w-4" />
            <span className="font-medium">+12% from yesterday</span>
          </div>
        </div>

        <div className="card p-6 border-l-4 border-green-500">
          <div className="flex items-start justify-between mb-4">
            <div className="p-3 bg-green-50 rounded-xl">
              <Users className="h-6 w-6 text-green-600" />
            </div>
            <div className="px-3 py-1 bg-green-50 text-green-700 text-sm font-semibold rounded-full">Active</div>
          </div>
          <div className="text-3xl font-bold text-secondary-900 mb-1">127</div>
          <div className="text-sm font-medium text-secondary-600">Total Patients</div>
          <div className="mt-3 flex items-center gap-1 text-sm text-green-600">
            <TrendingUp className="h-4 w-4" />
            <span className="font-medium">+5 new this week</span>
          </div>
        </div>

        <div className="card p-6 border-l-4 border-amber-500">
          <div className="flex items-start justify-between mb-4">
            <div className="p-3 bg-amber-50 rounded-xl">
              <AlertCircle className="h-6 w-6 text-amber-600" />
            </div>
            <div className="px-3 py-1 bg-amber-50 text-amber-700 text-sm font-semibold rounded-full">Pending</div>
          </div>
          <div className="text-3xl font-bold text-secondary-900 mb-1">5</div>
          <div className="text-sm font-medium text-secondary-600">Pending Records</div>
          <div className="mt-3 text-sm text-secondary-500">Requires attention</div>
        </div>

        <div className="card p-6 border-l-4 border-purple-500">
          <div className="flex items-start justify-between mb-4">
            <div className="p-3 bg-purple-50 rounded-xl">
              <Activity className="h-6 w-6 text-purple-600" />
            </div>
            <div className="px-3 py-1 bg-purple-50 text-purple-700 text-sm font-semibold rounded-full">Active</div>
          </div>
          <div className="text-3xl font-bold text-secondary-900 mb-1">42</div>
          <div className="text-sm font-medium text-secondary-600">Active Cases</div>
          <div className="mt-3 text-sm text-secondary-500">Under treatment</div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Today's Schedule */}
        <div className="lg:col-span-2 card p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-secondary-900 flex items-center gap-2">
              <Clock className="h-5 w-5 text-primary-600" />
              Today's Schedule
            </h2>
            <button className="text-sm font-semibold text-primary-600 hover:text-primary-700">View All</button>
          </div>

          <div className="space-y-4">
            {[
              { time: "09:00 AM", patient: "John Smith", type: "Checkup", status: "confirmed" },
              { time: "10:30 AM", patient: "Emma Davis", type: "Follow-up", status: "confirmed" },
              { time: "02:00 PM", patient: "Michael Brown", type: "Consultation", status: "pending" },
            ].map((apt, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-4 rounded-xl bg-secondary-50 hover:bg-primary-50 transition-colors group"
              >
                <div className="flex items-center gap-4">
                  <div className="text-center">
                    <div className="text-sm font-semibold text-secondary-900">{apt.time.split(" ")[0]}</div>
                    <div className="text-xs text-secondary-500">{apt.time.split(" ")[1]}</div>
                  </div>
                  <div className="h-12 w-px bg-secondary-200"></div>
                  <div>
                    <div className="font-semibold text-secondary-900">{apt.patient}</div>
                    <div className="text-sm text-secondary-500">{apt.type}</div>
                  </div>
                </div>
                <div
                  className={`px-3 py-1 rounded-full text-xs font-semibold ${
                    apt.status === "confirmed" ? "bg-green-100 text-green-700" : "bg-amber-100 text-amber-700"
                  }`}
                >
                  {apt.status === "confirmed" ? (
                    <CheckCircle className="h-3 w-3 inline mr-1" />
                  ) : (
                    <Clock className="h-3 w-3 inline mr-1" />
                  )}
                  {apt.status}
                </div>
              </div>
            ))}

            <div className="text-center py-8 text-secondary-500">
              <Calendar className="h-12 w-12 mx-auto mb-3 opacity-50" />
              <p>No more appointments for today</p>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="space-y-6">
          <div className="card p-6">
            <h3 className="font-bold text-lg text-secondary-900 mb-4">Recent Activity</h3>
            <div className="space-y-4">
              {[
                { type: "New patient", name: "Sarah Wilson", time: "2h ago", icon: <Users className="h-4 w-4" /> },
                { type: "Record updated", name: "John Smith", time: "4h ago", icon: <FileText className="h-4 w-4" /> },
                {
                  type: "Prescription sent",
                  name: "Emma Davis",
                  time: "6h ago",
                  icon: <Activity className="h-4 w-4" />,
                },
              ].map((activity, idx) => (
                <div key={idx} className="flex items-start gap-3">
                  <div className="p-2 bg-primary-50 rounded-lg text-primary-600">{activity.icon}</div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-secondary-900">{activity.type}</p>
                    <p className="text-sm text-secondary-500 truncate">{activity.name}</p>
                  </div>
                  <span className="text-xs text-secondary-400">{activity.time}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Stats */}
          <div className="card p-6 bg-gradient-to-br from-primary-600 to-primary-700 text-white">
            <h3 className="font-bold text-lg mb-4">Performance This Month</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-primary-100">Patients Seen</span>
                <span className="text-2xl font-bold">156</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-primary-100">Avg. Rating</span>
                <span className="text-2xl font-bold">4.9⭐</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-primary-100">Response Time</span>
                <span className="text-2xl font-bold">12m</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DoctorDashboard
