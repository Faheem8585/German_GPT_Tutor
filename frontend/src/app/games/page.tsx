"use client";

import { useState, useEffect, useRef } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import {
  Trophy,
  Clock,
  Zap,
  ChevronRight,
  RotateCcw,
  Flame,
  Volume2,
  Mic,
  MicOff,
} from "lucide-react";
import { gamesApi } from "@/lib/api";
import { useUserStore } from "@/stores/userStore";
import toast from "react-hot-toast";

interface GameType {
  type: string;
  name: string;
  name_de: string;
  description: string;
  xp_per_correct: number;
  time_limit: number;
  icon: string;
}

interface Question {
  german?: string;
  english?: string;
  options?: string[];
  correct?: number | string;
  scrambled?: string[];
  sentence?: string;
  answer?: string;
  hint?: string;
  translation?: string;
  example?: string;
  question?: string;
  explanation?: string;
}

interface GameState {
  gameId: string;
  gameType: string;
  questions: Question[];
  timeLimit: number;
  xpPerCorrect: number;
  currentIndex: number;
  answers: Record<string, unknown>[];
  startTime: number;
  finished: boolean;
  result: Record<string, unknown> | null;
}

function speakGerman(text: string) {
  if (typeof window === "undefined" || !window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  const utt = new SpeechSynthesisUtterance(text);
  utt.lang = "de-DE";
  utt.rate = 0.85;
  window.speechSynthesis.speak(utt);
}

function GameCard({ game, onStart }: { game: GameType; onStart: (type: string) => void }) {
  return (
    <motion.div
      whileHover={{ y: -4, scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className="glass-card p-6 cursor-pointer group"
      onClick={() => onStart(game.type)}
    >
      <div className="text-4xl mb-3">{game.icon}</div>
      <h3 className="font-bold mb-1">{game.name}</h3>
      <p className="text-xs text-muted-foreground mb-1">{game.name_de}</p>
      <p className="text-sm text-muted-foreground mb-4">{game.description}</p>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          <span className="flex items-center gap-1">
            <Zap className="w-3 h-3 text-amber-500" />
            {game.xp_per_correct} XP/correct
          </span>
          <span className="flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {game.time_limit}s
          </span>
        </div>
        <ChevronRight className="w-4 h-4 text-muted-foreground group-hover:text-brand-500 group-hover:translate-x-1 transition-all" />
      </div>
    </motion.div>
  );
}

function VocabularyBattle({ question, onAnswer }: { question: Question; onAnswer: (a: unknown) => void }) {
  const [selected, setSelected] = useState<number | null>(null);

  const handleSelect = (idx: number) => {
    if (selected !== null) return;
    setSelected(idx);
    setTimeout(() => { onAnswer(idx); setSelected(null); }, 700);
  };

  return (
    <div className="space-y-4">
      <div className="text-center py-8">
        <p className="text-sm text-muted-foreground mb-2">What does this mean?</p>
        <p className="text-4xl font-bold font-mono">{question.german}</p>
      </div>
      <div className="grid grid-cols-2 gap-3">
        {(question.options ?? []).map((opt, idx) => (
          <motion.button key={idx} whileTap={{ scale: 0.97 }} onClick={() => handleSelect(idx)}
            className={`p-4 rounded-xl border-2 text-left transition-all font-medium ${
              selected === null
                ? "border-border hover:border-brand-500 hover:bg-brand-500/10"
                : selected === idx
                ? idx === question.correct ? "border-green-500 bg-green-500/20 text-green-600" : "border-red-500 bg-red-500/20 text-red-600"
                : idx === question.correct ? "border-green-500 bg-green-500/10" : "border-border opacity-50"
            }`}>
            <span className="text-muted-foreground text-xs mr-2">{["A", "B", "C", "D"][idx]}.</span>
            {opt}
          </motion.button>
        ))}
      </div>
    </div>
  );
}

function WordMatch({ question, onAnswer }: { question: Question; onAnswer: (a: unknown) => void }) {
  const [input, setInput] = useState("");

  return (
    <div className="space-y-6">
      <div className="text-center py-8">
        <p className="text-lg text-muted-foreground mb-2">What does this mean in English?</p>
        <p className="text-5xl font-bold font-mono">{question.german ?? "—"}</p>
        {question.example && <p className="text-sm text-muted-foreground mt-4 italic">Beispiel: {question.example}</p>}
      </div>
      <div className="flex gap-3">
        <input value={input} onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && onAnswer(input)}
          placeholder="Type the English meaning..."
          className="flex-1 px-4 py-3 rounded-xl border border-border bg-secondary outline-none focus:border-brand-500 text-sm"
          autoFocus />
        <button onClick={() => onAnswer(input)}
          className="px-6 py-3 bg-brand-600 text-white rounded-xl font-medium hover:bg-brand-500 transition-colors">
          Check
        </button>
      </div>
    </div>
  );
}

function SentenceBuilder({ question, onAnswer }: { question: Question; onAnswer: (a: unknown) => void }) {
  const [chosen, setChosen] = useState<string[]>([]);
  const [pool, setPool] = useState<string[]>([...(question.scrambled ?? [])]);

  useEffect(() => {
    setChosen([]);
    setPool([...(question.scrambled ?? [])]);
  }, [question]);

  const addWord = (word: string, idx: number) => {
    setChosen((p) => [...p, word]);
    setPool((p) => p.filter((_, i) => i !== idx));
  };
  const removeWord = (idx: number) => {
    const w = chosen[idx];
    setChosen((p) => p.filter((_, i) => i !== idx));
    setPool((p) => [...p, w]);
  };

  return (
    <div className="space-y-5">
      <div className="text-center py-4">
        <p className="text-lg text-muted-foreground mb-1">Arrange into a correct German sentence</p>
        {question.translation && <p className="text-sm text-muted-foreground italic">Meaning: {question.translation}</p>}
      </div>
      <div className="min-h-[56px] p-3 rounded-xl border-2 border-dashed border-brand-500/40 bg-brand-500/5 flex flex-wrap gap-2">
        {chosen.length === 0 && <span className="text-muted-foreground text-sm self-center">Click words below to build the sentence</span>}
        {chosen.map((w, i) => (
          <button key={i} onClick={() => removeWord(i)}
            className="px-3 py-1.5 bg-brand-600 text-white rounded-lg text-sm font-mono hover:bg-red-500 transition-colors">
            {w}
          </button>
        ))}
      </div>
      <div className="flex flex-wrap gap-2">
        {pool.map((w, i) => (
          <button key={i} onClick={() => addWord(w, i)}
            className="px-3 py-1.5 bg-secondary border border-border rounded-lg text-sm font-mono hover:border-brand-500 hover:bg-brand-500/10 transition-colors">
            {w}
          </button>
        ))}
      </div>
      <button onClick={() => onAnswer(chosen.join(" "))} disabled={chosen.length === 0}
        className="w-full py-3 bg-brand-600 text-white rounded-xl font-medium hover:bg-brand-500 transition-colors disabled:opacity-40">
        Submit Sentence
      </button>
    </div>
  );
}

function FillInBlank({ question, onAnswer }: { question: Question; onAnswer: (a: unknown) => void }) {
  const [input, setInput] = useState("");
  const raw = question.sentence ?? "___";
  const parts = raw.includes("___") ? raw.split("___") : [raw, ""];

  return (
    <div className="space-y-6">
      <div className="text-center py-6">
        <p className="text-lg text-muted-foreground mb-4">Fill in the blank</p>
        <p className="text-2xl font-bold font-mono leading-relaxed">
          {parts[0]}
          <span className="inline-block min-w-[100px] border-b-2 border-brand-500 text-brand-400 mx-1 text-center">
            {input || "___"}
          </span>
          {parts[1]}
        </p>
        {question.hint && <p className="text-sm text-amber-500 mt-3">💡 Hint: {question.hint}</p>}
      </div>
      <div className="flex gap-3">
        <input value={input} onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && onAnswer(input)}
          placeholder="Type the missing word..."
          className="flex-1 px-4 py-3 rounded-xl border border-border bg-secondary outline-none focus:border-brand-500 text-sm"
          autoFocus />
        <button onClick={() => onAnswer(input)}
          className="px-6 py-3 bg-brand-600 text-white rounded-xl font-medium hover:bg-brand-500 transition-colors">
          Check
        </button>
      </div>
    </div>
  );
}

function ListeningQuiz({ question, onAnswer }: { question: Question; onAnswer: (a: unknown) => void }) {
  const [selected, setSelected] = useState<string | null>(null);
  const [played, setPlayed] = useState(false);

  const textToPlay = question.sentence ?? question.german ?? question.question ?? "";
  const options: string[] = question.options ?? [];

  const handlePlay = () => {
    speakGerman(textToPlay);
    setPlayed(true);
  };

  const handleSelect = (letter: string) => {
    if (selected !== null) return;
    setSelected(letter);
    setTimeout(() => { onAnswer(letter); setSelected(null); }, 700);
  };

  const letterMap: Record<string, string> = { "a": "A", "b": "B", "c": "C", "d": "D" };

  return (
    <div className="space-y-5">
      <div className="text-center py-6">
        <p className="text-lg text-muted-foreground mb-4">Listen and answer</p>
        <button onClick={handlePlay}
          className="flex items-center gap-2 px-6 py-3 bg-brand-600 text-white rounded-2xl font-semibold hover:bg-brand-500 transition-colors mx-auto">
          <Volume2 className="w-5 h-5" />
          {played ? "Play Again" : "Play Audio 🔊"}
        </button>
        {textToPlay && <p className="text-sm text-muted-foreground mt-3 italic">(Click to hear the German)</p>}
        {question.question && <p className="text-base font-semibold mt-4">{question.question}</p>}
      </div>
      <div className="grid grid-cols-2 gap-3">
        {options.map((opt, idx) => {
          const letter = ["a", "b", "c", "d"][idx];
          const isCorrect = question.correct === letter || question.correct === idx;
          return (
            <motion.button key={idx} whileTap={{ scale: 0.97 }} onClick={() => handleSelect(letter)}
              className={`p-4 rounded-xl border-2 text-left transition-all font-medium ${
                selected === null
                  ? "border-border hover:border-brand-500 hover:bg-brand-500/10"
                  : selected === letter
                  ? isCorrect ? "border-green-500 bg-green-500/20 text-green-600" : "border-red-500 bg-red-500/20 text-red-600"
                  : isCorrect ? "border-green-500 bg-green-500/10" : "border-border opacity-50"
              }`}>
              <span className="text-muted-foreground text-xs mr-2">{letterMap[letter]}.</span>
              {opt.replace(/^[a-d]\)\s*/i, "")}
            </motion.button>
          );
        })}
      </div>
    </div>
  );
}

