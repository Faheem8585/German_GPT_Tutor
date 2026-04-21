import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const api = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  timeout: 90000,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error.response?.status === 401) {
      if (typeof window !== "undefined") localStorage.removeItem("token");
    }
    return Promise.reject(error);
  }
);

// tutor
export const tutorApi = {
  chat: (data: {
    message: string;
    session_id?: string;
    cefr_level?: string;
    interface_language?: string;
  }) => api.post("/tutor/chat", data),

  grammarCheck: (text: string, cefr_level = "B1") =>
    api.post("/tutor/grammar/check", null, { params: { text, cefr_level } }),

  pronunciationGuide: (word: string) =>
    api.post("/tutor/pronunciation/guide", null, { params: { word } }),

  listScenarios: () => api.get("/tutor/scenarios"),

  startConversation: (data: { scenario: string; cefr_level: string }) =>
    api.post("/tutor/conversation/start", data),

  estimateLevel: (sample: string) =>
    api.get("/tutor/level/estimate", { params: { sample } }),
};

// voice
export const voiceApi = {
  transcribe: (audioBlob: Blob, language = "de") => {
    const form = new FormData();
    form.append("audio", audioBlob, "audio.webm");
    form.append("language", language);
    return api.post("/voice/transcribe", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },

  synthesize: (text: string, voice = "nova", speed = 0.9) =>
    api.post(
      "/voice/synthesize",
      { text, voice, speed },
      { responseType: "blob" }
    ),

  scorePronunciation: (data: {
    reference_text: string;
    spoken_text: string;
    native_language?: string;
    cefr_level?: string;
  }) => api.post("/voice/pronunciation/score", data),

  voiceTutor: (audioBlob: Blob, cefr_level = "A1", session_id = "") => {
    const form = new FormData();
    form.append("audio", audioBlob, "audio.webm");
    form.append("cefr_level", cefr_level);
    form.append("session_id", session_id);
    return api.post("/voice/voice-tutor", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

// games
export const gamesApi = {
  createGame: (data: { game_type: string; cefr_level: string; topic?: string }) =>
    api.post("/games/create", data),

  submitResult: (data: {
    game_id: string;
    answers: Record<string, unknown>[];
    questions: Record<string, unknown>[];
    game_type: string;
    time_taken_seconds: number;
    cefr_level: string;
  }) => api.post("/games/submit", data),

  getDailyMissions: (cefr_level = "A1") =>
    api.get("/games/daily-missions", { params: { cefr_level } }),

  getLeaderboard: () => api.get("/games/leaderboard"),

  getGameTypes: () => api.get("/games/types"),
};

// analytics
export const analyticsApi = {
  getDashboard: () => api.get("/analytics/dashboard"),
  getTimeline: () => api.get("/analytics/progress/timeline"),
  getMistakes: () => api.get("/analytics/mistakes/breakdown"),
  getAIMetrics: () => api.get("/analytics/ai-metrics"),
  getPlatformStats: () => api.get("/analytics/leaderboard/stats"),
};
