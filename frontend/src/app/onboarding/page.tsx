"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useRouter } from "next/navigation";
import { ChevronRight, ChevronLeft, Check } from "lucide-react";
import { useUserStore } from "@/stores/userStore";
import { tutorApi } from "@/lib/api";

const STEPS = ["Welcome", "Your Level", "Your Goal", "Language", "Ready!"];

const CEFR_OPTIONS = [
  { level: "A1", label: "Complete Beginner", desc: "I know nothing or just started", flag: "🌱" },
  { level: "A2", label: "Elementary", desc: "I know basic greetings and phrases", flag: "🌿" },
  { level: "B1", label: "Intermediate", desc: "I can handle everyday situations", flag: "🌳" },
  { level: "B2", label: "Upper Intermediate", desc: "I can have complex conversations", flag: "🌲" },
  { level: "C1", label: "Advanced", desc: "Near-native fluency", flag: "🏔️" },
  { level: "C2", label: "Mastery", desc: "Native-level proficiency", flag: "🚀" },
];

const GOALS = [
  { id: "work", label: "Get a job in Germany", icon: "💼" },
  { id: "exam", label: "Pass TELC/Goethe exam", icon: "📜" },
  { id: "daily", label: "Daily life in Germany", icon: "🏘️" },
  { id: "travel", label: "Travel and tourism", icon: "✈️" },
  { id: "family", label: "Connect with family/friends", icon: "👨‍👩‍👧" },
  { id: "culture", label: "German culture & media", icon: "🎭" },
];

const LANGUAGES = [
  { value: "en", label: "English", native: "English" },
  { value: "hi", label: "Hindi", native: "हिंदी" },
  { value: "de", label: "German only", native: "Nur Deutsch" },
];

