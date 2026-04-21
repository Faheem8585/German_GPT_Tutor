import { create } from "zustand";
import { persist } from "zustand/middleware";

interface UserState {
  userId: string;
  username: string;
  xp: number;
  streak: number;
  cefrLevel: string;
  interfaceLanguage: "en" | "de" | "hi";
  sessionId: string | null;
  isVoiceMode: boolean;

  setUser: (data: Partial<UserState>) => void;
  addXP: (amount: number) => void;
  incrementStreak: () => void;
  setSessionId: (id: string | null) => void;
  toggleVoiceMode: () => void;
  setCefrLevel: (level: string) => void;
}

export const useUserStore = create<UserState>()(
  persist(
    (set) => ({
      userId: "demo_user",
      username: "Lernender",
      xp: 0,
      streak: 0,
      cefrLevel: "A1",
      interfaceLanguage: "en",
      sessionId: null,
      isVoiceMode: false,

      setUser: (data) => set((state) => ({ ...state, ...data })),
      addXP: (amount) => set((state) => ({ xp: state.xp + amount })),
      incrementStreak: () => set((state) => ({ streak: state.streak + 1 })),
      setSessionId: (id) => set({ sessionId: id }),
      toggleVoiceMode: () => set((state) => ({ isVoiceMode: !state.isVoiceMode })),
      setCefrLevel: (level) => set({ cefrLevel: level }),
    }),
    { name: "germangpt-user" }
  )
);
