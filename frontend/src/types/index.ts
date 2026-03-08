export interface User {
  id: number;
  email: string;
  full_name: string | null;
  avatar_url: string | null;
  is_active: boolean;
  is_admin: boolean;
  is_verified: boolean;
  oauth_provider: string | null;
  last_login_at: string | null;
  created_at: string;
}

export interface Task {
  id: number;
  user_id: number;
  title: string;
  description: string | null;
  source: 'gmail' | 'slack' | 'notion' | 'manual';
  source_id: string | null;
  impact: number;
  urgency: number;
  energy_required: number;
  priority_score: number;
  status: 'active' | 'completed' | 'archived' | 'snoozed';
  is_big_rock: boolean;
  sub_steps: string[] | null;
  snooze_until: string | null;
  completed_at: string | null;
  archived_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface EnergyLog {
  id: number;
  user_id: number;
  level: number;
  session_id: string | null;
  logged_at: string;
}

export interface Integration {
  id: number;
  user_id: number;
  provider: 'gmail' | 'slack' | 'notion';
  is_active: boolean;
  last_synced_at: string | null;
  created_at: string;
}

export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface FreshStartCheck {
  should_trigger: boolean;
  hours_since_last_login: number;
  threshold_hours: number;
}

export interface FreshStartReset {
  tasks_archived: number;
  next_action_task: Task | null;
  message: string;
}

export interface AnalyticsSummary {
  total_completed: number;
  big_rocks_completed: number;
  avg_energy: number;
  tasks_active: number;
  fresh_start_count: number;
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}