function PronunciationChallenge({ question, onAnswer }: { question: Question; onAnswer: (a: unknown) => void }) {
  const [recording, setRecording] = useState(false);
  const [heard, setHeard] = useState<string | null>(null);
  const recRef = useRef<SpeechRecognition | null>(null);

  const word = question.german ?? "Hallo";

  const startRecording = () => {
    const SR = (window as unknown as Record<string, unknown>)["SpeechRecognition"] as typeof SpeechRecognition | undefined
      ?? (window as unknown as Record<string, unknown>)["webkitSpeechRecognition"] as typeof SpeechRecognition | undefined;
    if (!SR) { toast.error("Speech recognition requires Chrome or Safari."); return; }
    const rec = new SR();
    rec.lang = "de-DE";
    rec.interimResults = false;
    rec.onresult = (e: SpeechRecognitionEvent) => {
      const spoken = e.results[0][0].transcript.trim();
      setHeard(spoken);
    };
    rec.onerror = () => { toast.error("Could not hear. Try again."); setRecording(false); };
    rec.onend = () => setRecording(false);
    recRef.current = rec;
    rec.start();
    setRecording(true);
  };

  const submit = () => onAnswer(heard ?? "");

  return (
    <div className="space-y-6">
      <div className="text-center py-6">
        <p className="text-lg text-muted-foreground mb-2">Pronounce this word in German</p>
        <p className="text-6xl font-bold font-mono mb-2">{word}</p>
        {question.english && <p className="text-muted-foreground text-lg">({question.english})</p>}
        {question.example && <p className="text-sm text-muted-foreground mt-3 italic">{question.example}</p>}
        <button onClick={() => speakGerman(word)}
          className="flex items-center gap-2 px-4 py-2 bg-secondary border border-border rounded-xl text-sm hover:border-brand-500 transition-colors mx-auto mt-4">
          <Volume2 className="w-4 h-4" /> Hear example
        </button>
      </div>
      <div className="flex flex-col items-center gap-4">
        <button onClick={recording ? () => { recRef.current?.stop(); } : startRecording}
          className={`flex items-center gap-2 px-8 py-4 rounded-2xl font-semibold transition-colors ${
            recording ? "bg-red-500 text-white animate-pulse" : "bg-brand-600 text-white hover:bg-brand-500"
          }`}>
          {recording ? <><MicOff className="w-5 h-5" /> Stop Recording</> : <><Mic className="w-5 h-5" /> Record Pronunciation</>}
        </button>
        {heard && (
          <div className="text-center">
            <p className="text-sm text-muted-foreground">You said:</p>
            <p className="text-xl font-mono font-bold">{heard}</p>
            <button onClick={submit}
              className="mt-3 px-6 py-2 bg-green-600 text-white rounded-xl font-medium hover:bg-green-500 transition-colors">
              Submit ✓
            </button>
          </div>
        )}
        {!heard && !recording && (
          <button onClick={() => onAnswer("(skipped)")}
            className="text-sm text-muted-foreground underline hover:text-foreground transition-colors">
            Skip this word
          </button>
        )}
      </div>
    </div>
  );
}