export default function OnboardingPage() {
  const router = useRouter();
  const { setCefrLevel, setUser } = useUserStore();
  const [step, setStep] = useState(0);
  const [selectedLevel, setSelectedLevel] = useState("A1");
  const [selectedGoals, setSelectedGoals] = useState<string[]>([]);
  const [selectedLang, setSelectedLang] = useState("en");
  const [estimating, setEstimating] = useState(false);
  const [sampleText, setSampleText] = useState("");

  const toggleGoal = (id: string) => {
    setSelectedGoals((prev) =>
      prev.includes(id) ? prev.filter((g) => g !== id) : [...prev, id]
    );
  };

  const estimateLevel = async () => {
    if (!sampleText.trim()) return;
    setEstimating(true);
    try {
      const { data } = await tutorApi.estimateLevel(sampleText);
      setSelectedLevel(data.estimated_level);
    } catch {
      // Keep A1 as default
    } finally {
      setEstimating(false);
    }
  };

  const finish = () => {
    setCefrLevel(selectedLevel);
    setUser({ interfaceLanguage: selectedLang as "en" | "de" | "hi" });
    router.push("/dashboard");
  };

  return (
    <div className="min-h-screen bg-[#0d0d1a] text-white flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        {/* Progress */}
        <div className="flex items-center gap-2 mb-12">
          {STEPS.map((s, i) => (
            <div key={s} className="flex items-center gap-2 flex-1">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-all ${
                  i < step
                    ? "bg-green-500 text-white"
                    : i === step
                    ? "bg-brand-600 text-white"
                    : "bg-white/10 text-white/30"
                }`}
              >
                {i < step ? <Check className="w-4 h-4" /> : i + 1}
              </div>
              {i < STEPS.length - 1 && (
                <div
                  className={`flex-1 h-0.5 rounded-full transition-all ${
                    i < step ? "bg-green-500" : "bg-white/10"
                  }`}
                />
              )}
            </div>
          ))}
        </div>

        <AnimatePresence mode="wait">
          {step === 0 && (
            <motion.div
              key="welcome"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              className="text-center space-y-6"
            >
              <div className="text-8xl">🇩🇪</div>
              <h1 className="text-4xl font-bold">Willkommen!</h1>
              <p className="text-white/60 text-lg max-w-md mx-auto">
                Let&apos;s set up your personalized German learning journey. This takes just 2 minutes.
              </p>
              <button
                onClick={() => setStep(1)}
                className="flex items-center gap-2 px-8 py-4 bg-brand-600 rounded-2xl font-semibold mx-auto hover:bg-brand-500 transition-colors"
              >
                Get Started <ChevronRight className="w-5 h-5" />
              </button>
            </motion.div>
          )}

          {step === 1 && (
            <motion.div
              key="level"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              className="space-y-6"
            >
              <h2 className="text-3xl font-bold">What&apos;s your German level?</h2>
              <p className="text-white/50">Select the closest match, or write a sample and let AI detect it.</p>

              <div className="grid grid-cols-2 gap-3">
                {CEFR_OPTIONS.map((opt) => (
                  <button
                    key={opt.level}
                    onClick={() => setSelectedLevel(opt.level)}
                    className={`p-4 rounded-xl border-2 text-left transition-all ${
                      selectedLevel === opt.level
                        ? "border-brand-500 bg-brand-500/10"
                        : "border-white/10 hover:border-white/30"
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <span>{opt.flag}</span>
                      <span className="font-mono font-bold">{opt.level}</span>
                    </div>
                    <p className="font-semibold text-sm">{opt.label}</p>
                    <p className="text-xs text-white/40">{opt.desc}</p>
                  </button>
                ))}
              </div>

              <div className="border border-white/10 rounded-xl p-4">
                <p className="text-sm text-white/60 mb-3">Or let AI detect your level:</p>
                <textarea
                  value={sampleText}
                  onChange={(e) => setSampleText(e.target.value)}
                  placeholder="Write a few sentences in German..."
                  className="w-full bg-white/5 rounded-lg px-3 py-2 text-sm outline-none resize-none h-20 placeholder:text-white/30"
                />
                <button
                  onClick={estimateLevel}
                  disabled={!sampleText.trim() || estimating}
                  className="mt-2 px-4 py-2 bg-white/10 rounded-lg text-sm hover:bg-white/20 transition-colors disabled:opacity-50"
                >
                  {estimating ? "Analyzing..." : "Detect my level"}
                </button>
              </div>
            </motion.div>
          )}

          {step === 2 && (
            <motion.div
              key="goals"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              className="space-y-6"
            >
              <h2 className="text-3xl font-bold">What&apos;s your goal?</h2>
              <p className="text-white/50">Choose all that apply — we&apos;ll customize your learning path.</p>
              <div className="grid grid-cols-2 gap-3">
                {GOALS.map((goal) => (
                  <button
                    key={goal.id}
                    onClick={() => toggleGoal(goal.id)}
                    className={`p-4 rounded-xl border-2 text-left transition-all flex items-center gap-3 ${
                      selectedGoals.includes(goal.id)
                        ? "border-brand-500 bg-brand-500/10"
                        : "border-white/10 hover:border-white/30"
                    }`}
                  >
                    <span className="text-2xl">{goal.icon}</span>
                    <span className="font-medium text-sm">{goal.label}</span>
                    {selectedGoals.includes(goal.id) && (
                      <Check className="w-4 h-4 text-brand-400 ml-auto" />
                    )}
                  </button>
                ))}
              </div>
            </motion.div>
          )}

          {step === 3 && (
            <motion.div
              key="language"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              className="space-y-6"
            >
              <h2 className="text-3xl font-bold">Explanation language</h2>
              <p className="text-white/50">When the AI explains grammar, which language do you prefer?</p>
              <div className="space-y-3">
                {LANGUAGES.map((lang) => (
                  <button
                    key={lang.value}
                    onClick={() => setSelectedLang(lang.value)}
                    className={`w-full p-4 rounded-xl border-2 text-left transition-all flex items-center justify-between ${
                      selectedLang === lang.value
                        ? "border-brand-500 bg-brand-500/10"
                        : "border-white/10 hover:border-white/30"
                    }`}
                  >
                    <span className="font-semibold">{lang.label}</span>
                    <span className="text-white/40">{lang.native}</span>
                  </button>
                ))}
              </div>
            </motion.div>
          )}

          {step === 4 && (
            <motion.div
              key="ready"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="text-center space-y-6"
            >
              <div className="text-6xl">🚀</div>
              <h2 className="text-4xl font-bold">You&apos;re all set!</h2>
              <div className="glass-card p-6 text-left space-y-3">
                <div className="flex justify-between">
                  <span className="text-white/50">Starting Level</span>
                  <span className="font-mono font-bold">{selectedLevel}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/50">Goals</span>
                  <span>{selectedGoals.length} selected</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/50">Language</span>
                  <span>{LANGUAGES.find((l) => l.value === selectedLang)?.label}</span>
                </div>
              </div>
              <button
                onClick={finish}
                className="flex items-center gap-2 px-10 py-4 bg-gradient-to-r from-brand-600 to-purple-600 rounded-2xl font-bold mx-auto hover:scale-105 transition-all"
              >
                Start Learning German! <ChevronRight className="w-5 h-5" />
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Navigation */}
        {step > 0 && step < 4 && (
          <div className="flex items-center justify-between mt-8">
            <button
              onClick={() => setStep((s) => s - 1)}
              className="flex items-center gap-2 px-4 py-2 text-white/50 hover:text-white transition-colors"
            >
              <ChevronLeft className="w-4 h-4" /> Back
            </button>
            <button
              onClick={() => setStep((s) => s + 1)}
              className="flex items-center gap-2 px-6 py-3 bg-brand-600 rounded-xl font-medium hover:bg-brand-500 transition-colors"
            >
              Continue <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
