"use client"

import type React from "react"
import { createContext, useContext, useState, useEffect, type ReactNode } from "react"
import type { User, AuthState } from "../types/user"
import { authService } from "../services/auth"

interface AuthContextType {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (correo: string, password: string) => Promise<void>
  register: (data: any) => Promise<void>
  logout: () => void
  updateUser: (user: User) => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error("useAuth debe usarse dentro de AuthProvider")
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [state, setState] = useState<AuthState>({
    user: authService.getCurrentUser(),
    token: authService.getToken(),
    isAuthenticated: authService.isAuthenticated(),
    isLoading: true,
  })

  useEffect(() => {
    const verifyToken = async () => {
      if (state.token) {
        try {
          const response = await authService.verifyToken()
          if (response.status === "success") {
            localStorage.setItem("user", JSON.stringify(response.data?.user))
            setState((prev: AuthState) => ({
              ...prev,
              user: response.data?.user || null,
              isAuthenticated: true,
              isLoading: false,
            }))
          } else {
            authService.logout()
            setState((prev: AuthState) => ({
              ...prev,
              user: null,
              token: null,
              isAuthenticated: false,
              isLoading: false,
            }))
          }
        } catch (error) {
          authService.logout()
          setState((prev: AuthState) => ({
            ...prev,
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
          }))
        }
      } else {
        setState((prev: AuthState) => ({ ...prev, isLoading: false }))
      }
    }

    verifyToken()
  }, [])

  const login = async (correo: string, password: string) => {
    setState((prev: AuthState) => ({ ...prev, isLoading: true }))

    try {
      const response = await authService.login({ correo, password })

      if (response.status === "success" && response.data) {
        localStorage.setItem("token", response.data.token)
        localStorage.setItem("user", JSON.stringify(response.data.user))

        setState({
          user: response.data.user,
          token: response.data.token,
          isAuthenticated: true,
          isLoading: false,
        })
      } else {
        throw new Error(response.message || "Error en login")
      }
    } catch (error) {
      setState((prev: AuthState) => ({ ...prev, isLoading: false }))
      throw error
    }
  }

  const register = async (data: any) => {
    setState((prev: AuthState) => ({ ...prev, isLoading: true }))

    try {
      const response = await authService.register(data)

      if (response.status === "success") {
        // Auto-login después del registro
        await login(data.correo, data.password)
      } else {
        throw new Error(response.message || "Error en registro")
      }
    } catch (error) {
      setState((prev: AuthState) => ({ ...prev, isLoading: false }))
      throw error
    }
  }

  const logout = () => {
    authService.logout()
    setState({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
    })
  }

  const updateUser = (user: User) => {
    localStorage.setItem("user", JSON.stringify(user))
    setState((prev: AuthState) => ({ ...prev, user }))
  }

  return (
    <AuthContext.Provider
      value={{
        ...state,
        login,
        register,
        logout,
        updateUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}
