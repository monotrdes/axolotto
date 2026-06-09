// Types for play page
export type TabId = 'tienda' | 'jugar' | 'mochila' | 'cartas' | 'tablas' | 'santuario' | 'criadero' | 'axolotitos' | 'rankings' | 'gashapon';

export interface ZoneTab {
  id: TabId;
  label: string;
  emoji: string;
  color: string;
  glow: string;
  zone: string;
}

export type OnboardingPhase =
  | "loading"
  | "intro"
  | "tutorial"
  | "branch"
  | "done";

export interface SyncData {
  is_new_user: boolean;
  tutorial_completed: boolean;
  cave_level: number;
  cave_name: string | null;
}

export interface VipTierConfig {
  emoji: string;
  color: string;
  glow: string;
  label: string;
}
