"use client";

import { useState, useRef, useEffect, useCallback, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  Send,
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Settings,
  ChevronDown,
  AlertCircle,
  CheckCircle,
  Plus,
  Loader2,
  Brain,
} from "lucide-react";
import { tutorApi } from "@/lib/api";
import { useUserStore } from "@/stores/userStore";
import toast from "react-hot-toast";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  grammarErrors?: GrammarError[];
  xpEarned?: number;
  timestamp: Date;
}

interface GrammarError {
  incorrect: string;
  correct: string;
  rule: string;
  explanation: string;
  severity: "minor" | "major";
}

const CEFR_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"];
const INTERFACE_LANGS = [
  { value: "en", label: "English" },
  { value: "de", label: "Deutsch" },
  { value: "hi", label: "हिंदी" },
];

function GrammarFeedback({ errors }: { errors: GrammarError[] }) {
  if (!errors.length) return null;
  return (
    <div className="mt-3 space-y-2">
      {errors.map((err, i) => (
        <div key={i} className="text-xs rounded-lg overflow-hidden border border-border">
          <div className="grammar-correction">
            ❌ <span className="line-through text-red-500">{err.incorrect}</span>
          </div>
          <div className="grammar-correct">
            ✅ <span className="text-green-600 dark:text-green-400">{err.correct}</span>
          </div>
          <div className="px-3 py-1.5 bg-muted text-muted-foreground">
            <strong>{err.rule}:</strong> {err.explanation}
          </div>
        </div>
      ))}
    </div>
  );
}

function XPToast({ amount }: { amount: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0, y: 20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      className="xp-badge text-sm"
    >
      +{amount} XP ⚡
    </motion.div>
  );
}

function VoiceWave() {
  return (
    <div className="voice-wave flex items-center justify-center h-8">
      {[1, 2, 3, 4, 5].map((i) => (
        <span key={i} style={{ animationDelay: `${(i - 1) * 0.1}s` }} />
      ))}
    </div>
  );
}

