export default function Page() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">MediConnect Backend</h1>
        <p className="text-xl text-gray-600 mb-8">API Services Running</p>
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-2xl">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Access the Frontend</h2>
          <p className="text-gray-600 mb-6">
            The MediConnect frontend application is running separately. Please access it through the configured port
            (default: 3000).
          </p>
          <div className="space-y-2 text-left">
            <p className="text-sm text-gray-500">
              <strong>Frontend:</strong> http://localhost:3000
            </p>
            <p className="text-sm text-gray-500">
              <strong>API Gateway:</strong> http://localhost:8000/api
            </p>
            <p className="text-sm text-gray-500">
              <strong>Status:</strong> <span className="text-green-600 font-semibold">Active</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
