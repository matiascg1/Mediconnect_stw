import type React from "react"
import { Link } from "react-router-dom"
import { Home } from "lucide-react"

const NotFound: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="text-center">
        <h1 className="text-9xl font-bold text-blue-600">404</h1>
        <h2 className="text-3xl font-semibold text-gray-900 mt-4">Page Not Found</h2>
        <p className="text-gray-600 mt-4 mb-8">The page you are looking for does not exist or has been moved.</p>
        <Link
          to="/"
          className="inline-flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition"
        >
          <Home className="h-5 w-5" />
          Back to Home
        </Link>
      </div>
    </div>
  )
}

export default NotFound
