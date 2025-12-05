"use client"

import type React from "react"
import { useState } from "react"
import { Link } from "react-router-dom"
import { useAuth } from "../contexts/AuthContext"
import { RegisterForm } from "../components/Forms/RegisterForm"
import toast from "react-hot-toast"
import { FaUserPlus } from "react-icons/fa"

const RegisterPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false)
  const { register } = useAuth()

  const handleRegister = async (data: any) => {
    setIsLoading(true)
    try {
      await register(data)
      toast.success("¡Registro exitoso! Bienvenido a MediConnect")
    } catch (error: any) {
      console.error(error.message || "Error en el registro")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <div className="bg-white p-4 rounded-full shadow-lg">
            <div className="h-12 w-12 text-blue-600 flex items-center justify-center text-3xl">🏥</div>
          </div>
        </div>
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">Crear Cuenta en MediConnect</h2>
        <p className="mt-2 text-center text-sm text-gray-600">Únete a nuestra plataforma de telemedicina</p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <RegisterForm onSubmit={handleRegister} isLoading={isLoading} />

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">¿Ya tienes cuenta?</span>
              </div>
            </div>

            <div className="mt-6">
              <Link
                to="/login"
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Iniciar Sesión
              </Link>
            </div>
          </div>
        </div>

        <div className="mt-6 bg-white p-6 rounded-lg shadow">
          <div className="flex items-center mb-4">
            <FaUserPlus className="h-6 w-6 text-green-500 mr-3" />
            <h3 className="text-lg font-semibold text-gray-800">Beneficios de Registrarse</h3>
          </div>
          <ul className="space-y-3 text-sm text-gray-600">
            <li className="flex items-start">
              <span className="h-2 w-2 bg-blue-500 rounded-full mt-2 mr-3"></span>
              <span>Acceso a consultas médicas remotas</span>
            </li>
            <li className="flex items-start">
              <span className="h-2 w-2 bg-blue-500 rounded-full mt-2 mr-3"></span>
              <span>Historial clínico digital</span>
            </li>
            <li className="flex items-start">
              <span className="h-2 w-2 bg-blue-500 rounded-full mt-2 mr-3"></span>
              <span>Recetas electrónicas</span>
            </li>
            <li className="flex items-start">
              <span className="h-2 w-2 bg-blue-500 rounded-full mt-2 mr-3"></span>
              <span>Notificaciones de citas</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default RegisterPage
