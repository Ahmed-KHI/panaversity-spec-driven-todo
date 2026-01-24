/**
 * API client for backend communication.
 * [Task]: T-020 (API Client)
 * [From]: spec.md §9, plan.md §8
 */

import { API_URL } from './config'

export interface User {
  id: string
  email: string
}

export interface Task {
  id: number
  user_id: string
  title: string
  description: string | null
  completed: boolean
  created_at: string
  updated_at: string
}

export interface RegisterRequest {
  email: string
  password: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

export interface RegisterResponse {
  id: string
  email: string
  message: string
}

export interface TaskCreateRequest {
  title: string
  description?: string
  priority?: string
  due_date?: string | null
  is_recurring?: boolean
  recurrence_pattern?: {
    frequency: string
    interval: number
  }
}

export interface TaskUpdateRequest {
  title?: string
  description?: string
  priority?: string
  due_date?: string | null
  is_recurring?: boolean
  recurrence_pattern?: {
    frequency: string
    interval: number
  }
}

export interface TaskPatchRequest {
  completed: boolean
}

export class ApiClient {
  private token: string | null = null

  setToken(token: string | null) {
    this.token = token
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    }

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`
    }

    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
      throw new Error(error.detail || `HTTP ${response.status}`)
    }

    if (response.status === 204) {
      return {} as T
    }

    return response.json()
  }

  // Auth endpoints
  async register(data: RegisterRequest): Promise<RegisterResponse> {
    return this.request<RegisterResponse>('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async login(data: LoginRequest): Promise<AuthResponse> {
    return this.request<AuthResponse>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  // Task endpoints
  async getTasks(userId: string, completed: 'all' | 'pending' | 'completed' = 'all'): Promise<{ tasks: Task[], count: number }> {
    return this.request<{ tasks: Task[], count: number }>(
      `/api/${userId}/tasks?completed=${completed}`
    )
  }

  async getTask(userId: string, taskId: number): Promise<Task> {
    return this.request<Task>(`/api/${userId}/tasks/${taskId}`)
  }

  async createTask(userId: string, data: TaskCreateRequest): Promise<Task> {
    return this.request<Task>(`/api/${userId}/tasks`, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async updateTask(userId: string, taskId: number, data: TaskUpdateRequest): Promise<Task> {
    return this.request<Task>(`/api/${userId}/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  async toggleTask(userId: string, taskId: number, completed: boolean): Promise<Task> {
    return this.request<Task>(`/api/${userId}/tasks/${taskId}`, {
      method: 'PATCH',
      body: JSON.stringify({ completed }),
    })
  }

  async deleteTask(userId: string, taskId: number): Promise<void> {
    return this.request<void>(`/api/${userId}/tasks/${taskId}`, {
      method: 'DELETE',
    })
  }
}

export const apiClient = new ApiClient()