function ResultScreen({ result, onReplay }: { result: Record<string, unknown>; onReplay: () => void }) {
  const accuracy = (result.accuracy_percent as number) ?? 0;
  const perfect = accuracy === 100;

  return (
    <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="text-center space-y-6 py-8">
      <div className="text-6xl">{perfect ? "🏆" : accuracy >= 70 ? "⭐" : "💪"}</div>
      <div>
        <h2 className="text-3xl font-bold mb-2">{perfect ? "Perfekt!" : accuracy >= 70 ? "Sehr gut!" : "Gut versucht!"}</h2>
        <p className="text-muted-foreground">{perfect ? "Flawless game! You're amazing!" : "Keep practicing to improve!"}</p>
      </div>

      <div className="grid grid-cols-3 gap-4 max-w-sm mx-auto">
        {[
          { label: "Accuracy", value: `${Math.round(accuracy)}%` },
          { label: "XP Earned", value: `+${result.xp_earned ?? 0}` },
          { label: "Score", value: `${result.correct_answers ?? 0}/${result.total_questions ?? 0}` },
        ].map((stat) => (
          <div key={stat.label} className="glass-card p-3 text-center">
            <div className="text-xl font-bold text-brand-500">{stat.value}</div>
            <div className="text-xs text-muted-foreground">{stat.label}</div>
          </div>
        ))}
      </div>

      {((result.new_achievements as unknown[]) ?? []).length > 0 && (
        <div>
          <h3 className="font-semibold mb-3 flex items-center justify-center gap-2">
            <Trophy className="w-4 h-4 text-amber-500" /> New Achievements!
          </h3>
          <div className="space-y-2">
            {(result.new_achievements as Record<string, unknown>[]).map((ach) => (
              <div key={ach.name as string}
                className="flex items-center gap-3 px-4 py-2 bg-amber-500/10 border border-amber-500/20 rounded-xl">
                <Trophy className="w-4 h-4 text-amber-500" />
                <div className="text-left">
                  <div className="font-medium text-sm">{ach.name as string}</div>
                  <div className="text-xs text-muted-foreground">{ach.description as string}</div>
                </div>
                <span className="ml-auto xp-badge">+{ach.xp as number} XP</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <button onClick={onReplay}
        className="flex items-center gap-2 px-8 py-3 bg-brand-600 text-white rounded-2xl font-semibold hover:bg-brand-500 transition-colors mx-auto">
        <RotateCcw className="w-4 h-4" /> Play Again
      </button>
    </motion.div>
  );
}

export default function GamesPage() {
  const { cefrLevel, addXP } = useUserStore();
  const [gameState, setGameState] = useState<GameState | null>(null);

  const { data: gameTypes } = useQuery({
    queryKey: ["game-types"],
    queryFn: () => gamesApi.getGameTypes(),
    select: (r) => r.data.games as GameType[],
  });

  const { data: leaderboard } = useQuery({
    queryKey: ["leaderboard"],
    queryFn: () => gamesApi.getLeaderboard(),
    select: (r) => r.data.leaderboard,
  });

  const createGameMutation = useMutation({
    mutationFn: (gameType: string) =>
      gamesApi.createGame({ game_type: gameType, cefr_level: cefrLevel }),
    onSuccess: (res, gameType) => {
      const data = res.data;
      setGameState({
        gameId: data.game_id,
        gameType,
        questions: data.questions,
        timeLimit: data.time_limit_seconds,
        xpPerCorrect: data.xp_per_correct,
        currentIndex: 0,
        answers: [],
        startTime: Date.now(),
        finished: false,
        result: null,
      });
    },
    onError: () => toast.error("Failed to create game. Please try again."),
  });

  const submitMutation = useMutation({
    mutationFn: (state: GameState) =>
      gamesApi.submitResult({
        game_id: state.gameId,
        answers: state.answers,
        questions: state.questions as Record<string, unknown>[],
        game_type: state.gameType,
        time_taken_seconds: (Date.now() - state.startTime) / 1000,
        cefr_level: cefrLevel,
      }),
    onSuccess: (res) => {
      const data = res.data;
      setGameState((prev) => prev ? { ...prev, finished: true, result: data } : null);
      if ((data.xp_earned ?? 0) > 0) {
        addXP(data.xp_earned);
        toast.success(`+${data.xp_earned} XP earned! 🎉`);
      }
    },
    onError: () => {
      toast.error("Failed to submit game. Your progress is saved locally.");
      setGameState((prev) => prev ? { ...prev, finished: true, result: { accuracy_percent: 0, xp_earned: 0, correct_answers: 0, total_questions: prev.questions.length, new_achievements: [] } } : null);
    },
  });

  const handleAnswer = (answer: unknown) => {
    if (!gameState) return;
    const newAnswers = [...gameState.answers, { answer, question_index: gameState.currentIndex }];
    const nextIndex = gameState.currentIndex + 1;
    if (nextIndex >= gameState.questions.length) {
      const finalState = { ...gameState, answers: newAnswers, currentIndex: nextIndex };
      setGameState(finalState);
      submitMutation.mutate(finalState);
    } else {
      setGameState({ ...gameState, answers: newAnswers, currentIndex: nextIndex });
    }
  };

  // Result screen
  if (gameState?.finished && gameState.result) {
    return (
      <div className="min-h-screen bg-background p-6 flex items-center justify-center">
        <div className="max-w-lg w-full glass-card p-8">
          <ResultScreen result={gameState.result} onReplay={() => setGameState(null)} />
        </div>
      </div>
    );
  }

  // Active game
  if (gameState && !gameState.finished) {
    const current = gameState.questions[gameState.currentIndex];
    const progress = (gameState.currentIndex / gameState.questions.length) * 100;

    const renderQuestion = () => {
      if (!current) return <p className="text-center text-muted-foreground">Loading question...</p>;
      switch (gameState.gameType) {
        case "vocabulary_battle":
          return <VocabularyBattle key={gameState.currentIndex} question={current} onAnswer={handleAnswer} />;
        case "sentence_builder":
          return <SentenceBuilder key={gameState.currentIndex} question={current} onAnswer={handleAnswer} />;
        case "fill_in_blank":
          return <FillInBlank key={gameState.currentIndex} question={current} onAnswer={handleAnswer} />;
        case "listening_quiz":
          return <ListeningQuiz key={gameState.currentIndex} question={current} onAnswer={handleAnswer} />;
        case "pronunciation_challenge":
          return <PronunciationChallenge key={gameState.currentIndex} question={current} onAnswer={handleAnswer} />;
        default:
          return <WordMatch key={gameState.currentIndex} question={current} onAnswer={handleAnswer} />;
      }
    };

    return (
      <div className="min-h-screen bg-background p-6">
        <div className="max-w-2xl mx-auto">
          <div className="flex items-center justify-between mb-6">
            <div>
              <span className="text-sm text-muted-foreground">Question</span>
              <p className="font-bold">{gameState.currentIndex + 1} / {gameState.questions.length}</p>
            </div>
            <div className="flex items-center gap-2 px-3 py-1.5 bg-brand-500/10 rounded-lg">
              <Zap className="w-4 h-4 text-brand-500" />
              <span className="text-sm font-semibold text-brand-500">{gameState.xpPerCorrect} XP/correct</span>
            </div>
            <button onClick={() => setGameState(null)} className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Exit
            </button>
          </div>

          <div className="h-2 bg-secondary rounded-full mb-8 overflow-hidden">
            <motion.div animate={{ width: `${progress}%` }} className="h-full bg-gradient-to-r from-brand-500 to-purple-500 rounded-full" />
          </div>

          <div className="glass-card p-8">
            <AnimatePresence mode="wait">
              <motion.div key={gameState.currentIndex} initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -30 }}>
                {renderQuestion()}
              </motion.div>
            </AnimatePresence>
          </div>
        </div>
      </div>
    );
  }

  // Game lobby
  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-6xl mx-auto space-y-8">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Trophy className="w-8 h-8 text-amber-500" /> Game Center
          </h1>
          <p className="text-muted-foreground mt-1">Level {cefrLevel} • Learn German through fun, addictive games</p>
        </div>

        {createGameMutation.isPending && (
          <div className="text-center py-12">
            <div className="inline-flex items-center gap-3 px-6 py-3 bg-brand-500/10 rounded-2xl">
              <div className="w-5 h-5 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
              <span>AI is generating your game...</span>
            </div>
          </div>
        )}

        {!createGameMutation.isPending && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {gameTypes?.map((game) => (
              <GameCard key={game.type} game={game} onStart={(type) => createGameMutation.mutate(type)} />
            ))}
          </div>
        )}

        <div>
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Flame className="w-5 h-5 text-orange-500" /> Leaderboard
          </h2>
          <div className="glass-card overflow-hidden">
            {leaderboard?.map((entry: Record<string, unknown>, i: number) => (
              <div key={i} className={`flex items-center gap-4 px-6 py-4 ${i < leaderboard.length - 1 ? "border-b border-border" : ""} ${entry.username === "You" ? "bg-brand-500/5" : ""}`}>
                <span className={`w-7 h-7 rounded-full flex items-center justify-center text-sm font-bold ${i === 0 ? "bg-amber-500 text-black" : i === 1 ? "bg-gray-400 text-black" : i === 2 ? "bg-amber-700 text-white" : "bg-secondary text-foreground"}`}>
                  {entry.rank as number}
                </span>
                <div className="flex-1">
                  <p className={`font-medium ${entry.username === "You" ? "text-brand-500" : ""}`}>{entry.username as string}</p>
                  <p className="text-xs text-muted-foreground">Level {entry.level as string} • {entry.streak as number} day streak</p>
                </div>
                <div className="flex items-center gap-1">
                  <Zap className="w-4 h-4 text-amber-500" />
                  <span className="font-bold">{(entry.xp as number).toLocaleString()}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
