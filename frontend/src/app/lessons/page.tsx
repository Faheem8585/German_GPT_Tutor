"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import {
  BookOpen,
  ChevronRight,
  ChevronDown,
  CheckCircle,
  Lock,
  Play,
  Zap,
  MessageSquare,
  Volume2,
} from "lucide-react";
import { useUserStore } from "@/stores/userStore";

interface Lesson {
  id: string;
  title: string;
  title_de: string;
  description: string;
  xp: number;
  duration: string;
  type: "grammar" | "vocabulary" | "conversation" | "culture" | "pronunciation";
  completed?: boolean;
  locked?: boolean;
  tutorPrompt: string;
}

interface Unit {
  id: string;
  title: string;
  level: string;
  color: string;
  lessons: Lesson[];
}

const LESSON_UNITS: Unit[] = [
  {
    id: "basics",
    title: "Absolute Basics",
    level: "A1",
    color: "from-green-500 to-emerald-600",
    lessons: [
      {
        id: "greetings",
        title: "Greetings & Introductions",
        title_de: "Begrüßungen",
        description: "Say hello, goodbye, and introduce yourself in German",
        xp: 20,
        duration: "5 min",
        type: "conversation",
        tutorPrompt: "Teach me German greetings and how to introduce myself. Start with 'Hallo' and 'Guten Morgen', then help me practice a short self-introduction.",
      },
      {
        id: "numbers",
        title: "Numbers 1–100",
        title_de: "Zahlen 1–100",
        description: "Count in German and use numbers in everyday situations",
        xp: 20,
        duration: "8 min",
        type: "vocabulary",
        tutorPrompt: "Teach me German numbers from 1 to 100. Start with 1-10, then show me the pattern for teens and tens. Quiz me after each section.",
      },
      {
        id: "articles",
        title: "Der, Die, Das — Articles",
        title_de: "Artikel",
        description: "Master the three German articles and how to use them",
        xp: 30,
        duration: "10 min",
        type: "grammar",
        tutorPrompt: "Explain German articles der, die, das to me. I need to understand when to use each one, with lots of examples. Also explain how they change in accusative case.",
      },
      {
        id: "colors",
        title: "Colors & Adjectives",
        title_de: "Farben & Adjektive",
        description: "Learn colors and basic adjectives in German",
        xp: 20,
        duration: "6 min",
        type: "vocabulary",
        tutorPrompt: "Teach me German colors and basic adjectives. Show me how adjectives change with der/die/das and give me practice sentences.",
      },
    ],
  },
  {
    id: "daily-life",
    title: "Daily Life",
    level: "A2",
    color: "from-blue-500 to-cyan-600",
    lessons: [
      {
        id: "food",
        title: "Food & Restaurants",
        title_de: "Essen & Restaurants",
        description: "Order food, talk about meals, and navigate German restaurants",
        xp: 30,
        duration: "10 min",
        type: "conversation",
        tutorPrompt: "Teach me German food vocabulary and how to order at a restaurant. Practice a restaurant conversation with me where I order food and ask for the bill.",
      },
      {
        id: "transport",
        title: "Public Transport",
        title_de: "Öffentliche Verkehrsmittel",
        description: "Use U-Bahn, S-Bahn, and buses like a local in Germany",
        xp: 30,
        duration: "8 min",
        type: "vocabulary",
        tutorPrompt: "Teach me vocabulary for German public transport — U-Bahn, S-Bahn, Bus, Straßenbahn. How do I buy a ticket, ask for directions, and read signs?",
      },
      {
        id: "shopping",
        title: "Shopping & Prices",
        title_de: "Einkaufen & Preise",
        description: "Shop at German markets, ask for prices, and pay",
        xp: 25,
        duration: "8 min",
        type: "conversation",
        tutorPrompt: "Teach me how to shop in Germany. I need vocabulary for clothes sizes, asking prices, and paying. Practice a shopping dialogue with me.",
      },
      {
        id: "time",
        title: "Telling Time & Dates",
        title_de: "Uhrzeit & Datum",
        description: "Read clocks, say dates, and talk about schedules",
        xp: 25,
        duration: "7 min",
        type: "grammar",
        tutorPrompt: "Teach me how to tell time in German (both formal 24h and casual), and how to say dates and months. Quiz me with time-telling exercises.",
      },
    ],
  },
  {
    id: "workplace",
    title: "Work & Career",
    level: "B1",
    color: "from-purple-500 to-violet-600",
    lessons: [
      {
        id: "job-interview",
        title: "Job Interview German",
        title_de: "Vorstellungsgespräch",
        description: "Ace your German job interview with key phrases and vocabulary",
        xp: 50,
        duration: "15 min",
        type: "conversation",
        tutorPrompt: "Help me prepare for a German job interview. Teach me: how to introduce myself professionally, talk about my experience, answer 'Why do you want this job?', and ask about the role. Then do a mock interview with me.",
      },
      {
        id: "emails",
        title: "Business Emails",
        title_de: "Geschäftliche E-Mails",
        description: "Write professional German emails that impress",
        xp: 40,
        duration: "12 min",
        type: "grammar",
        tutorPrompt: "Teach me how to write formal German business emails. Show me: formal greetings (Sehr geehrte/r), how to state the purpose, polite requests, and formal sign-offs. Then help me write a sample email applying for a job.",
      },
      {
        id: "office",
        title: "Office Communication",
        title_de: "Bürokommunikation",
        description: "Navigate meetings, phone calls, and office small talk",
        xp: 40,
        duration: "12 min",
        type: "conversation",
        tutorPrompt: "Teach me German for the workplace: how to join a meeting, give my opinion, agree/disagree politely, and make small talk with colleagues. Practice some office scenarios with me.",
      },
    ],
  },
  {
    id: "bureaucracy",
    title: "Germany Life",
    level: "B1",
    color: "from-amber-500 to-orange-600",
    lessons: [
      {
        id: "anmeldung",
        title: "Anmeldung & Bürgeramt",
        title_de: "Behördendeutsch",
        description: "Register your address and handle German bureaucracy",
        xp: 50,
        duration: "15 min",
        type: "conversation",
        tutorPrompt: "Teach me German for the Bürgeramt (citizen's office). I need to do my Anmeldung (address registration). Teach me the vocabulary, what documents I need, and practice the conversation at the counter.",
      },
      {
        id: "apartment",
        title: "Finding an Apartment",
        title_de: "Wohnung suchen",
        description: "Read listings, talk to landlords, and sign a Mietvertrag",
        xp: 50,
        duration: "15 min",
        type: "vocabulary",
        tutorPrompt: "Teach me German for apartment hunting. I need: vocabulary from rental listings (Kaltmiete, Nebenkosten, WG, Kaution), how to contact a landlord, questions to ask during a viewing, and key terms in a Mietvertrag.",
      },
      {
        id: "doctor",
        title: "Doctor & Health",
        title_de: "Arzt & Gesundheit",
        description: "Describe symptoms, understand diagnoses, and use German healthcare",
        xp: 40,
        duration: "10 min",
        type: "conversation",
        tutorPrompt: "Teach me German for visiting a doctor. I need to: describe symptoms and pain, understand what a doctor asks, talk about medication, and navigate health insurance (Krankenkasse). Practice a doctor appointment conversation with me.",
      },
    ],
  },
  {
    id: "advanced",
    title: "Advanced German",
    level: "B2",
    color: "from-red-500 to-rose-600",
    lessons: [
      {
        id: "konjunktiv",
        title: "Konjunktiv II",
        title_de: "Konjunktiv II",
        description: "Express wishes, hypotheticals, and polite requests",
        xp: 60,
        duration: "15 min",
        type: "grammar",
        tutorPrompt: "Teach me Konjunktiv II in German. Explain: how it's formed (würde + infinitive, and irregular forms like wäre, hätte, könnte), when to use it for wishes, hypotheticals, and polite requests. Give me lots of examples and practice sentences.",
      },
      {
        id: "passive",
        title: "Passive Voice",
        title_de: "Passiv",
        description: "Understand and use the German passive voice in all tenses",
        xp: 60,
        duration: "15 min",
        type: "grammar",
        tutorPrompt: "Teach me the German passive voice (Passiv). Explain Vorgangspassiv (werden + Partizip II) and Zustandspassiv (sein + Partizip II), in different tenses. Show me when German uses passive where English might not, and give me practice exercises.",
      },
      {
        id: "idioms",
        title: "German Idioms & Slang",
        title_de: "Redewendungen & Umgangssprache",
        description: "Sound like a native with popular German expressions",
        xp: 50,
        duration: "12 min",
        type: "culture",
        tutorPrompt: "Teach me 10 popular German idioms and expressions that locals actually use. For each one: the idiom, its literal meaning, actual meaning, and when to use it. Then teach me some everyday Berlin/Hamburg slang.",
      },
    ],
  },
];

