import { createFileRoute, Link } from "@tanstack/react-router";
import AgentLogs from "@/components/agent-logs";
import AgentsSheet from "@/components/agents-sheet";
import NextQueue from "@/components/next-queue";
import { Button } from "@/components/ui/button";
import { useQuery } from "@tanstack/react-query";
import { Loader2 } from "lucide-react";
import { useSheetState } from "@/components/sheet-provider";

export const Route = createFileRoute("/second")({
	component: Page,
});
// Type definitions for conversation messages
export interface TextBlock {
	text: string;
}

export interface ToolUseBlock {
	id: string;
	name: string;
	input: Record<string, unknown>;
}

export interface ToolResultBlock {
	tool_use_id: string;
	content: string;
	is_error: boolean | null;
}

export interface AssistantMessage {
	content: (TextBlock | ToolUseBlock)[];
	model: string;
	parent_tool_use_id: string | null;
	error: string | null;
}

export interface UserMessage {
	content: (ToolResultBlock | TextBlock)[];
	parent_tool_use_id: string | null;
}

export interface ResultMessage {
	type: 'result';
	subtype: string;
	duration_ms: number;
	total_cost_usd: number;
	result: string;
}

export interface SystemMessage {
	subtype: string;
	data: Record<string, unknown>;
}

export type ConversationMessage = AssistantMessage | UserMessage | ResultMessage | SystemMessage;

type ConversationLogEntry = {
	timestamp: string;
	type: 'AssistantMessage' | 'UserMessage' | 'SystemMessage' | 'ResultMessage';
	content: ConversationMessage;
};

// Type guards for content blocks
export function isToolUseBlock(block: TextBlock | ToolUseBlock | ToolResultBlock): block is ToolUseBlock {
	return 'id' in block && 'name' in block;
}

export function isTextBlock(block: TextBlock | ToolUseBlock | ToolResultBlock): block is TextBlock {
	return 'text' in block && !('tool_use_id' in block);
}

export function isToolResultBlock(block: TextBlock | ToolUseBlock | ToolResultBlock): block is ToolResultBlock {
	return 'tool_use_id' in block;
}

type Idea = {
	id: number;
	prompt: string;
	repos: string[];
	state: string;
	created_at: string;
};

export type AgentStatus = {
	is_online: boolean;
	is_running: boolean;
	current_job_id: number | null;
	current_prompt: string | null;
	started_at: string | null;
	message_count: number;
	conversation_log: ConversationLogEntry[];
	ideas_queue: Idea[];
	num_completed_ideas: number;
};


function Page() {
	const { setIsOpen } = useSheetState();

	const { data: status, isPending } = useQuery<AgentStatus>({
		queryKey: ['agentStatus'],
		queryFn: async () => {
			const response = await fetch('http://localhost:8000/agent/status');
			if (!response.ok) {
				throw new Error('Failed to fetch status');
			}
			return response.json();
		},
		refetchInterval: 5000,
	});

	if (isPending) {
		return (
			<div className="flex flex-col h-[90vh] w-full max-w-[1000px] mx-auto">
				<div className="flex-1 min-h-0 w-full flex p-12 pb-6 items-center justify-center">
					<Loader2 className="w-12 h-12 text-uchu-blue animate-spin" />
				</div>
			</div>
		);
	}

	return (
		<div className="flex flex-col h-[90vh] w-full max-w-[1000px] mx-auto">
			<div className="flex-1 min-h-0 w-full flex p-12 pb-6">
				<AgentLogs status={status} />
			</div>
			<div className="flex justify-between items-center px-6">
				<NextQueue status={status} />
				<div className="flex gap-3">
					<Button size='lg' onClick={() => setIsOpen(true)} variant="secondary">Workers</Button>
					<Link to="/third">
						<Button size='lg' className="hover:bg-uchu-green/80 bg-uchu-green shiny-button">
							See <span className="text-uchu-black font-bold">{status?.num_completed_ideas ?? "-"}</span> Finished Projects
						</Button>
					</Link>
				</div>

			</div>

			<AgentsSheet />
		</div>
	)
}