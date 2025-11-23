import { useSheetState } from "@/components/sheet-provider";
import {
	Sheet,
	SheetContent,
	SheetHeader,
	SheetTitle,
	SheetDescription,
} from "@/components/ui/sheet";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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

	const { data: stats, isLoading, error } = useQuery<StatsResponse>({
		queryKey: ['stats'],
		queryFn: async () => {
			const response = await fetch('http://localhost:8000/stats');
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
					<SheetTitle>Dashboard</SheetTitle>
					<SheetDescription>
						Usage statistics and workers
					</SheetDescription>
				</SheetHeader>

				<div className="mt-6 space-y-6">
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
								<div className="w-2 h-2 bg-uchu-green rounded-full" />
								<span className="text-sm">Daren's Claude Code</span>
							</div>
						</CardContent>
					</Card>
				</div>
			</SheetContent>
		</Sheet>
	);
}
