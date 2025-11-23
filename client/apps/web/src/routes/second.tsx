import { createFileRoute, Link } from "@tanstack/react-router";
import AgentLogs from "@/components/agent-logs";
import AgentsSheet from "@/components/agents-sheet";
import NextQueue from "@/components/next-queue";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/second")({
	component: Page,
});

function Page() {
	return (
		<div className="flex flex-col h-[90vh] w-full max-w-[1000px] mx-auto">
			<div className="flex-1 min-h-0 w-full flex p-12 pb-6">
				<AgentLogs />
			</div>
			<div className="flex justify-between items-center px-6">
				<NextQueue />
				<Link to="/">
					<Button size='lg' className="hover:bg-uchu-green/80 bg-uchu-green ">
						3 Finished Projects
					</Button>
				</Link>
			</div>

			<AgentsSheet />
		</div>
	)
}