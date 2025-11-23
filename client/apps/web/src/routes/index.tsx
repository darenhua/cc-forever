import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import {
	Activity,
	CheckCircle,
	Clock,
	Code,
	Users,
	Zap,
	Calendar,
	BarChart3,
	ArrowRight,
	AlertCircle,
	Loader2,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { statsApi, ideasApi, agentApi } from "@/lib/api";
import type { Idea } from "@/lib/api";

export const Route = createFileRoute("/")({
	component: HomeComponent,
});

// Fallback data for when API is unavailable
const FALLBACK_STATS = {
	usage: {
		session: 0,
		weekly: 0,
		projected: 0
	},
};

function ProgressBar({ value, color = "bg-uchu-green", label, subLabel }: { value: number; color?: string; label: string; subLabel?: string }) {
	return (
		<div className="space-y-2">
			<div className="flex justify-between text-sm font-bold text-uchu-dark-gray dark:text-uchu-light-gray">
				<span>{label}</span>
				<span>{value}%</span>
			</div>
			<div className="h-4 w-full bg-uchu-light-gray dark:bg-uchu-dark-gray rounded-full overflow-hidden border-b-2 border-uchu-gray dark:border-uchu-dark-gray">
				<div
					className={`h-full ${color} transition-all duration-500 ease-out`}
					style={{ width: `${value}%` }}
				/>
			</div>
			{subLabel && <p className="text-xs text-uchu-gray font-medium">{subLabel}</p>}
		</div>
	);
}

function HomeComponent() {
	// Fetch stats from API
	const { data: stats, isLoading: statsLoading, error: statsError } = useQuery({
		queryKey: ["stats"],
		queryFn: statsApi.getStats,
	});

	// Fetch ideas from API
	const { data: ideas, isLoading: ideasLoading } = useQuery({
		queryKey: ["ideas"],
		queryFn: ideasApi.list,
	});

	// Fetch agent status (poll more frequently to see live updates)
	const { data: agentStatus } = useQuery({
		queryKey: ["agentStatus"],
		queryFn: agentApi.getStatus,
	});

	// Derive values from API data
	const usage = stats?.usage_stats ?? FALLBACK_STATS.usage;
	const isWorking = agentStatus?.is_running ?? false;
	const currentTask = agentStatus?.current_prompt ?? "No active task";
	const pendingIdeas = ideas?.filter((idea: Idea) => idea.state === "NotStarted") ?? [];
	const completedIdeas = ideas?.filter((idea: Idea) => idea.state === "Completed") ?? [];
	const nextIdea = pendingIdeas[0];

	// Loading state
	if (statsLoading || ideasLoading) {
		return (
			<div className="max-w-5xl mx-auto p-6 min-h-screen bg-uchu-light-gray dark:bg-uchu-yin font-sans flex items-center justify-center">
				<div className="flex flex-col items-center gap-4">
					<Loader2 className="w-12 h-12 text-uchu-blue animate-spin" />
					<p className="text-uchu-dark-gray dark:text-uchu-light-gray font-bold">Loading stats...</p>
				</div>
			</div>
		);
	}

	// Error state
	if (statsError) {
		return (
			<div className="max-w-5xl mx-auto p-6 min-h-screen bg-uchu-light-gray dark:bg-uchu-yin font-sans flex items-center justify-center">
				<div className="flex flex-col items-center gap-4 text-center">
					<AlertCircle className="w-12 h-12 text-uchu-red" />
					<p className="text-uchu-dark-gray dark:text-uchu-light-gray font-bold">Failed to load stats</p>
					<p className="text-uchu-gray text-sm">{statsError.message}</p>
				</div>
			</div>
		);
	}

	return (
		<div className="max-w-5xl mx-auto p-6 min-h-screen bg-uchu-light-gray dark:bg-uchu-yin font-sans selection:bg-uchu-light-green selection:text-uchu-dark-green">
			{/* Header */}
			<header className="mb-8 text-center md:text-left">
				<h1 className="text-4xl font-extrabold text-uchu-yin dark:text-uchu-yang tracking-tight mb-2">
					HardestWorkingGameDev
				</h1>
				<p className="text-xl text-uchu-dark-gray dark:text-uchu-gray font-medium">
					Hi Daren! I'm still working on my projects. Come back in a few minutes!
				</p>
			</header>

			{/* Analytics Dashboard */}
			<Card className="border-2 border-uchu-gray border-b-4 border-b-uchu-dark-gray dark:border-uchu-dark-gray dark:border-b-uchu-gray rounded-3xl shadow-sm overflow-hidden bg-uchu-yang dark:bg-uchu-yin mb-8">
				<CardHeader className="border-b border-uchu-light-gray dark:border-uchu-dark-gray bg-uchu-light-gray/50 dark:bg-uchu-dark-gray/30 pb-4">
					<div className="flex items-center gap-3">
						<div className="bg-uchu-light-blue dark:bg-uchu-dark-blue/30 p-2 rounded-xl">
							<Activity className="w-6 h-6 text-uchu-blue dark:text-uchu-light-blue" />
						</div>
						<CardTitle className="text-xl font-bold text-uchu-dark-gray dark:text-uchu-light-gray">Analytics</CardTitle>
					</div>
				</CardHeader>

				<CardContent className="p-6 md:p-8 grid gap-8">

					{/* Top Status Row */}
					<div className="grid md:grid-cols-2 gap-6">
						{/* Working Status */}
						<div className={`
              p-6 rounded-2xl border-2 border-b-4 flex items-center gap-4
              ${isWorking
								? 'bg-uchu-light-green border-uchu-green border-b-uchu-dark-green text-uchu-dark-green dark:bg-uchu-dark-green/20 dark:border-uchu-dark-green dark:border-b-uchu-green dark:text-uchu-light-green'
								: 'bg-uchu-light-red border-uchu-red border-b-uchu-dark-red text-uchu-dark-red dark:bg-uchu-dark-red/20 dark:border-uchu-dark-red dark:border-b-uchu-red dark:text-uchu-light-red'}
            `}>
							<div className={`p-3 rounded-xl ${isWorking ? 'bg-uchu-green/20 dark:bg-uchu-green/30' : 'bg-uchu-red/20 dark:bg-uchu-red/30'}`}>
								<Zap className={`w-8 h-8 ${isWorking ? 'text-uchu-green fill-uchu-green dark:text-uchu-light-green dark:fill-uchu-light-green' : 'text-uchu-red dark:text-uchu-light-red'}`} />
							</div>
							<div>
								<div className="text-sm font-bold uppercase opacity-70 mb-1">Status</div>
								<div className="text-xl font-extrabold">
									{isWorking ? "CLAUDE IS COOKING" : "TAKING A BREAK"}
								</div>
							</div>
						</div>

						{/* Current Task */}
						<div className="p-6 rounded-2xl border-2 border-b-4 border-uchu-gray border-b-uchu-dark-gray dark:border-uchu-dark-gray dark:border-b-uchu-gray bg-uchu-light-gray dark:bg-uchu-dark-gray/30 flex flex-col justify-center">
							<div className="flex items-center gap-2 mb-2 text-uchu-blue dark:text-uchu-light-blue font-bold text-sm uppercase tracking-wider">
								<Clock className="w-4 h-4" />
								Current Task
							</div>
							<div className="font-bold text-lg text-uchu-dark-gray dark:text-uchu-light-gray leading-tight">
								"{currentTask}"
							</div>
						</div>
					</div>

					{/* Conversation Log */}
					{isWorking && agentStatus && agentStatus.conversation_log.length > 0 && (
						<div className="p-6 rounded-2xl border-2 border-b-4 border-uchu-gray border-b-uchu-dark-gray dark:border-uchu-dark-gray dark:border-b-uchu-gray bg-uchu-light-gray dark:bg-uchu-dark-gray/30">
							<div className="flex items-center justify-between mb-4">
								<div className="flex items-center gap-2 text-uchu-blue dark:text-uchu-light-blue font-bold text-sm uppercase tracking-wider">
									<Activity className="w-4 h-4" />
									Live Activity
								</div>
								<span className="text-xs font-bold text-uchu-gray bg-uchu-yang dark:bg-uchu-yin px-2 py-1 rounded-full">
									{agentStatus.message_count} messages
								</span>
							</div>
							<div className="space-y-2 max-h-48 overflow-y-auto">
								{agentStatus.conversation_log.slice(-5).map((msg, i) => (
									<div key={i} className="text-sm p-3 rounded-xl bg-uchu-yang dark:bg-uchu-yin border border-uchu-light-gray dark:border-uchu-dark-gray">
										<div className="flex items-center gap-2 mb-1">
											<span className="text-xs font-bold text-uchu-purple dark:text-uchu-light-purple">
												{msg.type}
											</span>
											<span className="text-xs text-uchu-gray">
												{new Date(msg.timestamp).toLocaleTimeString()}
											</span>
										</div>
										<p className="text-uchu-dark-gray dark:text-uchu-light-gray font-medium truncate">
											{msg.content.slice(0, 150)}{msg.content.length > 150 ? '...' : ''}
										</p>
									</div>
								))}
							</div>
						</div>
					)}

					{/* Stats Grid */}
					<div className="grid md:grid-cols-3 gap-8">
						{/* Usage Stats */}
						<div className="md:col-span-2 space-y-6">
							<h3 className="font-bold text-uchu-dark-gray dark:text-uchu-light-gray text-lg flex items-center gap-2">
								<BarChart3 className="w-5 h-5 text-uchu-gray" />
								Usage Statistics
							</h3>
							<div className="grid gap-5">
								<ProgressBar
									label="Active 5-Hour Session"
									value={usage.session}
									color="bg-uchu-orange"
									subLabel="Keep that streak alive!"
								/>
								<ProgressBar
									label="Weekly Usage"
									value={usage.weekly}
									color="bg-uchu-blue"
								/>
							</div>
						</div>

						{/* Worker & Projects Summary */}
						<div className="space-y-4">
							<div className="p-5 rounded-2xl border-2 border-uchu-light-gray dark:border-uchu-dark-gray bg-uchu-light-gray/50 dark:bg-uchu-dark-gray/20 flex flex-col items-center text-center">
								<Users className="w-8 h-8 text-uchu-purple mb-2" />
								<div className="text-3xl font-black text-uchu-yin dark:text-uchu-yang">1</div>
								<div className="text-sm font-bold text-uchu-gray dark:text-uchu-light-gray">Active Workers</div>
							</div>

							<div className="p-5 rounded-2xl border-2 border-uchu-light-gray dark:border-uchu-dark-gray bg-uchu-light-gray/50 dark:bg-uchu-dark-gray/20 flex flex-col items-center text-center">
								<CheckCircle className="w-8 h-8 text-uchu-green mb-2" />
								<div className="text-3xl font-black text-uchu-yin dark:text-uchu-yang">{completedIdeas.length}</div>
								<div className="text-sm font-bold text-uchu-gray dark:text-uchu-light-gray">Projects Done</div>
							</div>
						</div>
					</div>

					{/* Projects & Next Up */}
					<div className="grid md:grid-cols-2 gap-8 pt-4 border-t border-uchu-light-gray dark:border-uchu-dark-gray">
						{/* Recent Projects Link */}
						<div>
							<h3 className="font-bold text-uchu-dark-gray dark:text-uchu-light-gray text-lg mb-4 flex items-center gap-2">
								<Code className="w-5 h-5 text-uchu-gray" />
								Recent Projects
							</h3>

							<div className="space-y-3">
								{completedIdeas.slice(0, 3).map((idea: Idea) => (
									<Link
										key={idea.id}
										to="/projects/$projectId"
										params={{ projectId: idea.id.toString() }}
										className="block w-full text-left group p-4 rounded-2xl border-2 border-uchu-gray border-b-4 hover:bg-uchu-light-blue hover:border-uchu-blue hover:border-b-uchu-dark-blue dark:border-uchu-dark-gray dark:border-b-uchu-gray dark:hover:bg-uchu-dark-blue/20 dark:hover:border-uchu-dark-blue dark:hover:border-b-uchu-blue transition-all active:border-b-2 active:translate-y-[2px]"
									>
										<div className="flex justify-between items-center">
											<span className="font-bold text-uchu-dark-gray dark:text-uchu-light-gray group-hover:text-uchu-blue dark:group-hover:text-uchu-light-blue truncate">{idea.prompt}</span>
											<ArrowRight className="w-4 h-4 text-uchu-gray group-hover:text-uchu-blue dark:group-hover:text-uchu-light-blue flex-shrink-0" />
										</div>
									</Link>
								))}
								{completedIdeas.length === 0 && (
									<p className="text-uchu-gray text-sm">No completed projects yet</p>
								)}
							</div>
						</div>

						{/* Next Up */}
						<div>
							<h3 className="font-bold text-uchu-dark-gray dark:text-uchu-light-gray text-lg mb-4 flex items-center gap-2">
								<Calendar className="w-5 h-5 text-uchu-gray" />
								Coming Up Next
							</h3>
							<div className="p-5 rounded-2xl border-2 border-uchu-light-purple dark:border-uchu-dark-purple/50 bg-uchu-light-purple/30 dark:bg-uchu-dark-purple/20">
								<div className="text-uchu-purple dark:text-uchu-light-purple font-bold text-sm uppercase tracking-wide mb-2">Next Task</div>
								<div className="font-bold text-uchu-yin dark:text-uchu-yang text-lg">
									"{nextIdea?.prompt ?? "No tasks in queue"}"
								</div>
							</div>
						</div>
					</div>

				</CardContent>
			</Card>

			{/* Queue Section */}
			<div className="space-y-4">
				<div className="flex items-center justify-between px-2">
					<h2 className="text-xl font-bold text-uchu-dark-gray dark:text-uchu-light-gray">Project Queue</h2>
					<span className="text-sm font-bold text-uchu-gray bg-uchu-light-gray dark:bg-uchu-dark-gray px-3 py-1 rounded-full">{pendingIdeas.length} Pending</span>
				</div>

				<div className="bg-uchu-yang dark:bg-uchu-yin p-2 rounded-3xl border-2 border-uchu-gray border-b-4 border-b-uchu-dark-gray dark:border-uchu-dark-gray dark:border-b-uchu-gray">
					<div className="flex gap-3 overflow-x-auto pb-4 pt-2 px-2 snap-x">
						{pendingIdeas.map((idea: Idea, i: number) => (
							<div key={idea.id} className="snap-center shrink-0 w-64 p-5 rounded-2xl bg-uchu-light-yellow dark:bg-uchu-dark-yellow/20 border-2 border-uchu-light-yellow dark:border-uchu-dark-yellow/50 flex flex-col gap-3">
								<div className="w-8 h-8 rounded-full bg-uchu-yellow dark:bg-uchu-dark-yellow flex items-center justify-center text-uchu-dark-yellow dark:text-uchu-light-yellow font-bold text-sm">
									{i + 1}
								</div>
								<p className="font-bold text-uchu-dark-gray dark:text-uchu-light-gray leading-tight">
									{idea.prompt}
								</p>
							</div>
						))}
						<div className="snap-center shrink-0 w-64 p-5 rounded-2xl bg-uchu-light-gray dark:bg-uchu-dark-gray/30 border-2 border-dashed border-uchu-gray dark:border-uchu-dark-gray flex flex-col items-center justify-center gap-2 text-uchu-gray dark:text-uchu-light-gray hover:bg-uchu-gray/10 dark:hover:bg-uchu-dark-gray hover:text-uchu-dark-gray dark:hover:text-uchu-gray transition-colors cursor-pointer">
							<div className="w-10 h-10 rounded-full bg-uchu-gray/20 dark:bg-uchu-dark-gray flex items-center justify-center">
								<span className="text-2xl font-bold">+</span>
							</div>
							<span className="font-bold text-sm">Add to Queue</span>
						</div>
					</div>
				</div>
			</div>

		</div>
	);
}
