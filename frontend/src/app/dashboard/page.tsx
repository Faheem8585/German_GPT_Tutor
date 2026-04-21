"use client";

import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import Link from "next/link";
import {
  Flame,
  Zap,
  Trophy,
  Target,
  TrendingUp,
  MessageSquare,
  Gamepad2,
  BookOpen,
  Mic,
  ChevronRight,
  Calendar,
  Award,
  Star,
} from "lucide-react";
import { analyticsApi, gamesApi } from "@/lib/api";
import {
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";
import { useUserStore } from "@/stores/userStore";

function StatCard({
  icon,
  label,
  value,
  sub,
  color,
}: {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  sub?: string;
  color: string;
}) {
  return (
    <motion.div
      whileHover={{ y: -2 }}
      className="glass-card p-5 flex items-center gap-4"
    >
      <div className={`w-12 h-12 rounded-xl ${color} flex items-center justify-center text-white flex-shrink-0`}>
        {icon}
      </div>
      <div>
        <p className="text-sm text-muted-foreground">{label}</p>
        <p className="text-2xl font-bold">{value}</p>
        {sub && <p className="text-xs text-muted-foreground mt-0.5">{sub}</p>}
      </div>
    </motion.div>
  );
}

const QUICK_ACTIONS = [
  {
    href: "/tutor",
    icon: <MessageSquare className="w-6 h-6" />,
    label: "AI Tutor Chat",
    sublabel: "Practice conversation",
    color: "from-brand-600 to-purple-600",
  },
  {
    href: "/games",
    icon: <Gamepad2 className="w-6 h-6" />,
    label: "Play Games",
    sublabel: "Earn XP while learning",
    color: "from-amber-500 to-orange-600",
  },
  {
    href: "/tutor?mode=voice",
    icon: <Mic className="w-6 h-6" />,
    label: "Voice Practice",
    sublabel: "Improve pronunciation",
    color: "from-pink-500 to-rose-600",
  },
  {
    href: "/lessons",
    icon: <BookOpen className="w-6 h-6" />,
    label: "Lessons",
    sublabel: "Structured learning",
    color: "from-green-500 to-emerald-600",
  },
];

export default function DashboardPage() {
  const { xp, streak, cefrLevel } = useUserStore();

  const { data: dashData } = useQuery({
    queryKey: ["dashboard"],
    queryFn: () => analyticsApi.getDashboard(),
    select: (r) => r.data,
  });

  const { data: timelineData } = useQuery({
    queryKey: ["timeline"],
    queryFn: () => analyticsApi.getTimeline(),
    select: (r) => r.data.timeline,
  });

  const { data: missions } = useQuery({
    queryKey: ["missions", cefrLevel],
    queryFn: () => gamesApi.getDailyMissions(cefrLevel),
    select: (r) => r.data,
  });

  const summary = dashData?.summary;
  const skillBreakdown = dashData?.skill_breakdown;

  const radarData = skillBreakdown
    ? Object.entries(skillBreakdown).map(([name, value]) => ({
        skill: name.charAt(0).toUpperCase() + name.slice(1),
        score: value,
      }))
    : [];

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Guten Morgen! 👋</h1>
            <p className="text-muted-foreground mt-1">
              Level {summary?.level ?? cefrLevel} • Keep up the great work!
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-4 py-2 bg-orange-500/10 border border-orange-500/20 rounded-xl">
              <Flame className="w-5 h-5 text-orange-500 streak-flame" />
              <span className="font-bold text-orange-500">{streak ?? 0}</span>
              <span className="text-sm text-muted-foreground">day streak</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 bg-brand-500/10 border border-brand-500/20 rounded-xl">
              <Zap className="w-5 h-5 text-brand-500" />
              <span className="font-bold text-brand-500">{xp.toLocaleString()}</span>
              <span className="text-sm text-muted-foreground">XP</span>
            </div>
          </div>
        </div>

        {/* Level Progress */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="level-badge">{summary?.level ?? cefrLevel}</div>
              <div>
                <p className="font-semibold">Current Level</p>
                <p className="text-sm text-muted-foreground">
                  {summary?.xp_to_next_level?.toLocaleString() ?? "..."} XP to next level
                </p>
              </div>
            </div>
            <span className="text-2xl font-bold text-brand-500">
              {summary?.level_progress_percent ?? 0}%
            </span>
          </div>
          <div className="h-3 bg-secondary rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${summary?.level_progress_percent ?? 0}%` }}
              transition={{ duration: 1, ease: "easeOut" }}
              className="h-full bg-gradient-to-r from-brand-500 to-purple-500 rounded-full"
            />
          </div>
        </motion.div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard
            icon={<Trophy className="w-6 h-6" />}
            label="Total XP"
            value={(xp || summary?.xp_points || 0).toLocaleString()}
            sub="Lifetime earned"
            color="bg-gradient-to-br from-amber-500 to-orange-600"
          />
          <StatCard
            icon={<Flame className="w-6 h-6" />}
            label="Streak"
            value={`${streak || 0} days`}
            sub="Keep it going!"
            color="bg-gradient-to-br from-orange-500 to-red-600"
          />
          <StatCard
            icon={<Target className="w-6 h-6" />}
            label="Level"
            value={summary?.level ?? cefrLevel}
            sub="CEFR certification"
            color="bg-gradient-to-br from-brand-500 to-purple-600"
          />
          <StatCard
            icon={<Calendar className="w-6 h-6" />}
            label="Weekly Goal"
            value={`${summary ? Math.round((missions?.completed_minutes ?? 47) / 150 * 100) : 0}%`}
            sub="150 min target"
            color="bg-gradient-to-br from-green-500 to-emerald-600"
          />
        </div>

        {/* Quick Actions */}
        <div>
          <h2 className="text-lg font-semibold mb-4">Continue Learning</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {QUICK_ACTIONS.map((action) => (
              <Link key={action.href} href={action.href}>
                <motion.div
                  whileHover={{ y: -3, scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="glass-card p-5 cursor-pointer group h-full"
                >
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${action.color} flex items-center justify-center text-white mb-3 group-hover:scale-110 transition-transform`}>
                    {action.icon}
                  </div>
                  <p className="font-semibold text-sm">{action.label}</p>
                  <p className="text-xs text-muted-foreground mt-1">{action.sublabel}</p>
                </motion.div>
              </Link>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* XP Timeline */}
          <div className="glass-card p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-brand-500" />
              Weekly XP Progress
            </h2>
            {timelineData && (
              <ResponsiveContainer width="100%" height={200}>
                <AreaChart data={timelineData}>
                  <defs>
                    <linearGradient id="xpGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#a855f7" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#a855f7" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="date" tick={{ fontSize: 10 }} tickFormatter={(d) => d.slice(5)} />
                  <YAxis tick={{ fontSize: 10 }} />
                  <Tooltip />
                  <Area
                    type="monotone"
                    dataKey="xp_earned"
                    stroke="#a855f7"
                    fill="url(#xpGradient)"
                    strokeWidth={2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>

          {/* Skill Radar */}
          <div className="glass-card p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Star className="w-5 h-5 text-amber-500" />
              Skill Breakdown
            </h2>
            {radarData.length > 0 && (
              <ResponsiveContainer width="100%" height={200}>
                <RadarChart data={radarData}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="skill" tick={{ fontSize: 10 }} />
                  <Radar
                    name="Skills"
                    dataKey="score"
                    stroke="#a855f7"
                    fill="#a855f7"
                    fillOpacity={0.3}
                  />
                </RadarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Daily Missions */}
        {missions?.missions && (
          <div>
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Award className="w-5 h-5 text-amber-500" />
              Daily Missions
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {missions.missions.map((mission: Record<string, unknown>) => (
                <motion.div
                  key={mission.id as string}
                  whileHover={{ y: -2 }}
                  className="glass-card p-5"
                >
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-sm font-semibold">{mission.title as string}</span>
                    <span className="xp-badge">+{mission.xp_reward as number} XP</span>
                  </div>
                  <p className="text-xs text-muted-foreground mb-3">{mission.description as string}</p>
                  <Link
                    href="/games"
                    className="flex items-center gap-1 text-xs text-brand-500 hover:text-brand-400 transition-colors font-medium"
                  >
                    Start mission <ChevronRight className="w-3 h-3" />
                  </Link>
                </motion.div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
