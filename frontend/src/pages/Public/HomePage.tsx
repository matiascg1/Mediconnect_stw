import type React from "react"
import { Link } from "react-router-dom"
import { Activity, Calendar, FileText, Users, ArrowRight, Shield, Smartphone } from "lucide-react"

const HomePage: React.FC = () => {
  return (
    <div className="min-h-screen bg-secondary-50">
      {/* Hero Section */}
      <div className="relative overflow-hidden bg-white">
        <div className="absolute inset-0 bg-hero-pattern opacity-10"></div>
        <div className="absolute inset-0 bg-gradient-to-b from-white/0 via-white/50 to-secondary-50"></div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-24 sm:pt-24 sm:pb-32">
          <div className="text-center max-w-4xl mx-auto">
            <div className="inline-flex items-center px-4 py-2 rounded-full bg-primary-50 text-primary-700 text-sm font-medium mb-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
              <span className="flex h-2 w-2 rounded-full bg-primary-600 mr-2"></span>
              Now available for all patients
            </div>
            
            <h1 className="text-5xl sm:text-6xl md:text-7xl font-bold tracking-tight text-secondary-900 mb-8 animate-in fade-in slide-in-from-bottom-8 duration-1000">
              Healthcare reimagined for the <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-600 to-primary-400">digital age</span>
            </h1>
            
            <p className="text-xl text-secondary-600 mb-10 max-w-2xl mx-auto leading-relaxed animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-200">
              Experience seamless medical care with MediConnect. Schedule appointments, access records, and consult with top specialists—all from one secure platform.
            </p>
            
            <div className="flex flex-col sm:flex-row justify-center gap-4 animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-300">
              <Link
                to="/register"
                className="btn-primary text-lg px-8 py-4 shadow-lg shadow-primary-500/20 hover:shadow-primary-500/40 transform hover:-translate-y-1 transition-all"
              >
                Get Started Now
              </Link>
              <Link
                to="/login"
                className="btn-secondary text-lg px-8 py-4 hover:bg-white transform hover:-translate-y-1 transition-all"
              >
                Patient Login
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="bg-white border-y border-secondary-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            {[
              { label: "Active Patients", value: "10k+" },
              { label: "Qualified Doctors", value: "500+" },
              { label: "Consultations", value: "50k+" },
              { label: "Patient Satisfaction", value: "98%" },
            ].map((stat, index) => (
              <div key={index} className="flex flex-col">
                <dt className="text-3xl font-bold text-secondary-900">{stat.value}</dt>
                <dd className="text-sm font-medium text-secondary-500 uppercase tracking-wide mt-1">{stat.label}</dd>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div className="py-24 bg-secondary-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-secondary-900 sm:text-4xl mb-4">Everything you need for better health</h2>
            <p className="text-lg text-secondary-600 max-w-2xl mx-auto">
              Our platform provides a comprehensive suite of tools to manage your healthcare journey effectively.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: <Calendar className="h-6 w-6 text-primary-600" />,
                title: "Easy Scheduling",
                description: "Book appointments with your preferred doctors instantly. Get reminders and manage reschedules effortlessly."
              },
              {
                icon: <FileText className="h-6 w-6 text-primary-600" />,
                title: "Digital Records",
                description: "Access your complete medical history, lab results, and vaccination records securely from anywhere."
              },
              {
                icon: <Activity className="h-6 w-6 text-primary-600" />,
                title: "E-Prescriptions",
                description: "Receive prescriptions digitally and have them sent directly to your preferred pharmacy."
              },
              {
                icon: <Users className="h-6 w-6 text-primary-600" />,
                title: "Expert Network",
                description: "Connect with a wide network of qualified healthcare professionals across various specialties."
              },
              {
                icon: <Shield className="h-6 w-6 text-primary-600" />,
                title: "Secure & Private",
                description: "Your health data is protected with enterprise-grade encryption and full HIPAA compliance."
              },
              {
                icon: <Smartphone className="h-6 w-6 text-primary-600" />,
                title: "Mobile Friendly",
                description: "Manage your health on the go with our fully responsive mobile interface."
              }
            ].map((feature, index) => (
              <div key={index} className="bg-white p-8 rounded-2xl shadow-card hover:shadow-card-hover transition-all duration-300 group">
                <div className="w-12 h-12 bg-primary-50 rounded-xl flex items-center justify-center mb-6 group-hover:bg-primary-600 group-hover:text-white transition-colors duration-300">
                  <div className="group-hover:text-white transition-colors duration-300">
                    {feature.icon}
                  </div>
                </div>
                <h3 className="text-xl font-bold text-secondary-900 mb-3">{feature.title}</h3>
                <p className="text-secondary-600 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-white py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-primary-900 rounded-3xl overflow-hidden relative">
            <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?ixlib=rb-1.2.1&auto=format&fit=crop&w=2850&q=80')] bg-cover bg-center opacity-10 mix-blend-overlay"></div>
            <div className="relative px-8 py-16 md:py-20 md:px-16 text-center md:text-left flex flex-col md:flex-row items-center justify-between gap-8">
              <div className="max-w-2xl">
                <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Ready to take control of your health?</h2>
                <p className="text-primary-100 text-lg">Join thousands of patients who trust MediConnect for their healthcare needs.</p>
              </div>
              <div className="flex-shrink-0">
                <Link
                  to="/register"
                  className="inline-flex items-center px-8 py-4 border border-transparent text-lg font-medium rounded-xl text-primary-900 bg-white hover:bg-primary-50 transition-colors shadow-lg"
                >
                  Create Free Account
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default HomePage