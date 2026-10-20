import axios from 'axios';

const BASE = 'http://localhost:8000/api';
const api = axios.create({ baseURL: BASE, timeout: 30000 });

// Types
export interface EligibilityInfo {
  status: 'potentially_eligible' | 'needs_more_info' | 'not_eligible';
  score: number;
  matched_rules: string[];
  failed_rules: string[];
  unknown_rules: string[];
  explanation: string;
}

export interface SchemeCard {
  id: number;
  name: string;
  slug: string;
  level: string;
  state_ministry: string;
  categories_raw: string;
  description: string;
  benefits: string;
  official_link: string;
  myscheme_url: string;
  eligibility: EligibilityInfo;
  ranking_score: number;
  semantic_score: number;
  data_completeness_score: number;
  application_mode: string;
  required_documents?: string[];
  cross_encoder_score?: number;
  why_recommended?: string[];
  rrf_score?: number;
}

export interface SchemeDetail extends SchemeCard {
  eligibility_text: string;
  eligibility_general: string;
  exclusions_text: string;
  application_process: string;
  documents_required: string;
  faqs: string;
  categories_list: string[];
  source_dataset: string;
  ingested_at: string;
  verified: boolean;
}

export interface UserProfile {
  state?: string;
  age?: number;
  gender?: 'male' | 'female' | 'other';
  caste_category?: 'SC' | 'ST' | 'OBC' | 'EWS' | 'General';
  annual_income?: number;
  is_rural?: boolean;
  education?: string;
  occupation?: string;
  goals?: string[];
  documents?: string[];
}

export interface RecommendRequest {
  query: string;
  profile?: UserProfile;
  filters?: { state?: string; level?: string; category?: string };
  top_k?: number;
  page?: number;
}

export interface RecommendResponse {
  total: number;
  page: number;
  page_size: number;
  query: string;
  results: SchemeCard[];
  has_embeddings: boolean;
  model_used: string;
}

export interface Stats {
  total_schemes: number;
  central_schemes: number;
  state_schemes: number;
  total_states_uts: number;
  top_states: Record<string, number>;
  has_embeddings: boolean;
  has_tfidf: boolean;
  device?: string;
  gpu_name?: string;
  architecture?: string;
  bi_encoder_model?: string;
  cross_encoder_model?: string;
  schemes_with_structured_docs?: number;
}

export interface QAAnswer {
  scheme_id: number;
  scheme_name: string;
  snippet: string;
  official_link: string;
  myscheme_url: string;
  relevance_score: number;
}

// API calls
export const getHealth = () => api.get('/health');
export const getStats = () => api.get<Stats>('/stats');
export const getFilters = () => api.get<{ states: string[]; categories: string[]; levels: string[] }>('/filters');
export const listSchemes = (params: Record<string, string | number>) => api.get('/schemes', { params });
export const getSchemeById = (id: number) => api.get<SchemeDetail>(`/schemes/${id}`);
export const getSchemeBySlug = (slug: string) => api.get<SchemeDetail>(`/schemes/slug/${slug}`);
export const recommend = (req: RecommendRequest) => api.post<RecommendResponse>('/recommend', req);
export const askQuestion = (query: string) =>
  api.post<{ query: string; answers: QAAnswer[]; note: string }>('/qa', { query });
export const saveScheme = (sessionId: string, schemeId: number) =>
  api.post(`/saved/${sessionId}/${schemeId}`);
export const removeScheme = (sessionId: string, schemeId: number) =>
  api.delete(`/saved/${sessionId}/${schemeId}`);
export const getSaved = (sessionId: string) => api.get(`/saved/${sessionId}`);
export const compareSchemes = (schemeIds: number[], profile?: UserProfile) =>
  api.post('/compare', { scheme_ids: schemeIds, profile });
export const getEvaluation = () => api.get('/evaluation');
export const getDataQuality = () => api.get('/data-quality');

export interface SimilarSchemeItem {
  id: number;
  name: string;
  slug: string;
  level: string;
  state_ministry: string;
  categories_raw?: string;
  description: string;
  benefits: string;
  similarity_score: number;
  match_pct: number;
  shared_categories: string[];
  official_link: string;
  myscheme_url: string;
  required_documents: string[];
}

export interface BundleSchemeItem {
  id: number;
  name: string;
  slug: string;
  level: string;
  state_ministry: string;
  benefit_role: string;
  rationale: string;
  eligibility: EligibilityInfo;
  official_link: string;
  myscheme_url: string;
  required_documents: string[];
}

export interface ComplementaryBundle {
  bundle_id: string;
  title: string;
  description: string;
  target_persona: string;
  icon: string;
  schemes: BundleSchemeItem[];
}

export interface PersonaItem {
  persona_id: string;
  name: string;
  tagline: string;
  avatar: string;
  description: string;
  profile: UserProfile;
}

export interface PersonalizedFeedResponse {
  top_matches: SchemeCard[];
  bundles: ComplementaryBundle[];
  similar_to_saved: SchemeCard[];
  state_spotlight: SchemeCard[];
  algorithm_info: {
    architecture: string;
    lexical_model: string;
    dense_model: string;
    diversity_algorithm: string;
    device: string;
    hardware: string;
  };
  active_profile_summary?: string;
}

export const getSimilarSchemes = (id: number, topK = 4) =>
  api.get<{ scheme_id: number; scheme_name: string; count: number; results: SimilarSchemeItem[] }>(`/schemes/${id}/similar`, { params: { top_k: topK } });

export const getPersonalizedFeed = (payload: { profile?: UserProfile; saved_ids?: number[]; top_k?: number }) =>
  api.post<PersonalizedFeedResponse>('/recommend/feed', payload);

export const getPersonas = () =>
  api.get<{ personas: PersonaItem[] }>('/recommend/personas');

export const getBundles = (params?: { state?: string; gender?: string; age?: number }) =>
  api.get<{ bundles: ComplementaryBundle[] }>('/recommend/bundles', { params });

