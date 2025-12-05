"use client"

import type React from "react"
import { useState } from "react"
import { useNavigate, Link } from "react-router-dom"
import { useAuth } from "../contexts/AuthContext"
import { LoginForm } from "../components/Forms/LoginForm"
import { Activity, ArrowLeft } from "lucide-react"

const LoginPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleLogin = async (data: { correo: string; password: string }) => {
    setIsLoading(true)
    try {
      await login(data.correo, data.password)

      // Redirigir según el rol
      const user = JSON.parse(localStorage.getItem("user") || "{}")
      switch (user.role) {
        case "patient":
          navigate("/dashboard")
          break
        case "doctor":
          navigate("/dashboard")
          break
        case "admin":
          navigate("/dashboard")
          break
        default:
          navigate("/")
      }
    } catch (error: any) {
      console.error(error.message || "Error al iniciar sesión")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-secondary-50 flex flex-col lg:flex-row">
      {/* Left Side - Form */}
      <div className="flex-1 flex flex-col justify-center py-12 px-4 sm:px-6 lg:flex-none lg:px-20 xl:px-24 bg-white z-10">
        <div className="mx-auto w-full max-w-sm lg:w-96">
          <div className="mb-10">
            <Link to="/" className="inline-flex items-center text-sm text-secondary-500 hover:text-primary-600 transition-colors mb-8">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Home
            </Link>
            <div className="flex items-center gap-2 mb-6">
              <div className="bg-primary-600 text-white p-1.5 rounded-lg">
                <Activity className="h-6 w-6" />
              </div>
              <span className="text-2xl font-bold text-secondary-900 tracking-tight">
                Medi<span className="text-primary-600">Connect</span>
              </span>
            </div>
            <h2 className="text-3xl font-bold tracking-tight text-secondary-900">
              Welcome back
            </h2>
            <p className="mt-2 text-sm text-secondary-600">
              Please enter your details to sign in.
            </p>
          </div>

          <div className="mt-8">
            <LoginForm onSubmit={handleLogin} isLoading={isLoading} />

            <div className="mt-6">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-secondary-200" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-white text-secondary-500">Don't have an account?</span>
                </div>
              </div>

              <div className="mt-6">
                <Link
                  to="/register"
                  className="w-full flex justify-center py-2.5 px-4 border border-secondary-300 rounded-lg shadow-sm text-sm font-medium text-secondary-700 bg-white hover:bg-secondary-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-all"
                >
                  Create an account
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right Side - Image/Background */}
      <div className="hidden lg:block relative flex-1 bg-secondary-900">
        <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1576091160550-2173dba999ef?ixlib=rb-1.2.1&auto=format&fit=crop&w=2850&q=80')] bg-cover bg-center opacity-40 mix-blend-overlay"></div>
        <div className="absolute inset-0 bg-gradient-to-t from-primary-900/90 to-primary-800/50"></div>
        <div className="relative h-full flex flex-col justify-end p-12 text-white">
          <blockquote className="mb-8">
            <p className="text-2xl font-medium leading-relaxed">
              "MediConnect has transformed how I manage my healthcare. The ease of scheduling appointments and accessing my records is unmatched."
            </p>
            <footer className="mt-4">
              <div className="font-semibold text-lg">Sarah Johnson</div>
              <div className="text-primary-200">Verified Patient</div>
            </footer>
          </blockquote>
        </div>
      </div>
    </div>
  )
}

export default LoginPage