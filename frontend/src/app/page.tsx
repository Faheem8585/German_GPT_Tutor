"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import {
  Mic,
  MessageSquare,
  Trophy,
  Brain,
  Zap,
  Globe2,
  BookOpen,
  ChevronRight,
  Star,
  TrendingUp,
  Shield,
} from "lucide-react";

const CEFR_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"];

const FEATURES = [
  {
    icon: <Brain className="w-6 h-6" />,
    title: "Multi-Agent AI Tutor",
    description:
      "LangGraph-powered orchestration with specialized agents for grammar, pronunciation, motivation & curriculum planning",
    color: "from-purple-500 to-indigo-600",
  },
  {
    icon: <Mic className="w-6 h-6" />,
    title: "Voice AI (STT + TTS)",
    description:
      "Real-time Whisper transcription + high-quality TTS. Speak German and get instant AI feedback on pronunciation",
    color: "from-pink-500 to-rose-600",
  },
  {
    icon: <BookOpen className="w-6 h-6" />,
    title: "Hybrid RAG Knowledge Base",
    description:
      "BM25 + vector search with LLM reranking. German grammar, vocabulary, exam prep & cultural knowledge",
    color: "from-amber-500 to-orange-600",
  },
  {
    icon: <Trophy className="w-6 h-6" />,
    title: "Duolingo-Level Gamification",
    description:
      "XP, streaks, leaderboards, achievements, daily missions, survival mode — learning that's genuinely addictive",
    color: "from-green-500 to-emerald-600",
  },
  {
    icon: <TrendingUp className="w-6 h-6" />,
    title: "Adaptive Learning Engine",
    description:
      "Auto-detects your CEFR level, tracks mistakes with spaced repetition, personalizes every lesson",
    color: "from-cyan-500 to-blue-600",
  },
  {
    icon: <Globe2 className="w-6 h-6" />,
    title: "Germany-Specific Modules",
    description:
      "Job interview simulator, Bürgeramt vocabulary, Wohnung suchen, business email writing — real Germany skills",
    color: "from-red-500 to-rose-700",
  },
  {
    icon: <Shield className="w-6 h-6" />,
    title: "Production-Grade Engineering",
    description:
      "Prompt injection defense, PII masking, GDPR-aware, rate limiting, observability, eval framework",
    color: "from-slate-500 to-gray-700",
  },
  {
    icon: <Zap className="w-6 h-6" />,
    title: "LLM Evaluation Pipeline",
    description:
      "Automated hallucination detection, accuracy scoring, pedagogical quality assessment, A/B testing",
    color: "from-yellow-500 to-amber-600",
  },
];

const STATS = [
  { value: "6", label: "CEFR Levels" },
  { value: "8+", label: "Game Types" },
  { value: "12+", label: "AI Agents" },
  { value: "A1→C2", label: "Full Journey" },
];

