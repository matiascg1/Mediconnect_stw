"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { useAuth } from "../../contexts/AuthContext"
import api from "../../services/api"
import AppointmentCard from "../../components/Cards/AppointmentCard"
import StatCard from "../../components/Cards/StatCard"
import { Calendar, Activity, FileText, Pill, Plus, ChevronRight, Bell } from "lucide-react"

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
          <div className="h-16 w-16 rounded-full border-t-4 border-b-4 border-primary-600 animate-spin"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
            <Activity className="h-6 w-6 text-primary-600" />
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* Welcome Section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-secondary-900 tracking-tight">
            Hello, {user?.first_name}! 👋
          </h1>
          <p className="text-secondary-500 mt-1 text-lg">
            Here's what's happening with your health today.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button className="p-2.5 rounded-full bg-white border border-secondary-200 text-secondary-600 hover:bg-secondary-50 hover:text-primary-600 transition-colors relative">
            <Bell className="h-5 w-5" />
            <span className="absolute top-2 right-2.5 h-2 w-2 bg-red-500 rounded-full border-2 border-white"></span>
          </button>
          <button className="btn-primary flex items-center gap-2 shadow-lg shadow-primary-500/20">
            <Plus className="h-5 w-5" />
            <span>New Appointment</span>
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Upcoming Appointments"
          value={stats.upcoming_appointments}
          icon={<Calendar className="h-6 w-6" />}
          color="blue"
        />
        <StatCard
          title="Past Appointments"
          value={stats.past_appointments}
          icon={<Activity className="h-6 w-6" />}
          color="green"
        />
        <StatCard
          title="Active Prescriptions"
          value={stats.active_prescriptions}
          icon={<Pill className="h-6 w-6" />}
          color="purple"
        />
        <StatCard
          title="Health Records"
          value={stats.ehr_records}
          icon={<FileText className="h-6 w-6" />}
          color="yellow"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content - Recent Appointments */}
        <div className="lg:col-span-2 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-secondary-900">Recent Appointments</h2>
            <button className="text-sm font-medium text-primary-600 hover:text-primary-700 flex items-center gap-1">
              View All <ChevronRight className="h-4 w-4" />
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
            <div className="bg-white rounded-xl border border-secondary-200 p-12 text-center">
              <div className="w-16 h-16 bg-secondary-50 rounded-full flex items-center justify-center mx-auto mb-4">
                <Calendar className="h-8 w-8 text-secondary-400" />
              </div>
              <h3 className="text-lg font-medium text-secondary-900 mb-2">No appointments found</h3>
              <p className="text-secondary-500 mb-6">You don't have any upcoming appointments scheduled.</p>
              <button className="btn-secondary">Schedule Now</button>
            </div>
          )}
        </div>

        {/* Sidebar - Quick Actions & Tips */}
        <div className="space-y-8">
          {/* Quick Actions */}
          <div className="bg-white rounded-xl shadow-card p-6 border border-secondary-100">
            <h3 className="font-bold text-secondary-900 mb-4">Quick Actions</h3>
            <div className="space-y-3">
              <button className="w-full flex items-center justify-between p-3 rounded-lg bg-secondary-50 hover:bg-primary-50 text-secondary-700 hover:text-primary-700 transition-colors group">
                <span className="font-medium">Schedule New Appointment</span>
                <ChevronRight className="h-4 w-4 text-secondary-400 group-hover:text-primary-500" />
              </button>
              <button className="w-full flex items-center justify-between p-3 rounded-lg bg-secondary-50 hover:bg-green-50 text-secondary-700 hover:text-green-700 transition-colors group">
                <span className="font-medium">View Health Records</span>
                <ChevronRight className="h-4 w-4 text-secondary-400 group-hover:text-green-500" />
              </button>
              <button className="w-full flex items-center justify-between p-3 rounded-lg bg-secondary-50 hover:bg-purple-50 text-secondary-700 hover:text-purple-700 transition-colors group">
                <span className="font-medium">Check Prescriptions</span>
                <ChevronRight className="h-4 w-4 text-secondary-400 group-hover:text-purple-500" />
              </button>
            </div>
          </div>

          {/* Health Tips */}
          <div className="bg-gradient-to-br from-primary-600 to-primary-700 rounded-xl shadow-card p-6 text-white relative overflow-hidden">
            <div className="absolute top-0 right-0 -mt-4 -mr-4 w-24 h-24 bg-white opacity-10 rounded-full blur-xl"></div>
            <div className="absolute bottom-0 left-0 -mb-4 -ml-4 w-20 h-20 bg-white opacity-10 rounded-full blur-xl"></div>
            
            <h3 className="font-bold text-lg mb-4 relative z-10">Daily Health Tip</h3>
            <div className="space-y-4 relative z-10">
              <p className="text-primary-50 leading-relaxed">
                "Stay hydrated! Drinking enough water is crucial for many reasons: to regulate body temperature, keep joints lubricated, prevent infections, and deliver nutrients to cells."
              </p>
              <div className="pt-2">
                <button className="text-sm font-medium text-white hover:text-primary-100 flex items-center gap-1">
                  Read more tips <ChevronRight className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PatientDashboard