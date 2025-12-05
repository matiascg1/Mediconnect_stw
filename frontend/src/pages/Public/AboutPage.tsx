import type React from "react"

const AboutPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">About MediConnect</h1>
        <div className="bg-white rounded-lg shadow p-8 space-y-6">
          <p className="text-lg text-gray-700">
            MediConnect is a comprehensive telemedicine platform designed to bridge the gap between patients and
            healthcare providers through innovative digital solutions.
          </p>
          <p className="text-gray-700">
            Our mission is to make healthcare more accessible, efficient, and patient-centered by leveraging modern
            technology to provide seamless medical services.
          </p>
          <div className="mt-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">Our Services</h2>
            <ul className="space-y-3 text-gray-700">
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <span>Virtual consultations with licensed healthcare professionals</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <span>Electronic health records management</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <span>Digital prescription services</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <span>Appointment scheduling and reminders</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AboutPage
