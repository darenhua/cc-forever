import { useSheetState } from "@/components/sheet-provider";
import { useEffect, useState } from "react";
import {
	Sheet,
	SheetContent,
	SheetHeader,
	SheetTitle,
	SheetDescription,
} from "@/components/ui/sheet";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8001";
import { useQuery } from "@tanstack/react-query";
import { Loader2 } from "lucide-react";

interface StatsResponse {
	usage_stats: {
		session: number;
		weekly: number;
	};
	work_session: {
		start_time: string | null;
		end_time: string | null;
		idea_id: string | null;
		duration_seconds: number;
	};
}

function ProgressBar({ value, label }: { value: number; label: string }) {
	return (
		<div className="space-y-2">
			<div className="flex justify-between text-sm">
				<span className="text-muted-foreground">{label}</span>
				<span className="font-medium">{value}%</span>
			</div>
			<div className="h-2 bg-gray-200 rounded-full overflow-hidden">
				<div
					className="h-full bg-uchu-purple rounded-full transition-all duration-300"
					style={{ width: `${Math.min(value, 100)}%` }}
				/>
			</div>
		</div>
	);
}

export default function AgentsSheet() {
	const { isOpen, setIsOpen } = useSheetState();
	const [session, setSession] = useState(null);

	// Fetch session data when sheet opens
	useEffect(() => {
		if (isOpen) {
			const fetchSession = async () => {
				try {
					const response = await fetch(`${API_BASE_URL}/stats`);
					const data = await response.json();

					if (data.session !== undefined) {
						setSession(data.usage_stats.session);
						// You could also store it elsewhere if needed
						console.log('Session ID:', data.usage_stats.session);
					}
				} catch (error) {
					console.error('Error fetching session:', error);
				}
			};

			fetchSession();
		}
	}, [isOpen]); // This effect runs whenever isOpen changes

	const { data: stats, isLoading, error } = useQuery<StatsResponse>({
		queryKey: ['stats'],
		queryFn: async () => {
			const response = await fetch(`${API_BASE_URL}/stats`);
			if (!response.ok) {
				throw new Error('Failed to fetch stats');
			}
			return response.json();
		},
		refetchInterval: 5000,
	});

	return (
		<Sheet open={isOpen} onOpenChange={setIsOpen}>
			<SheetContent>
				<SheetHeader>
					<SheetTitle>Workers</SheetTitle>
					<SheetDescription>
						Claude Codes that are working on games.
						{session !== null && (
							<div>Current Session: {session}</div>
						)}
					</SheetDescription>
				</SheetHeader>

				<div className="mt-6 space-y-6 px-6">
					{/* Usage Stats Section */}
					<Card>
						<CardHeader>
							<CardTitle className="text-sm">Daren's Claude Code Usage Stats</CardTitle>
						</CardHeader>
						<CardContent className="space-y-4">
							{isLoading ? (
								<div className="flex items-center justify-center py-4">
									<Loader2 className="w-4 h-4 animate-spin" />
								</div>
							) : error ? (
								<div className="text-sm text-destructive">
									Failed to load stats
								</div>
							) : stats ? (
								<>
									<ProgressBar
										value={stats.usage_stats.session}
										label="Session"
									/>
									<ProgressBar
										value={stats.usage_stats.weekly}
										label="Weekly"
									/>
								</>
							) : null}
						</CardContent>
					</Card>

					{/* Workers Section */}
					<Card>
						<CardHeader>
							<CardTitle className="text-sm">Workers</CardTitle>
						</CardHeader>
						<CardContent>
							<div className="flex items-center gap-3">
								<span className="text-sm">Daren's Claude Code</span>
							</div>
						</CardContent>
					</Card>
				</div>
			</SheetContent>
		</Sheet>
	);
}
