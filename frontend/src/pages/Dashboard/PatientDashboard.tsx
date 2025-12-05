"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { useAuth } from "../../contexts/AuthContext"
import api from "../../services/api"
import AppointmentCard from "../../components/Cards/AppointmentCard"
import { Calendar, Activity, FileText, Pill, Plus, ChevronRight, Bell, Zap, Heart } from "lucide-react"

interface Appointment {
  id: number
  appointment_date: string
  status: string
  doctor_first_name: string
  doctor_last_name: string
  doctor_specialty: string
}

interface DashboardStats {
  upcoming_appointments: number
  past_appointments: number
  active_prescriptions: number
  ehr_records: number
}

const PatientDashboard: React.FC = () => {
  const { user } = useAuth()
  const [appointments, setAppointments] = useState<Appointment[]>([])
  const [stats, setStats] = useState<DashboardStats>({
    upcoming_appointments: 0,
    past_appointments: 0,
    active_prescriptions: 0,
    ehr_records: 0,
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)

      // Fetch appointments
      const appointmentsRes = await api.get("/appointments")
      const appointmentsData = appointmentsRes.data.appointments || []
      setAppointments(appointmentsData.slice(0, 5)) // Show only 5 latest

      // Calculate stats
      const now = new Date()
      const upcoming = appointmentsData.filter(
        (apt: Appointment) => new Date(apt.appointment_date) > now && apt.status !== "cancelled",
      ).length

      const past = appointmentsData.filter(
        (apt: Appointment) => new Date(apt.appointment_date) <= now || apt.status === "completed",
      ).length

      // Fetch prescriptions
      const prescriptionsRes = await api.get("/prescriptions/patient/active")
      const activePrescriptions = prescriptionsRes.data.count || 0

      // Fetch EHR records
      const ehrRes = await api.get("/ehr/patient/history")
      const ehrRecords = ehrRes.data.count || 0

      setStats({
        upcoming_appointments: upcoming,
        past_appointments: past,
        active_prescriptions: activePrescriptions,
        ehr_records: ehrRecords,
      })
    } catch (error) {
      console.error("Error fetching dashboard data:", error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-[calc(100vh-200px)]">
        <div className="relative">
          <div className="h-20 w-20 rounded-full border-4 border-primary-600/20 border-t-primary-600 animate-spin"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
            <Activity className="h-8 w-8 text-primary-600 animate-pulse" />
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* Welcome Section */}
      <div className="relative overflow-hidden rounded-2xl gradient-primary p-8 text-white shadow-xl">
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -mr-32 -mt-32"></div>
        <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/5 rounded-full -ml-24 -mb-24"></div>

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold tracking-tight mb-2">Welcome back, {user?.first_name}! 👋</h1>
            <p className="text-primary-100 text-lg">Here's your health overview for today</p>
          </div>
          <div className="flex items-center gap-3">
            <button className="p-3 rounded-xl bg-white/20 backdrop-blur-sm text-white hover:bg-white/30 transition-colors relative group">
              <Bell className="h-5 w-5" />
              <span className="absolute top-2 right-2 h-2 w-2 bg-red-500 rounded-full ring-2 ring-white"></span>
              <span className="absolute -top-1 -right-1 px-1.5 py-0.5 bg-red-500 text-white text-xs rounded-full font-bold opacity-0 group-hover:opacity-100 transition-opacity">
                3
              </span>
            </button>
            <button className="flex items-center gap-2 px-6 py-3 bg-white text-primary-900 rounded-xl font-semibold hover:bg-primary-50 transition-all shadow-lg hover:shadow-xl">
              <Plus className="h-5 w-5" />
              <span className="hidden sm:inline">New Appointment</span>
            </button>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card p-6 border-l-4 border-blue-500">
          <div className="flex items-start justify-between mb-4">
            <div className="p-3 bg-blue-50 rounded-xl">
              <Calendar className="h-6 w-6 text-blue-600" />
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-secondary-900">{stats.upcoming_appointments}</div>
              <div className="text-sm text-secondary-500 mt-1">Upcoming</div>
            </div>
          </div>
          <div className="text-sm font-medium text-secondary-700">Next Appointments</div>
        </div>

        <div className="card p-6 border-l-4 border-green-500">
          <div className="flex items-start justify-between mb-4">
            <div className="p-3 bg-green-50 rounded-xl">
              <Activity className="h-6 w-6 text-green-600" />
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-secondary-900">{stats.past_appointments}</div>
              <div className="text-sm text-secondary-500 mt-1">Completed</div>
            </div>
          </div>
          <div className="text-sm font-medium text-secondary-700">Past Visits</div>
        </div>

        <div className="card p-6 border-l-4 border-purple-500">
          <div className="flex items-start justify-between mb-4">
            <div className="p-3 bg-purple-50 rounded-xl">
              <Pill className="h-6 w-6 text-purple-600" />
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-secondary-900">{stats.active_prescriptions}</div>
              <div className="text-sm text-secondary-500 mt-1">Active</div>
            </div>
          </div>
          <div className="text-sm font-medium text-secondary-700">Prescriptions</div>
        </div>

        <div className="card p-6 border-l-4 border-amber-500">
          <div className="flex items-start justify-between mb-4">
            <div className="p-3 bg-amber-50 rounded-xl">
              <FileText className="h-6 w-6 text-amber-600" />
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-secondary-900">{stats.ehr_records}</div>
              <div className="text-sm text-secondary-500 mt-1">Records</div>
            </div>
          </div>
          <div className="text-sm font-medium text-secondary-700">Health Records</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content - Recent Appointments */}
        <div className="lg:col-span-2 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-secondary-900">Recent Appointments</h2>
            <button className="text-sm font-semibold text-primary-600 hover:text-primary-700 flex items-center gap-1 group">
              View All
              <ChevronRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>

          {appointments.length > 0 ? (
            <div className="space-y-4">
              {appointments.map((appointment) => (
                <AppointmentCard
                  key={appointment.id}
                  appointment={appointment}
                  onCancel={() => {
                    /* Handle cancel */
                  }}
                  onReschedule={() => {
                    /* Handle reschedule */
                  }}
                />
              ))}
            </div>
          ) : (
            <div className="card p-12 text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-blue-50 to-cyan-50 rounded-full flex items-center justify-center mx-auto mb-4">
                <Calendar className="h-10 w-10 text-primary-600" />
              </div>
              <h3 className="text-xl font-bold text-secondary-900 mb-2">No appointments yet</h3>
              <p className="text-secondary-500 mb-6">Schedule your first appointment with one of our specialists</p>
              <button className="btn-primary">Schedule Now</button>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <div className="card p-6">
            <h3 className="font-bold text-lg text-secondary-900 mb-4 flex items-center gap-2">
              <Zap className="h-5 w-5 text-amber-500" />
              Quick Actions
            </h3>
            <div className="space-y-2">
              {[
                { label: "Schedule Appointment", icon: <Calendar className="h-4 w-4" />, color: "blue" },
                { label: "View Health Records", icon: <FileText className="h-4 w-4" />, color: "green" },
                { label: "Check Prescriptions", icon: <Pill className="h-4 w-4" />, color: "purple" },
                { label: "Message Doctor", icon: <Activity className="h-4 w-4" />, color: "cyan" },
              ].map((action, idx) => (
                <button
                  key={idx}
                  className="w-full flex items-center justify-between p-3 rounded-xl bg-secondary-50 hover:bg-primary-50 text-secondary-700 hover:text-primary-700 transition-all group"
                >
                  <span className="flex items-center gap-3 font-medium">
                    <span className={`text-${action.color}-600`}>{action.icon}</span>
                    {action.label}
                  </span>
                  <ChevronRight className="h-4 w-4 text-secondary-400 group-hover:text-primary-500 group-hover:translate-x-1 transition-all" />
                </button>
              ))}
            </div>
          </div>

          {/* Health Tip */}
          <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-emerald-500 via-teal-600 to-cyan-600 p-6 text-white shadow-xl">
            <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16"></div>
            <div className="absolute bottom-0 left-0 w-24 h-24 bg-white/10 rounded-full -ml-12 -mb-12"></div>

            <div className="relative z-10">
              <div className="flex items-center gap-2 mb-4">
                <Heart className="h-5 w-5" />
                <h3 className="font-bold text-lg">Daily Health Tip</h3>
              </div>
              <p className="text-emerald-50 leading-relaxed mb-4">
                Stay hydrated! Drinking enough water helps regulate body temperature, keep joints lubricated, and
                deliver nutrients to cells.
              </p>
              <button className="text-sm font-semibold text-white hover:text-emerald-100 flex items-center gap-1 group">
                Read more tips
                <ChevronRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PatientDashboard
