import type React from "react"
import { ArrowUpRight, ArrowDownRight } from "lucide-react"

interface StatCardProps {
  title: string
  value: number | string
  icon: React.ReactNode
  color: "blue" | "green" | "purple" | "yellow" | "red"
  trend?: { value: string; isPositive: boolean } // Optional trend for future use
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, color, trend }) => {
  const colorStyles = {
    blue: { bg: "bg-blue-50", text: "text-blue-600", border: "border-blue-100" },
    green: { bg: "bg-green-50", text: "text-green-600", border: "border-green-100" },
    purple: { bg: "bg-purple-50", text: "text-purple-600", border: "border-purple-100" },
    yellow: { bg: "bg-yellow-50", text: "text-yellow-600", border: "border-yellow-100" },
    red: { bg: "bg-red-50", text: "text-red-600", border: "border-red-100" },
  }

  const style = colorStyles[color]

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border border-secondary-100 hover:shadow-md transition-all duration-300 group">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-secondary-500 mb-1">{title}</p>
          <h3 className="text-2xl font-bold text-secondary-900 tracking-tight">{value}</h3>
          
          {trend && (
            <div className={`flex items-center mt-2 text-xs font-medium ${trend.isPositive ? 'text-green-600' : 'text-red-600'}`}>
              {trend.isPositive ? <ArrowUpRight className="h-3 w-3 mr-1" /> : <ArrowDownRight className="h-3 w-3 mr-1" />}
              <span>{trend.value}</span>
              <span className="text-secondary-400 ml-1">vs last month</span>
            </div>
          )}
        </div>
        
        <div className={`p-3 rounded-xl ${style.bg} ${style.text} group-hover:scale-110 transition-transform duration-300`}>
          {icon}
        </div>
      </div>
    </div>
  )
}

export default StatCard