export interface User {
  id: string;
  email: string;
  subscription_tier: 'free' | 'pro' | 'business' | 'enterprise';
  created_at: string;
  mfa_enabled: boolean;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData extends LoginCredentials {
  confirm_password: string;
}

export interface ApiResponse {
  data: T;
  message?: string;
}