const TYPE_COLORS: Record<string, string> = {
  grammar: "bg-purple-500/20 text-purple-400 border-purple-500/30",
  vocabulary: "bg-blue-500/20 text-blue-400 border-blue-500/30",
  conversation: "bg-green-500/20 text-green-400 border-green-500/30",
  culture: "bg-amber-500/20 text-amber-400 border-amber-500/30",
  pronunciation: "bg-rose-500/20 text-rose-400 border-rose-500/30",
};

const TYPE_ICONS: Record<string, React.ReactNode> = {
  grammar: <BookOpen className="w-3 h-3" />,
  vocabulary: <Zap className="w-3 h-3" />,
  conversation: <MessageSquare className="w-3 h-3" />,
  culture: <span className="text-xs">🇩🇪</span>,
  pronunciation: <Volume2 className="w-3 h-3" />,
};

function LessonCard({ lesson, unitColor }: { lesson: Lesson; unitColor: string }) {
  return (
    <Link
      href={`/tutor?prompt=${encodeURIComponent(lesson.tutorPrompt)}&lesson=${lesson.id}`}
      className={`block ${lesson.locked ? "pointer-events-none opacity-50" : ""}`}
    >
      <motion.div
        whileHover={lesson.locked ? {} : { x: 4 }}
        className="flex items-center gap-4 p-4 rounded-xl border border-border hover:border-brand-500/50 hover:bg-brand-500/5 transition-all group"
      >
        <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${unitColor} flex items-center justify-center flex-shrink-0`}>
          {lesson.locked ? <Lock className="w-4 h-4 text-white/60" /> : lesson.completed ? <CheckCircle className="w-4 h-4 text-white" /> : <Play className="w-4 h-4 text-white" />}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="font-semibold text-sm truncate">{lesson.title}</h3>
            <span className={`flex items-center gap-1 px-1.5 py-0.5 rounded-md text-xs border ${TYPE_COLORS[lesson.type]}`}>
              {TYPE_ICONS[lesson.type]}
              {lesson.type}
            </span>
          </div>
          <p className="text-xs text-muted-foreground truncate">{lesson.description}</p>
          <p className="text-xs text-muted-foreground italic mt-0.5">{lesson.title_de}</p>
        </div>

        <div className="flex flex-col items-end gap-1 flex-shrink-0">
          <span className="flex items-center gap-1 text-xs text-amber-500 font-semibold">
            <Zap className="w-3 h-3" />{lesson.xp} XP
          </span>
          <span className="text-xs text-muted-foreground">{lesson.duration}</span>
        </div>

        <ChevronRight className="w-4 h-4 text-muted-foreground group-hover:text-brand-500 transition-colors flex-shrink-0" />
      </motion.div>
    </Link>
  );
}

function UnitSection({ unit, defaultOpen }: { unit: Unit; defaultOpen?: boolean }) {
  const [open, setOpen] = useState(defaultOpen ?? false);
  const completedCount = unit.lessons.filter((l) => l.completed).length;

  return (
    <div className="glass-card overflow-hidden">
      <button
        onClick={() => setOpen((p) => !p)}
        className="w-full flex items-center gap-4 p-5 text-left hover:bg-white/5 transition-colors"
      >
        <div className={`w-12 h-12 rounded-2xl bg-gradient-to-br ${unit.color} flex items-center justify-center flex-shrink-0`}>
          <BookOpen className="w-6 h-6 text-white" />
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h2 className="font-bold text-lg">{unit.title}</h2>
            <span className="px-2 py-0.5 rounded-lg bg-white/10 text-xs font-mono font-bold">{unit.level}</span>
          </div>
          <p className="text-sm text-muted-foreground">{completedCount}/{unit.lessons.length} lessons complete</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="w-24 h-1.5 bg-secondary rounded-full overflow-hidden">
            <div
              className={`h-full bg-gradient-to-r ${unit.color} rounded-full transition-all`}
              style={{ width: `${unit.lessons.length > 0 ? (completedCount / unit.lessons.length) * 100 : 0}%` }}
            />
          </div>
          <ChevronDown className={`w-5 h-5 text-muted-foreground transition-transform ${open ? "rotate-180" : ""}`} />
        </div>
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-5 pb-5 space-y-2 border-t border-border pt-4">
              {unit.lessons.map((lesson) => (
                <LessonCard key={lesson.id} lesson={lesson} unitColor={unit.color} />
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default function LessonsPage() {
  const { cefrLevel } = useUserStore();

  const levelOrder = ["A1", "A2", "B1", "B2", "C1", "C2"];
  const userLevelIdx = levelOrder.indexOf(cefrLevel);

  const totalLessons = LESSON_UNITS.reduce((acc, u) => acc + u.lessons.length, 0);

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-3xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-3">
              <BookOpen className="w-8 h-8 text-brand-500" />
              Lessons
            </h1>
            <p className="text-muted-foreground mt-1">
              Your level: <span className="font-bold text-brand-400">{cefrLevel}</span> •{" "}
              {totalLessons} structured lessons • AI-powered by Gemma
            </p>
          </div>
          <Link
            href="/tutor"
            className="flex items-center gap-2 px-4 py-2 bg-brand-600 text-white rounded-xl text-sm font-medium hover:bg-brand-500 transition-colors"
          >
            <MessageSquare className="w-4 h-4" />
            Free Chat
          </Link>
        </div>

        {/* Info banner */}
        <div className="flex items-start gap-3 p-4 rounded-xl bg-brand-500/10 border border-brand-500/20 text-sm">
          <span className="text-xl">💡</span>
          <div>
            <p className="font-semibold text-brand-300">How lessons work</p>
            <p className="text-muted-foreground mt-0.5">
              Each lesson opens the AI Tutor with a pre-loaded topic. The tutor teaches you, shows examples, and quizzes you — all in a real conversation. Click any lesson to start.
            </p>
          </div>
        </div>

        {/* Units */}
        {LESSON_UNITS.map((unit, i) => {
          const unitLevelIdx = levelOrder.indexOf(unit.level);
          const isAccessible = unitLevelIdx <= userLevelIdx + 1;
          return (
            <UnitSection
              key={unit.id}
              unit={{
                ...unit,
                lessons: unit.lessons.map((l) => ({ ...l, locked: !isAccessible })),
              }}
              defaultOpen={i === 0 || unit.level === cefrLevel}
            />
          );
        })}
      </div>
    </div>
  );
}
