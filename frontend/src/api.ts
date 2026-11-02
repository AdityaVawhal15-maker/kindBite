/**
 * KindBite — Frontend API Client
 * Connects to FastAPI backend (/api/v1) with JWT bearer token support.
 */

const API_BASE = '/api/v1';

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'RESTAURANT' | 'NGO' | 'VOLUNTEER' | 'ADMIN';
  phone?: string;
  is_active: boolean;
  verification_status: 'UNVERIFIED' | 'PENDING' | 'VERIFIED' | 'REJECTED';
}

export interface Donation {
  id: string;
  restaurant_id: string;
  ngo_id?: string;
  food_name: string;
  food_category: string;
  quantity_kg: number;
  servings?: number;
  dietary_label?: string;
  allergens?: string[];
  storage_condition?: string;
  storage_temp_celsius?: number;
  preparation_datetime: string;
  collection_deadline: string;
  pickup_address: string;
  pickup_city?: string;
  pickup_pincode?: string;
  pickup_latitude?: number;
  pickup_longitude?: number;
  safety_confirmed: boolean;
  handler_declaration: boolean;
  is_eligible?: boolean;
  status: 'DRAFT' | 'PUBLISHED' | 'MATCHED' | 'ACCEPTED' | 'ASSIGNED' | 'COLLECTED' | 'DELIVERED' | 'CANCELLED';
  created_at: string;
  delivery?: {
    id: string;
    volunteer_id: string;
    status: string;
    estimated_distance_km?: number;
    estimated_duration_minutes?: number;
  };
  safety_check?: {
    preparation_time_ok?: boolean;
    storage_condition_ok?: boolean;
    allergens_declared?: boolean;
    packaging_ok?: boolean;
    within_deadline?: boolean;
    overall_eligible?: boolean;
    notes?: string;
  };
}

export interface MatchRecommendation {
  ngo_id: string;
  ngo_name: string;
  address: string;
  match_score: number;
  score_breakdown: Record<string, number>;
  distance_km?: number;
  capacity_available_kg?: number;
}

export interface SurplusPredictionResult {
  predicted_demand_kg: number;
  predicted_surplus_kg: number;
  waste_risk: 'LOW' | 'MEDIUM' | 'HIGH';
  risk_score: number;
  model_name?: string;
  model_version?: string;
}

export interface NotificationItem {
  id: string;
  title: string;
  body: string;
  type?: string;
  is_read: boolean;
  created_at?: string;
}

export interface AdminAnalytics {
  users: {
    total: number;
    restaurants: number;
    ngos: number;
    volunteers: number;
  };
  donations: {
    total: number;
    delivered: number;
    total_kg_rescued: number;
  };
}

// Token storage helpers
export function getToken(): string | null {
  return localStorage.getItem('kindbite_token');
}

export function setToken(token: string): void {
  localStorage.setItem('kindbite_token', token);
}

export function clearToken(): void {
  localStorage.removeItem('kindbite_token');
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetail = `Request failed (${response.status})`;
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || errorDetail;
    } catch {
      // ignore
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

export const api = {
  // Auth
  async login(email: string, password = 'KindBite@2026'): Promise<{ access_token: string; role: string }> {
    const res = await request<{ access_token: string; token_type: string }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    setToken(res.access_token);
    return { access_token: res.access_token, role: '' };
  },

  async getMe(): Promise<User> {
    return request<User>('/auth/me');
  },

  // Donations
  async listDonations(status?: string): Promise<Donation[]> {
    const q = status ? `?status=${status}` : '';
    return request<Donation[]>(`/donations${q}`);
  },

  async createDonation(data: Partial<Donation>): Promise<Donation> {
    return request<Donation>('/donations', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async getDonation(id: string): Promise<Donation> {
    return request<Donation>(`/donations/${id}`);
  },

  // Matching
  async getMatches(donationId: string): Promise<MatchRecommendation[]> {
    return request<MatchRecommendation[]>(`/matching/${donationId}/recommendations`);
  },

  async acceptDonation(donationId: string): Promise<any> {
    return request(`/matching/${donationId}/accept`, {
      method: 'POST',
    });
  },

  // ML Predictions
  async predictSurplus(data: {
    food_item_id?: string;
    prediction_date: string;
    prepared_quantity_kg: number;
  }): Promise<SurplusPredictionResult> {
    return request<SurplusPredictionResult>('/predictions/surplus', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async getEvaluationMetrics(): Promise<any> {
    return request('/ml/metrics');
  },

  // Deliveries
  async listDeliveries(): Promise<any[]> {
    return request<any[]>('/deliveries');
  },

  async updateDeliveryStatus(deliveryId: string, status: string, notes?: string): Promise<any> {
    return request(`/deliveries/${deliveryId}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status, notes }),
    });
  },

  // Admin
  async getAnalytics(): Promise<AdminAnalytics> {
    return request<AdminAnalytics>('/admin/analytics');
  },

  async listVerifications(): Promise<any[]> {
    return request<any[]>('/admin/verifications');
  },

  async updateVerification(entityType: string, entityId: string, status: string, notes?: string): Promise<any> {
    return request(`/admin/verifications/${entityType}/${entityId}`, {
      method: 'POST',
      body: JSON.stringify({ status, notes }),
    });
  },

  async listAuditLogs(): Promise<any[]> {
    return request<any[]>('/admin/audit-logs');
  },

  // Notifications
  async listNotifications(): Promise<NotificationItem[]> {
    return request<NotificationItem[]>('/notifications');
  },

  async getUnreadCount(): Promise<{ unread_count: number }> {
    return request<{ unread_count: number }>('/notifications/unread-count');
  },

  async markAllNotificationsRead(): Promise<any> {
    return request('/notifications/mark-all-read', {
      method: 'POST',
    });
  },

  // System Health
  async checkHealth(): Promise<{ status: string; service: string }> {
    const res = await fetch('/health');
    return res.json();
  },
};
