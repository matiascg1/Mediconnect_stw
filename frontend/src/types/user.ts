export interface User {
  id: number
  email: string
  first_name: string
  last_name: string
  role: "patient" | "doctor" | "admin"
  date_of_birth?: string
  phone_number?: string
  address?: string
  specialty?: string
  license_number?: string
  created_at?: string
  updated_at?: string
  is_active: boolean
}

export interface UserCreateRequest {
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

export interface UserUpdateRequest {
  first_name?: string
  last_name?: string
  date_of_birth?: string
  phone_number?: string
  address?: string
  specialty?: string
  license_number?: string
}

export interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
}
