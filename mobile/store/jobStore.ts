import { create } from 'zustand';

export interface JobResult {
  score_url: string;
  audio_url: string;
  image_type: 'sheet_music' | 'general';
  music_params?: Record<string, unknown>;
}

export interface HistoryEntry {
  job_id: string;
  result: JobResult;
  timestamp: number;
}

interface JobState {
  job_id: string | null;
  status: 'idle' | 'queued' | 'running' | 'done' | 'failed';
  current_step: string;
  progress: number;
  result: JobResult | null;
  error: string | null;
  history: HistoryEntry[];
}

interface JobStore extends JobState {
  setJob: (job_id: string) => void;
  updateStatus: (data: Partial<Omit<JobState, 'history'>>) => void;
  addToHistory: (job_id: string, result: JobResult) => void;
  reset: () => void;
}

export const useJobStore = create<JobStore>((set) => ({
  job_id: null,
  status: 'idle',
  current_step: '',
  progress: 0,
  result: null,
  error: null,
  history: [],

  setJob: (job_id) =>
    set({ job_id, status: 'queued', progress: 0, result: null, error: null }),

  updateStatus: (data) => set((state) => ({ ...state, ...data })),

  addToHistory: (job_id, result) =>
    set((state) => ({
      history: [
        { job_id, result, timestamp: Date.now() },
        ...state.history,
      ].slice(0, 20),
    })),

  reset: () =>
    set((state) => ({
      job_id: null,
      status: 'idle',
      current_step: '',
      progress: 0,
      result: null,
      error: null,
      history: state.history,
    })),
}));
