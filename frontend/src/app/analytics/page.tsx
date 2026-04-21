"use client";

import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  TrendingUp,
  Brain,
  Zap,
  AlertTriangle,
  CheckCircle,
  Server,
  Activity,
  Users,
  Globe,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
} from "recharts";
import { analyticsApi } from "@/lib/api";

function MetricCard({
  icon,
  label,
  value,
  sub,
  status,
}: {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  sub?: string;
  status?: "good" | "warn" | "neutral";
}) {
  return (
    <div className="glass-card p-5">
      <div className="flex items-center justify-between mb-3">
        <span className="text-muted-foreground text-sm">{label}</span>
        <div className={`p-2 rounded-lg ${
          status === "good" ? "bg-green-500/10 text-green-500" :
          status === "warn" ? "bg-amber-500/10 text-amber-500" :
          "bg-brand-500/10 text-brand-500"
        }`}>
          {icon}
        </div>
      </div>
      <p className="text-2xl font-bold">{value}</p>
      {sub && <p className="text-xs text-muted-foreground mt-1">{sub}</p>}
    </div>
  );
}

export default function AnalyticsPage() {
  const { data: dashboard } = useQuery({
    queryKey: ["dashboard"],
    queryFn: () => analyticsApi.getDashboard(),
    select: (r) => r.data,
  });

  const { data: timeline } = useQuery({
    queryKey: ["timeline"],
    queryFn: () => analyticsApi.getTimeline(),
    select: (r) => r.data.timeline,
  });

  const { data: mistakes } = useQuery({
    queryKey: ["mistakes"],
    queryFn: () => analyticsApi.getMistakes(),
    select: (r) => r.data,
  });

  const { data: aiMetrics } = useQuery({
    queryKey: ["ai-metrics"],
    queryFn: () => analyticsApi.getAIMetrics(),
    select: (r) => r.data,
  });

  const { data: platformStats } = useQuery({
    queryKey: ["platform-stats"],
    queryFn: () => analyticsApi.getPlatformStats(),
    select: (r) => r.data,
  });

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <TrendingUp className="w-8 h-8 text-brand-500" />
            Analytics Dashboard
          </h1>
          <p className="text-muted-foreground mt-1">
            Learning progress, AI performance, and platform insights
          </p>
        </div>

        {/* Learning Progress */}
        <div>
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Activity className="w-5 h-5" />
            Your Learning Progress
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <MetricCard
              icon={<Zap className="w-4 h-4" />}
              label="Total XP"
              value={dashboard?.summary?.xp_points?.toLocaleString() ?? 0}
              status="good"
            />
            <MetricCard
              icon={<TrendingUp className="w-4 h-4" />}
              label="CEFR Level"
              value={dashboard?.summary?.level ?? "A1"}
              sub="Current level"
              status="good"
            />
            <MetricCard
              icon={<CheckCircle className="w-4 h-4" />}
              label="Weekly Goal"
              value={`${dashboard?.weekly_goal?.completed_minutes ?? 0}/150 min`}
              status={
                (dashboard?.weekly_goal?.completed_minutes ?? 0) >= 100 ? "good" : "warn"
              }
            />
            <MetricCard
              icon={<AlertTriangle className="w-4 h-4" />}
              label="Weak Areas"
              value={dashboard?.weak_areas?.length ?? 0}
              sub="Grammar topics to focus on"
              status="warn"
            />
          </div>
        </div>

        {/* XP Chart */}
        {timeline && (
          <div className="glass-card p-6">
            <h3 className="font-semibold mb-4">XP Earned — Last 7 Days</h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={timeline}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.1} />
                <XAxis dataKey="date" tick={{ fontSize: 10 }} tickFormatter={(d) => d.slice(5)} />
                <YAxis tick={{ fontSize: 10 }} />
                <Tooltip />
                <Bar dataKey="xp_earned" fill="#a855f7" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Grammar Mistakes */}
        {mistakes?.top_mistakes && (
          <div className="glass-card p-6">
            <h3 className="font-semibold mb-2">Top Grammar Mistakes</h3>
            <p className="text-sm text-muted-foreground mb-4">{mistakes.recommendation}</p>
            <div className="space-y-3">
              {mistakes.top_mistakes.map((m: Record<string, unknown>, i: number) => (
                <div key={i} className="flex items-center gap-4">
                  <span className="text-sm font-medium w-48 flex-shrink-0">{m.rule as string}</span>
                  <div className="flex-1 h-2 bg-secondary rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${m.mastery_percent as number}%` }}
                      transition={{ duration: 1, delay: i * 0.1 }}
                      className={`h-full rounded-full ${
                        (m.mastery_percent as number) >= 70 ? "bg-green-500" :
                        (m.mastery_percent as number) >= 50 ? "bg-amber-500" :
                        "bg-red-500"
                      }`}
                    />
                  </div>
                  <span className="text-sm text-muted-foreground w-12 text-right">
                    {m.mastery_percent as number}%
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {m.frequency as number}× errors
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* AI Performance Metrics */}
        {aiMetrics && (
          <div>
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Brain className="w-5 h-5 text-brand-500" />
              AI System Performance
              <span className="text-xs text-muted-foreground bg-secondary px-2 py-1 rounded-full">
                Recruiter View
              </span>
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <MetricCard
                icon={<Activity className="w-4 h-4" />}
                label="Avg Response Latency"
                value={`${aiMetrics.llm_stats.avg_response_latency_ms}ms`}
                sub="P95: 2100ms"
                status="good"
              />
              <MetricCard
                icon={<Server className="w-4 h-4" />}
                label="Tokens Today"
                value={aiMetrics.llm_stats.total_tokens_today.toLocaleString()}
                sub={`$${aiMetrics.llm_stats.cost_today_usd} cost`}
                status="neutral"
              />
              <MetricCard
                icon={<CheckCircle className="w-4 h-4" />}
                label="Quality Score"
                value={`${(aiMetrics.eval_stats.avg_quality_score * 100).toFixed(0)}%`}
                sub="LLM-as-judge eval"
                status="good"
              />
              <MetricCard
                icon={<AlertTriangle className="w-4 h-4" />}
                label="Hallucination Rate"
                value={`${(aiMetrics.eval_stats.hallucination_rate * 100).toFixed(1)}%`}
                sub="Safety pass: 99%"
                status="good"
              />
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
              <MetricCard
                icon={<Brain className="w-4 h-4" />}
                label="RAG Cache Hit"
                value={`${(aiMetrics.rag_stats.cache_hit_rate * 100).toFixed(0)}%`}
                sub={`${aiMetrics.rag_stats.avg_retrieval_latency_ms}ms retrieval`}
                status="neutral"
              />
              <MetricCard
                icon={<Activity className="w-4 h-4" />}
                label="Voice STT Latency"
                value={`${aiMetrics.voice_stats.avg_stt_latency_ms}ms`}
                sub={`${aiMetrics.voice_stats.transcriptions_today} transcriptions today`}
                status="good"
              />
              <MetricCard
                icon={<Brain className="w-4 h-4" />}
                label="Tutor Agent Calls"
                value={aiMetrics.agent_stats.tutor_agent_calls}
                sub="Multi-agent orchestration"
                status="neutral"
              />
              <MetricCard
                icon={<CheckCircle className="w-4 h-4" />}
                label="Provider Split"
                value="75/25"
                sub="Anthropic / OpenAI"
                status="neutral"
              />
            </div>
          </div>
        )}

        {/* Platform Stats */}
        {platformStats && (
          <div>
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Users className="w-5 h-5" />
              Platform Statistics
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <MetricCard
                icon={<Users className="w-4 h-4" />}
                label="Total Users"
                value={platformStats.platform_stats.total_users.toLocaleString()}
                status="good"
              />
              <MetricCard
                icon={<Activity className="w-4 h-4" />}
                label="Daily Active Users"
                value={platformStats.platform_stats.daily_active_users}
                sub={`${Math.round(platformStats.platform_stats.daily_active_users / platformStats.platform_stats.total_users * 100)}% DAU rate`}
                status="good"
              />
              <MetricCard
                icon={<Globe className="w-4 h-4" />}
                label="Top City"
                value={platformStats.platform_stats.top_city}
                sub={`from ${platformStats.platform_stats.top_country}`}
                status="neutral"
              />
            </div>

            <div className="glass-card p-6 mt-4">
              <h3 className="font-semibold mb-4">Level Distribution</h3>
              <ResponsiveContainer width="100%" height={160}>
                <BarChart
                  data={Object.entries(platformStats.level_distribution).map(([level, pct]) => ({
                    level,
                    users: pct,
                  }))}
                >
                  <XAxis dataKey="level" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 10 }} unit="%" />
                  <Tooltip formatter={(v) => `${v}%`} />
                  <Bar dataKey="users" fill="#a855f7" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