const SCENARIOS = [
  "🏢 Job Interview",
  "🏠 Apartment Rental",
  "🏥 Doctor Visit",
  "🚂 Train Travel",
  "🛒 Grocery Shopping",
  "📋 Bureaucracy German",
  "📧 Business Email",
  "💼 Office Communication",
];

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-[#0d0d1a] text-white overflow-hidden">
      <nav className="fixed top-0 left-0 right-0 z-50 backdrop-blur-xl border-b border-white/5 bg-black/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center text-black font-bold text-sm">
              DE
            </div>
            <span className="font-bold text-lg tracking-tight">GermanGPT Tutor</span>
          </div>
          <div className="hidden md:flex items-center gap-8 text-sm text-white/60">
            <Link href="/dashboard" className="hover:text-white transition-colors">Dashboard</Link>
            <Link href="/tutor" className="hover:text-white transition-colors">AI Tutor</Link>
            <Link href="/games" className="hover:text-white transition-colors">Games</Link>
            <Link href="/lessons" className="hover:text-white transition-colors">Lessons</Link>
          </div>
          <div className="flex items-center gap-3">
            <Link
              href="/dashboard"
              className="px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-sm font-medium transition-colors"
            >
              Start Learning Free
            </Link>
          </div>
        </div>
      </nav>
      <section className="relative pt-32 pb-24 px-4">
        {/* Background effects */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-20 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-brand-600/10 rounded-full blur-3xl" />
          <div className="absolute top-40 right-0 w-[400px] h-[400px] bg-amber-500/5 rounded-full blur-3xl" />
          <div className="absolute bottom-0 left-0 w-[300px] h-[300px] bg-purple-800/10 rounded-full blur-3xl" />
        </div>

        <div className="max-w-5xl mx-auto text-center relative">
          {/* German flag accent */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/5 border border-white/10 text-sm mb-8"
          >
            <span>🇩🇪</span>
            <span className="text-white/60">AI-powered • Multi-agent • Production-grade</span>
            <span className="px-2 py-0.5 bg-brand-600/30 text-brand-300 rounded-full text-xs">
              2026 Stack
            </span>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-5xl md:text-7xl font-bold tracking-tight mb-6"
          >
            Master German with{" "}
            <span className="bg-gradient-to-r from-brand-400 via-purple-400 to-amber-400 bg-clip-text text-transparent">
              AI
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-xl text-white/60 max-w-2xl mx-auto mb-10"
          >
            From A1 to C2 — multi-agent tutoring, voice practice, gamified games, and personalized
            learning. Built for Germany job seekers, exam prep, and daily life.
          </motion.p>

          {/* CEFR Level selector */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="flex items-center justify-center gap-2 mb-10 flex-wrap"
          >
            {CEFR_LEVELS.map((level) => (
              <span
                key={level}
                className="px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-sm font-mono text-white/70 hover:bg-brand-600/20 hover:border-brand-500/50 hover:text-white transition-all cursor-pointer"
              >
                {level}
              </span>
            ))}
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <Link
              href="/tutor"
              className="flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-brand-600 to-purple-600 rounded-2xl font-semibold text-white hover:shadow-glow-brand transition-all hover:scale-105"
            >
              <MessageSquare className="w-5 h-5" />
              Chat with AI Tutor
              <ChevronRight className="w-4 h-4" />
            </Link>
            <Link
              href="/games"
              className="flex items-center gap-2 px-8 py-4 bg-white/5 border border-white/10 rounded-2xl font-semibold text-white hover:bg-white/10 transition-all"
            >
              <Trophy className="w-5 h-5 text-amber-400" />
              Explore Games
            </Link>
          </motion.div>

          {/* Stats row */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
            className="grid grid-cols-4 gap-4 mt-20 max-w-lg mx-auto"
          >
            {STATS.map((stat) => (
              <div key={stat.label} className="text-center">
                <div className="text-2xl font-bold text-white">{stat.value}</div>
                <div className="text-xs text-white/40 mt-1">{stat.label}</div>
              </div>
            ))}
          </motion.div>
        </div>
      </section>
      <section className="py-24 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">
              Production-Grade LLM Engineering
            </h2>
            <p className="text-white/50 text-lg max-w-2xl mx-auto">
              Every component demonstrates the skills German AI/ML companies look for in 2026
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {FEATURES.map((feature, i) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.05 }}
                whileHover={{ y: -4 }}
                className="glass-card p-6 group cursor-default"
              >
                <div
                  className={`w-12 h-12 rounded-xl bg-gradient-to-br ${feature.color} flex items-center justify-center text-white mb-4 group-hover:scale-110 transition-transform`}
                >
                  {feature.icon}
                </div>
                <h3 className="font-semibold mb-2 text-white/90">{feature.title}</h3>
                <p className="text-sm text-white/50 leading-relaxed">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>
      <section className="py-20 px-4 bg-white/2">
        <div className="max-w-5xl mx-auto text-center">
          <h2 className="text-4xl font-bold mb-4">Real Germany. Real Conversations.</h2>
          <p className="text-white/50 mb-12">
            Practice the exact situations you&apos;ll face living and working in Germany
          </p>
          <div className="flex flex-wrap gap-3 justify-center">
            {SCENARIOS.map((scenario) => (
              <motion.span
                key={scenario}
                whileHover={{ scale: 1.05 }}
                className="px-5 py-2.5 bg-white/5 border border-white/10 rounded-full text-sm font-medium text-white/70 hover:text-white hover:border-brand-500/50 transition-all cursor-pointer"
              >
                {scenario}
              </motion.span>
            ))}
          </div>
        </div>
      </section>
      <section className="py-24 px-4">
        <div className="max-w-3xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="glass-card p-12"
          >
            <div className="text-5xl mb-6">🇩🇪</div>
            <h2 className="text-4xl font-bold mb-4">Fangen wir an!</h2>
            <p className="text-white/50 mb-8">
              Join thousands learning German the smart way — with AI, games, and real conversation practice
            </p>
            <Link
              href="/onboarding"
              className="inline-flex items-center gap-2 px-10 py-4 bg-gradient-to-r from-amber-500 to-amber-600 text-black rounded-2xl font-bold hover:scale-105 transition-all hover:shadow-glow-gold"
            >
              <Star className="w-5 h-5" />
              Start Your German Journey
              <ChevronRight className="w-5 h-5" />
            </Link>
            <p className="text-white/30 text-sm mt-4">Free to start • No credit card required</p>
          </motion.div>
        </div>
      </section>
      <footer className="border-t border-white/5 py-8 px-4">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="text-sm text-white/30">
            © 2026 GermanGPT Tutor — Built with LangGraph, FastAPI, Next.js
          </div>
          <div className="flex items-center gap-6 text-sm text-white/30">
            <span>Multi-Agent AI</span>
            <span>•</span>
            <span>Hybrid RAG</span>
            <span>•</span>
            <span>Voice AI</span>
            <span>•</span>
            <span>GDPR Compliant</span>
          </div>
        </div>
      </footer>
    </main>
  );
}
