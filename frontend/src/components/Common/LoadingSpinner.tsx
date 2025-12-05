import type React from "react"

const LoadingSpinner: React.FC = () => {
  return (
    <div className="flex justify-center items-center min-h-screen">
      <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600"></div>
    </div>
  )
}

export default LoadingSpinner
