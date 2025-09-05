export interface Journal {
  id: number;
  name: string;
  slug: string;
  description?: string;
  base_url: string;
  proxy_path: string;
  requires_auth: boolean;
  auth_method: string;
  custom_headers?: Record<string, string>;
  timeout: number;
  is_active: boolean;
  access_level: 'public' | 'restricted' | 'admin';
  publisher?: string;
  issn?: string;
  e_issn?: string;
  subject_areas?: string[];
  created_at: string;
  updated_at: string;
}

export interface JournalListResponse {
  journals: Journal[];
  pagination: {
    page: number;
    pages: number;
    per_page: number;
    total: number;
    has_next: boolean;
    has_prev: boolean;
  };
}

export interface JournalAccessResponse {
  message: string;
  journal: Journal;
  access_url: string;
  proxy_config: ProxyConfig;
}

export interface ProxyConfig {
  id: number;
  journal_id: number;
  user_id?: number;
  config_name: string;
  ip_address?: string;
  user_agent?: string;
  referer?: string;
  is_active: boolean;
  expires_at?: string;
  last_used?: string;
  usage_count: number;
  created_at: string;
  updated_at: string;
}

export interface JournalSearchFilters {
  search?: string;
  publisher?: string;
  issn?: string;
  subject_areas?: string[];
  access_level?: string;
}
