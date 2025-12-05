"use client"

import type React from "react"
import { Link } from "react-router-dom"
import {
  Activity,
  Calendar,
  FileText,
  Users,
  ArrowRight,
  Shield,
  Check,
  Star,
  Clock,
  Heart,
  Zap,
  Award,
} from "lucide-react"

const HomePage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-white via-blue-50/30 to-white">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass">
        <div className="container-custom py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="bg-gradient-to-br from-primary-600 to-primary-700 text-white p-2 rounded-xl shadow-lg">
                <Activity className="h-6 w-6" />
              </div>
              <span className="text-2xl font-bold text-secondary-900 tracking-tight">
                Medi<span className="text-primary-600">Connect</span>
              </span>
            </div>
            <div className="hidden md:flex items-center gap-8">
              <Link to="about" className="text-secondary-600 hover:text-primary-600 font-medium transition-colors">
                About
              </Link>
              <Link to="/contact" className="text-secondary-600 hover:text-primary-600 font-medium transition-colors">
                Contact
              </Link>
              <Link to="/login" className="text-secondary-700 hover:text-primary-600 font-medium transition-colors">
                Sign In
              </Link>
              <Link to="/register" className="btn-primary text-sm">
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="relative overflow-hidden pt-32 pb-20 sm:pt-40 sm:pb-32">
        {/* Background Decoration */}
        <div className="absolute inset-0 -z-10">
          <div className="absolute top-20 right-0 w-96 h-96 bg-primary-200/30 rounded-full blur-3xl"></div>
          <div className="absolute bottom-0 left-0 w-96 h-96 bg-cyan-200/30 rounded-full blur-3xl"></div>
        </div>

        <div className="container-custom">
          <div className="text-center max-w-5xl mx-auto">
            {/* Badge */}
            <div className="inline-flex items-center px-4 py-2 rounded-full bg-gradient-to-r from-primary-50 to-cyan-50 border border-primary-100 text-primary-700 text-sm font-semibold mb-8 shadow-sm">
              <span className="flex h-2 w-2 rounded-full bg-primary-600 mr-2 animate-pulse"></span>
              Trusted by 10,000+ patients worldwide
            </div>

            {/* Main Headline */}
            <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-bold tracking-tight text-secondary-900 mb-8 leading-[1.1]">
              Healthcare
              <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-600 via-cyan-600 to-teal-600">
                reimagined
              </span>
            </h1>

            <p className="text-xl md:text-2xl text-secondary-600 mb-12 max-w-3xl mx-auto leading-relaxed">
              Experience seamless medical care with MediConnect. Schedule appointments, access records, and consult with
              specialists—all from one secure platform.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row justify-center gap-4 mb-16">
              <Link to="/register" className="btn-primary text-lg px-10 py-4 shine-effect">
                Start Free Today
                <ArrowRight className="inline ml-2 h-5 w-5" />
              </Link>
              <Link to="/login" className="btn-secondary text-lg px-10 py-4">
                Patient Login
              </Link>
            </div>

            {/* Trust Indicators */}
            <div className="flex flex-wrap items-center justify-center gap-8 text-sm text-secondary-500">
              <div className="flex items-center gap-2">
                <Check className="h-5 w-5 text-green-600" />
                <span>No credit card required</span>
              </div>
              <div className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-primary-600" />
                <span>HIPAA compliant</span>
              </div>
              <div className="flex items-center gap-2">
                <Star className="h-5 w-5 text-yellow-500" />
                <span>4.9/5 rating</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="bg-gradient-to-br from-primary-900 via-primary-800 to-cyan-900 relative overflow-hidden">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmZmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0iTTM2IDM0di00aC0ydjRoLTR2Mmg0djRoMnYtNGg0di0yaC00em0wLTMwVjBoLTJ2NGgtNHYyaDR2NGgyVjZoNFY0aC00ek02IDM0di00SDR2NEgwdjJoNHY0aDJ2LTRoNHYtMkg2ek02IDRWMEg0djRIMHYyaDR2NGgyVjZoNFY0SDZ6Ii8+PC9nPjwvZz48L3N2Zz4=')] opacity-10"></div>
        <div className="container-custom py-16 relative">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 md:gap-12">
            {[
              { label: "Active Patients", value: "10,000+", icon: <Users className="h-6 w-6" /> },
              { label: "Expert Doctors", value: "500+", icon: <Award className="h-6 w-6" /> },
              { label: "Consultations", value: "50,000+", icon: <Activity className="h-6 w-6" /> },
              { label: "Patient Satisfaction", value: "98%", icon: <Heart className="h-6 w-6" /> },
            ].map((stat, index) => (
              <div key={index} className="text-center">
                <div className="inline-flex items-center justify-center w-12 h-12 bg-white/10 rounded-xl mb-3 text-white">
                  {stat.icon}
                </div>
                <div className="text-4xl md:text-5xl font-bold text-white mb-1">{stat.value}</div>
                <div className="text-sm font-medium text-primary-200 uppercase tracking-wide">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div className="py-24 md:py-32">
        <div className="container-custom">
          <div className="text-center mb-16">
            <div className="inline-block px-4 py-1.5 rounded-full bg-primary-50 text-primary-700 text-sm font-semibold mb-4">
              Features
            </div>
            <h2 className="text-4xl md:text-5xl font-bold text-secondary-900 mb-4">
              Everything you need for
              <br />
              better health
            </h2>
            <p className="text-lg md:text-xl text-secondary-600 max-w-2xl mx-auto">
              Our platform provides a comprehensive suite of tools to manage your healthcare journey.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: <Calendar className="h-7 w-7" />,
                title: "Easy Scheduling",
                description:
                  "Book appointments instantly with your preferred doctors. Get reminders and manage reschedules effortlessly.",
                color: "from-blue-500 to-cyan-500",
              },
              {
                icon: <FileText className="h-7 w-7" />,
                title: "Digital Records",
                description:
                  "Access your complete medical history, lab results, and vaccination records securely from anywhere.",
                color: "from-purple-500 to-pink-500",
              },
              {
                icon: <Zap className="h-7 w-7" />,
                title: "E-Prescriptions",
                description: "Receive prescriptions digitally and have them sent directly to your preferred pharmacy.",
                color: "from-amber-500 to-orange-500",
              },
              {
                icon: <Users className="h-7 w-7" />,
                title: "Expert Network",
                description:
                  "Connect with a wide network of qualified healthcare professionals across various specialties.",
                color: "from-teal-500 to-emerald-500",
              },
              {
                icon: <Shield className="h-7 w-7" />,
                title: "Secure & Private",
                description:
                  "Your health data is protected with enterprise-grade encryption and full HIPAA compliance.",
                color: "from-indigo-500 to-blue-500",
              },
              {
                icon: <Clock className="h-7 w-7" />,
                title: "24/7 Support",
                description: "Get help whenever you need it with our round-the-clock patient support team.",
                color: "from-rose-500 to-red-500",
              },
            ].map((feature, index) => (
              <div key={index} className="group card p-8 hover:scale-105 transition-all duration-300 cursor-pointer">
                <div
                  className={`w-14 h-14 bg-gradient-to-br ${feature.color} rounded-2xl flex items-center justify-center mb-6 text-white shadow-lg group-hover:scale-110 transition-transform duration-300`}
                >
                  {feature.icon}
                </div>
                <h3 className="text-xl font-bold text-secondary-900 mb-3">{feature.title}</h3>
                <p className="text-secondary-600 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="py-24 bg-secondary-50">
        <div className="container-custom">
          <div className="relative overflow-hidden rounded-3xl gradient-primary p-12 md:p-20 text-center shadow-2xl">
            {/* Decoration */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -mr-32 -mt-32 blur-2xl"></div>
            <div className="absolute bottom-0 left-0 w-64 h-64 bg-white/10 rounded-full -ml-32 -mb-32 blur-2xl"></div>

            <div className="relative z-10">
              <h2 className="text-3xl md:text-5xl font-bold text-white mb-6">
                Ready to take control of
                <br className="hidden md:block" /> your health?
              </h2>
              <p className="text-primary-100 text-lg md:text-xl mb-10 max-w-2xl mx-auto">
                Join thousands of patients who trust MediConnect for their healthcare needs.
              </p>
              <Link
                to="/register"
                className="inline-flex items-center px-10 py-4 bg-white text-primary-900 rounded-xl text-lg font-bold hover:bg-primary-50 transition-all shadow-xl hover:shadow-2xl hover:-translate-y-1"
              >
                Create Free Account
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-secondary-900 text-secondary-300 py-12">
        <div className="container-custom">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <div className="bg-primary-600 text-white p-1.5 rounded-lg">
                <Activity className="h-5 w-5" />
              </div>
              <span className="text-xl font-bold text-white">
                Medi<span className="text-primary-400">Connect</span>
              </span>
            </div>
            <div className="text-sm">© 2025 MediConnect. All rights reserved.</div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default HomePage
