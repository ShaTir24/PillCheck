// Mirrors backend/app/schemas/*.py Read models. Keep in sync by hand for now —
// see .claude/skills/add-feature/SKILL.md for the checklist when a field changes.

export type UUID = string;

export interface Profile {
  id: UUID;
  display_name: string;
  accessibility_high_contrast: boolean;
  accessibility_voice_output: boolean;
  created_at: string;
  updated_at: string;
}

export interface Medication {
  id: UUID;
  profile_id: UUID;
  drug_name: string;
  strength: string | null;
  form: string | null;
  ndc: string | null;
  appearance_front_id: UUID | null;
  appearance_back_id: UUID | null;
  created_at: string;
  updated_at: string;
}

export interface Schedule {
  id: UUID;
  medication_id: UUID;
  window_label: string;
  time_of_day: string; // "HH:MM:SS"
  days_of_week: number[]; // 0=Mon .. 6=Sun, matches Python's date.weekday()
  dose_count: number;
  active: boolean;
  created_at: string;
  updated_at: string;
}

export type ReferenceAppearanceSide = "front" | "back";
export type ReferenceAppearanceOrigin = "library" | "user_enrolled";

export interface ReferenceAppearance {
  id: UUID;
  ndc: string | null;
  side: ReferenceAppearanceSide;
  imprint: string | null;
  shape: string | null;
  color: string | null;
  size_mm: number | null;
  scored: boolean;
  image_uri: string;
  origin: ReferenceAppearanceOrigin;
  owner_profile_id: UUID | null;
  created_at: string;
  updated_at: string;
}

export type DoseEventResult = "match" | "mismatch" | "cannot_identify" | "manual_taken";

export interface PerPillCandidate {
  ref_id: UUID;
  embed_sim: number;
  imprint_conf: number | null;
  fused_score: number;
}

export interface PerPillResult {
  bbox: [number, number, number, number];
  top_k: PerPillCandidate[];
  decision: string;
}

export interface DoseEvent {
  id: UUID;
  profile_id: UUID;
  ts: string;
  scheduled_window_id: UUID | null;
  result: DoseEventResult;
  per_pill: PerPillResult[];
  quality: Record<string, unknown>;
  image_uri: string | null;
  created_at: string;
}

export type CaregiverLinkStatus = "pending" | "active" | "revoked";

export interface CaregiverLink {
  id: UUID;
  subject_profile_id: UUID;
  caregiver_profile_id: UUID | null;
  invite_token: string;
  scopes: string[];
  status: CaregiverLinkStatus;
  revoked_at: string | null;
  created_at: string;
}
