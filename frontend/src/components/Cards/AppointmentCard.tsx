"use client"

import type React from "react"
import { Clock, MapPin } from "lucide-react"

interface AppointmentCardProps {
  appointment: {
    id: number
    appointment_date: string
    status: string
    doctor_first_name: string
    doctor_last_name: string
    doctor_specialty: string
    location?: string // Added for future support
  }
  onCancel?: (id: number) => void
  onReschedule?: (id: number) => void
}

const AppointmentCard: React.FC<AppointmentCardProps> = ({ appointment, onCancel, onReschedule }) => {
  const dateObj = new Date(appointment.appointment_date)
  
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  const getStatusStyles = (status: string) => {
    switch (status.toLowerCase()) {
      case "scheduled":
        return "bg-blue-50 text-blue-700 border-blue-100"
      case "confirmed":
        return "bg-green-50 text-green-700 border-green-100"
      case "cancelled":
        return "bg-red-50 text-red-700 border-red-100"
      case "completed":
        return "bg-secondary-100 text-secondary-700 border-secondary-200"
      default:
        return "bg-secondary-50 text-secondary-700 border-secondary-200"
    }
  }

  return (
    <div className="bg-white border border-secondary-200 rounded-xl p-5 hover:shadow-card-hover transition-all duration-300 group">
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
        {/* Date Box */}
        <div className="flex sm:flex-col items-center sm:items-center justify-center bg-secondary-50 rounded-lg p-3 sm:w-20 border border-secondary-100">
          <span className="text-xs font-semibold text-secondary-500 uppercase tracking-wider">{dateObj.toLocaleDateString("en-US", { month: 'short' })}</span>
          <span className="text-xl font-bold text-secondary-900 sm:mt-1">{dateObj.getDate()}</span>
          <span className="text-xs text-secondary-400 sm:mt-1 hidden sm:block">{dateObj.toLocaleDateString("en-US", { weekday: 'short' })}</span>
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="text-lg font-bold text-secondary-900 truncate">
                Dr. {appointment.doctor_first_name} {appointment.doctor_last_name}
              </h3>
              <p className="text-primary-600 font-medium text-sm mb-2">{appointment.doctor_specialty}</p>
            </div>
            <span className={`px-2.5 py-1 rounded-full text-xs font-semibold border ${getStatusStyles(appointment.status)} capitalize`}>
              {appointment.status}
            </span>
          </div>

          <div className="flex flex-wrap gap-y-2 gap-x-4 mt-2 text-sm text-secondary-500">
            <div className="flex items-center">
              <Clock className="h-4 w-4 mr-1.5 text-secondary-400" />
              {formatTime(dateObj)}
            </div>
            <div className="flex items-center">
              <MapPin className="h-4 w-4 mr-1.5 text-secondary-400" />
              Video Consultation
            </div>
          </div>
        </div>

        {/* Actions */}
        {onCancel && onReschedule && appointment.status === "scheduled" && (
          <div className="flex sm:flex-col gap-2 mt-4 sm:mt-0 sm:ml-2 border-t sm:border-t-0 sm:border-l border-secondary-100 pt-4 sm:pt-0 sm:pl-4">
            <button
              onClick={() => onReschedule(appointment.id)}
              className="flex-1 sm:w-full px-3 py-1.5 text-xs font-medium text-primary-700 bg-primary-50 rounded-lg hover:bg-primary-100 transition-colors"
            >
              Reschedule
            </button>
            <button
              onClick={() => onCancel(appointment.id)}
              className="flex-1 sm:w-full px-3 py-1.5 text-xs font-medium text-red-700 bg-red-50 rounded-lg hover:bg-red-100 transition-colors"
            >
              Cancel
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default AppointmentCard