function TutorPageInner() {
  const { cefrLevel, interfaceLanguage, addXP, setSessionId, sessionId } = useUserStore();
  const searchParams = useSearchParams();
  const lessonPrompt = searchParams.get("prompt");
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content: `Hallo! Ich bin dein KI-Deutschlehrer! 🇩🇪\n\nI'm your AI German tutor, ready to help you learn German at level **${cefrLevel}**.\n\nYou can:\n- 💬 Chat with me in German or English\n- 🎤 Use voice mode to practice speaking\n- 📝 Get instant grammar corrections\n- 🎯 Practice real-life scenarios\n\n**Wie kann ich dir helfen?** (How can I help you?)`,
      timestamp: new Date(),
    } as Message,
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isTTSEnabled, setIsTTSEnabled] = useState(true);
  const [selectedLevel, setSelectedLevel] = useState(cefrLevel);
  const [selectedLang, setSelectedLang] = useState(interfaceLanguage);
  const [showSettings, setShowSettings] = useState(false);

  const [liveTranscript, setLiveTranscript] = useState("");

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const speechRecRef = useRef<SpeechRecognition | null>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const sentLessonRef = useRef<string | null>(null);
  const transcriptRef = useRef<string>("");
  const resultSentRef = useRef<boolean>(false);

  const WELCOME_MSG = {
    id: "welcome",
    role: "assistant" as const,
    content: `Hallo! Ich bin dein KI-Deutschlehrer! 🇩🇪\n\nI'm your AI German tutor, ready to help you learn German at level **${cefrLevel}**.\n\nYou can:\n- 💬 Chat with me in German or English\n- 🎤 Use voice mode to practice speaking\n- 📝 Get instant grammar corrections\n- 🎯 Practice real-life scenarios\n\n**Wie kann ich dir helfen?** (How can I help you?)`,
    timestamp: new Date(),
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Auto-start lesson from /lessons page — re-fires whenever lessonPrompt changes
  useEffect(() => {
    if (!lessonPrompt || sentLessonRef.current === lessonPrompt) return;
    sentLessonRef.current = lessonPrompt;
    // Reset conversation for the new lesson
    setMessages([WELCOME_MSG]);
    const decoded = decodeURIComponent(lessonPrompt);
    const timer = setTimeout(() => sendMessage(decoded), 800);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lessonPrompt]);

  useEffect(scrollToBottom, [messages]);

  const sendMessage = useCallback(
    async (text: string) => {
      if (!text.trim() || loading) return;

      const userMsg: Message = {
        id: Date.now().toString(),
        role: "user",
        content: text.trim(),
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMsg]);
      setInput("");
      setLoading(true);

      try {
        const { data } = await tutorApi.chat({
          message: text.trim(),
          session_id: sessionId || undefined,
          cefr_level: selectedLevel,
          interface_language: selectedLang,
        });

        if (!sessionId) setSessionId(data.session_id);

        const assistantMsg: Message = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: data.response,
          grammarErrors: data.grammar_errors,
          xpEarned: data.xp_earned,
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, assistantMsg]);

        if (data.xp_earned > 0) {
          addXP(data.xp_earned);
          toast.custom(() => <XPToast amount={data.xp_earned} />);
        }

        // Auto-play TTS if enabled — use browser speechSynthesis (no API key needed)
        if (isTTSEnabled && data.response) {
          try {
            window.speechSynthesis.cancel();
            const utter = new SpeechSynthesisUtterance(data.response.slice(0, 400));
            utter.lang = "de-DE";
            utter.rate = 0.85;
            utter.pitch = 1;
            window.speechSynthesis.speak(utter);
          } catch {
            // TTS optional — don't block on failure
          }
        }
      } catch (error) {
        toast.error("Could not connect to AI tutor. Please try again.");
        setMessages((prev) => prev.filter((m) => m.id !== userMsg.id));
        setInput(text);
      } finally {
        setLoading(false);
        inputRef.current?.focus();
      }
    },
    [loading, sessionId, selectedLevel, selectedLang, isTTSEnabled, addXP, setSessionId]
  );

  const startRecording = () => {
    const SpeechRecognitionAPI =
      (window as typeof window & { SpeechRecognition?: typeof SpeechRecognition; webkitSpeechRecognition?: typeof SpeechRecognition }).SpeechRecognition ||
      (window as typeof window & { webkitSpeechRecognition?: typeof SpeechRecognition }).webkitSpeechRecognition;

    if (!SpeechRecognitionAPI) {
      toast.error("Speech recognition not supported. Use Chrome or Safari.");
      return;
    }

    transcriptRef.current = "";
    resultSentRef.current = false;
    setLiveTranscript("");

    const rec = new SpeechRecognitionAPI();
    rec.lang = selectedLang === "de" ? "de-DE" : selectedLang === "hi" ? "hi-IN" : "en-US";
    rec.interimResults = true;  // capture partial results while speaking
    rec.maxAlternatives = 1;
    rec.continuous = true;      // keep listening until stop() is called

    rec.onresult = (e: SpeechRecognitionEvent) => {
      let interim = "";
      let final = "";
      for (let i = 0; i < e.results.length; i++) {
        if (e.results[i].isFinal) {
          final += e.results[i][0].transcript;
        } else {
          interim += e.results[i][0].transcript;
        }
      }
      const full = (final + interim).trim();
      transcriptRef.current = full;
      setLiveTranscript(full);
    };

    rec.onerror = (e: SpeechRecognitionErrorEvent) => {
      if (e.error !== "aborted" && e.error !== "no-speech") {
        toast.error("Could not understand audio. Please try again.");
      }
      setIsRecording(false);
      setLiveTranscript("");
    };

    rec.onend = () => {
      setIsRecording(false);
      setLiveTranscript("");
      // Send whatever was captured if not already sent
      if (!resultSentRef.current && transcriptRef.current.trim()) {
        resultSentRef.current = true;
        sendMessage(transcriptRef.current.trim());
        transcriptRef.current = "";
      }
    };

    speechRecRef.current = rec;
    rec.start();
    setIsRecording(true);
  };

  const stopRecording = () => {
    // stop() finalizes recognition and triggers onend, which sends the transcript
    speechRecRef.current?.stop();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  const QUICK_MESSAGES = [
    "Erkläre mir den Dativ",
    "Was bedeutet 'Feierabend'?",
    "Üb einen Job-Interview mit mir",
    "Korrigiere meinen Text",
  ];

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-3 border-b border-border bg-card">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-brand-500 to-purple-600 flex items-center justify-center">
            <Brain className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-semibold text-sm">GermanGPT Tutor</h1>
            <p className="text-xs text-muted-foreground">AI • Multi-Agent • RAG-powered</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Level selector */}
          <div className="relative">
            <select
              value={selectedLevel}
              onChange={(e) => setSelectedLevel(e.target.value)}
              className="appearance-none pl-3 pr-8 py-1.5 text-xs rounded-lg bg-secondary border border-border font-mono cursor-pointer"
            >
              {CEFR_LEVELS.map((l) => (
                <option key={l} value={l}>{l}</option>
              ))}
            </select>
            <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-3 h-3 text-muted-foreground pointer-events-none" />
          </div>

          <button
            onClick={() => setIsTTSEnabled((p) => !p)}
            className="p-1.5 rounded-lg hover:bg-secondary transition-colors"
            title={isTTSEnabled ? "Disable voice" : "Enable voice"}
          >
            {isTTSEnabled ? (
              <Volume2 className="w-4 h-4" />
            ) : (
              <VolumeX className="w-4 h-4 text-muted-foreground" />
            )}
          </button>

          <button
            onClick={() => setShowSettings((p) => !p)}
            className="p-1.5 rounded-lg hover:bg-secondary transition-colors"
          >
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6">
        {/* Quick action chips */}
        {messages.length === 1 && (
          <div className="flex flex-wrap gap-2 mb-4">
            {QUICK_MESSAGES.map((msg) => (
              <button
                key={msg}
                onClick={() => sendMessage(msg)}
                className="px-3 py-1.5 text-xs rounded-full bg-secondary border border-border hover:bg-brand-600/10 hover:border-brand-500/50 transition-all"
              >
                {msg}
              </button>
            ))}
          </div>
        )}

        <AnimatePresence>
          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div className={msg.role === "user" ? "chat-bubble-user" : "chat-bubble-ai"}>
                <div className="whitespace-pre-wrap text-sm leading-relaxed">
                  {msg.content}
                </div>

                {msg.grammarErrors && msg.grammarErrors.length > 0 && (
                  <GrammarFeedback errors={msg.grammarErrors} />
                )}

                {msg.xpEarned && msg.xpEarned > 0 && (
                  <div className="mt-2">
                    <span className="xp-badge">+{msg.xpEarned} XP</span>
                  </div>
                )}

                <p className="text-xs mt-2 opacity-40">
                  {msg.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                </p>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex justify-start"
          >
            <div className="chat-bubble-ai flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin text-brand-500" />
              <span className="text-sm text-muted-foreground">GermanGPT is thinking...</span>
            </div>
          </motion.div>
        )}

        {isRecording && (
          <div className="flex justify-end">
            <div className="chat-bubble-user flex flex-col gap-2 max-w-sm">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                <VoiceWave />
                <span className="text-xs text-muted-foreground">tap mic to send</span>
              </div>
              {liveTranscript && (
                <p className="text-sm italic opacity-75">{liveTranscript}</p>
              )}
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input bar */}
      <div className="border-t border-border bg-card px-4 py-3">
        <div className="flex items-end gap-3 max-w-4xl mx-auto">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Schreib auf Deutsch... (Write in German...)"
              rows={1}
              className="w-full resize-none rounded-2xl border border-border bg-secondary px-4 py-3 pr-12 text-sm outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 transition-all max-h-32 overflow-y-auto"
              style={{ minHeight: "48px" }}
            />
          </div>

          <button
            onClick={isRecording ? stopRecording : startRecording}
            className={`p-3 rounded-2xl transition-all ${
              isRecording
                ? "bg-red-500 text-white shadow-glow-green animate-pulse"
                : "bg-secondary border border-border hover:bg-brand-600/20 hover:border-brand-500/50"
            }`}
          >
            {isRecording ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
          </button>

          <button
            onClick={() => sendMessage(input)}
            disabled={!input.trim() || loading}
            className="p-3 rounded-2xl bg-brand-600 text-white disabled:opacity-50 disabled:cursor-not-allowed hover:bg-brand-500 transition-all hover:shadow-glow-brand"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>

        <p className="text-center text-xs text-muted-foreground mt-2">
          Press Enter to send • Shift+Enter for new line • 🎤 for voice input
        </p>
      </div>
    </div>
  );
}

export default function TutorPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-background flex items-center justify-center"><div className="w-8 h-8 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" /></div>}>
      <TutorPageInner />
    </Suspense>
  );
}
