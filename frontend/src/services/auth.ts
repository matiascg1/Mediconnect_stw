import api from "./api"
import type { User } from "../types/user"

export interface LoginRequest {
  correo: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  first_name: string
  last_name: string
  role: string
  date_of_birth?: string
  phone_number?: string
  address?: string
  specialty?: string
  license_number?: string
}

export interface AuthResponse {
  status: string
  message?: string
  data?: {
    token: string
    user: User
  }
}

export const authService = {
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await api.post("/auth/login", credentials)
    return response.data
  },

  async register(userData: RegisterRequest): Promise<AuthResponse> {
    const response = await api.post("/auth/register", userData)
    return response.data
  },

  async logout(): Promise<void> {
    localStorage.removeItem("token")
    localStorage.removeItem("user")
  },

  async verifyToken(): Promise<AuthResponse> {
    const response = await api.get("/auth/verify")
    return response.data
  },

  getCurrentUser(): User | null {
    const userStr = localStorage.getItem("user")
    return userStr ? JSON.parse(userStr) : null
  },

  isAuthenticated(): boolean {
    const token = localStorage.getItem("token")
    return !!token
  },

  getToken(): string | null {
    return localStorage.getItem("token")
  },

  getUser(): User | null {
    const userStr = localStorage.getItem("user")
    return userStr ? JSON.parse(userStr) : null
  },

  setAuthData(data: AuthResponse): void {
    if (data.data) {
      localStorage.setItem("token", data.data.token)
      localStorage.setItem("user", JSON.stringify(data.data.user))
    }
  },
}
