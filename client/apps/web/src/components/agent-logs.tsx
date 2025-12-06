import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import type { AgentStatus, TextBlock, ToolUseBlock, ToolResultBlock, AssistantMessage, UserMessage, ResultMessage, SystemMessage } from "@/routes/second";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import Markdown from 'react-markdown'
import { Button } from "./ui/button";
import { Loader2, Square } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "./ui/dialog";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8001";



// Sample data based on the provided example

function isTextBlock(block: TextBlock | ToolUseBlock): block is TextBlock {
    return 'text' in block;
}

function isToolUseBlock(block: TextBlock | ToolUseBlock): block is ToolUseBlock {
    return 'name' in block && 'input' in block;
}

function isToolResultBlock(block: ToolResultBlock | { text: string }): block is ToolResultBlock {
    return 'tool_use_id' in block;
}

function AssistantMessageComponent({ message }: { message: AssistantMessage }) {
    return (
        <div className="flex flex-col gap-2">
            <div className="flex items-center gap-2">
                <span className="text-xs font-semibold text-uchu-purple bg-uchu-purple/10 px-2 py-0.5 rounded">
                    Assistant
                </span>
                <span className="text-xs text-muted-foreground">{message.model}</span>
            </div>
            <div className="bg-card border border-border rounded-lg p-3 shadow-sm">
                {message.content.map((block, idx) => {
                    if (isTextBlock(block)) {
                        return (
                            <div key={idx} className="text-sm text-muted-foreground whitespace-pre-wrap">
                                <Markdown>{block.text}</Markdown>
                            </div>
                        );
                    }
                    if (isToolUseBlock(block)) {
                        return (
                            <div key={idx} className="space-y-2">
                                <div className="flex items-center gap-2">
                                    <span className="text-xs font-mono bg-muted px-2 py-0.5 rounded text-muted-foreground">
                                        {block.name}
                                    </span>
                                    <span className="text-xs text-muted-foreground font-mono">
                                        {block.id.slice(0, 12)}...
                                    </span>
                                </div>
                                <pre className="text-xs bg-muted p-2 rounded overflow-x-auto text-muted-foreground">
                                    {JSON.stringify(block.input, null, 2)}
                                </pre>
                            </div>
                        );
                    }
                    return null;
                })}
            </div>
        </div>
    );
}

function UserMessageComponent({ message }: { message: UserMessage }) {
    return (
        <div className="flex flex-col gap-2">
            <div className="flex items-center gap-2">
                <span className="text-xs font-semibold text-uchu-blue bg-uchu-blue/10 px-2 py-0.5 rounded">
                    User
                </span>
            </div>
            <div className="bg-uchu-blue/5 border border-uchu-blue/20 rounded-lg p-3 shadow-sm">
                {message.content.map((block, idx) => {
                    if (isToolResultBlock(block)) {
                        // Handle content that can be string, array of objects, or other types
                        let contentDisplay: React.ReactNode;
                        if (typeof block.content === 'string') {
                            contentDisplay = block.content;
                        } else if (Array.isArray(block.content)) {
                            contentDisplay = block.content.map((item, i) => {
                                if (typeof item === 'string') return item;
                                if (item && typeof item === 'object' && 'text' in item) {
                                    return <div key={i}>{item.text}</div>;
                                }
                                return <pre key={i} className="text-xs">{JSON.stringify(item, null, 2)}</pre>;
                            });
                        } else if (block.content && typeof block.content === 'object') {
                            contentDisplay = <pre className="text-xs">{JSON.stringify(block.content, null, 2)}</pre>;
                        } else {
                            contentDisplay = String(block.content ?? '');
                        }

                        return (
                            <div key={idx} className="space-y-1">
                                <div className="flex items-center gap-2">
                                    <span className="text-xs text-muted-foreground">Tool Result:</span>
                                    <span className="text-xs font-mono text-muted-foreground">
                                        {block.tool_use_id.slice(0, 12)}...
                                    </span>
                                </div>
                                <div className="text-sm text-black">{contentDisplay}</div>
                            </div>
                        );
                    }
                    return (
                        <div key={idx} className="text-sm text-black">
                            {block.text}
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

function ResultMessageComponent({ message }: { message: ResultMessage }) {
    const durationSec = (message.duration_ms / 1000).toFixed(1);
    const cost = message.total_cost_usd.toFixed(4);

    return (
        <div className="flex flex-col gap-2">
            <div className="flex items-center gap-2">
                <span className={`text-xs font-semibold px-2 py-0.5 rounded ${message.subtype === 'success'
                    ? 'text-uchu-green bg-uchu-green/10'
                    : 'text-destructive bg-destructive/10'
                    }`}>
                    Result
                </span>
                <span className="text-xs text-muted-foreground">{durationSec}s</span>
                <span className="text-xs text-muted-foreground">${cost}</span>
            </div>
            <div className={`border rounded-lg p-3 shadow-sm ${message.subtype === 'success'
                ? 'bg-uchu-green/5 border-uchu-green/20'
                : 'bg-destructive/5 border-destructive/20'
                }`}>
                <div className="text-sm text-black">{message.result}</div>
            </div>
        </div>
    );
}

function SystemMessageComponent({ message }: { message: SystemMessage }) {
    return (
        <div className="flex flex-col gap-2">
            <div className="flex items-center gap-2">
                <span className="text-xs font-semibold text-gray-500 bg-gray-100 px-2 py-0.5 rounded">
                    System
                </span>
                <span className="text-xs text-muted-foreground">{message.subtype}</span>
            </div>
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 shadow-sm">
                <pre className="text-xs text-muted-foreground overflow-x-auto">
                    {JSON.stringify(message.data, null, 2)}
                </pre>
            </div>
        </div>
    );
}
function ClaudeCodeLogs({ status }: { status: AgentStatus }) {
    const scrollRef = useRef<HTMLDivElement>(null);
    const queryClient = useQueryClient();

    // Auto-scroll to bottom when conversation_log changes
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [status.conversation_log]);

    const mutation = useMutation({
        mutationFn: async () => {
            const response = await fetch(`${API_BASE_URL}/agent/start`, {
                method: 'POST',
            });
            return response.json();
        },
        onSuccess: (data) => {
            console.log(data);
            queryClient.invalidateQueries({ queryKey: ['agentStatus'] });
        },
        onError: (error) => {
            console.error('Failed to start agent:', error);
        }
    });

    if (!status.is_online) {
        return (
            <div className="h-full flex flex-col">
                <div className="flex-1 max-w-[800px] overflow-y-scroll space-y-4 p-2 mx-auto w-full">
                    <div className="flex flex-col items-center justify-center h-full text-center gap-4">
                        <div className="text-sm text-muted-foreground">No messages yet</div>
                        <Button
                            disabled={mutation.isPending}
                            onClick={() => mutation.mutate()}
                            className="bg-uchu-green hover:bg-uchu-green/80"
                        >
                            {mutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Start Agent'}
                        </Button>
                    </div>
                </div>
            </div>
        );
    }
    console.log(status);
    if (status.conversation_log.length === 0) {
        return (
            <div className="h-full flex flex-col">
                <div className="flex-1 max-w-[800px] overflow-y-scroll space-y-4 p-2 mx-auto w-full">
                    <div className="flex flex-col items-center justify-center h-full text-center gap-2">
                        <div className="text-sm text-muted-foreground">No messages yet</div>
                        <div className="text-xs text-muted-foreground">Waiting for agent activity...</div>
                    </div>
                </div>
                <div className="mx-4 mb-4 mt-2 bg-white border border-gray-200 rounded-lg p-3 shadow-sm">
                    <div className="flex items-center gap-2">
                        <span className="text-xs font-semibold text-gray-500">Current Task:</span>
                        <span className="text-sm text-gray-700">{status.current_prompt ?? 'No task yet'}</span>
                    </div>
                </div>

            </div>
        );
    }
    return (
        <div className="h-full flex flex-col">
            <div ref={scrollRef} className="flex-1 max-w-[800px] overflow-y-scroll space-y-4 p-2 mx-auto w-full">
                {status.conversation_log.map((message, idx) => {
                    switch (message.type) {
                        case 'AssistantMessage':
                            return <AssistantMessageComponent key={idx} message={message.content as AssistantMessage} />;
                        case 'UserMessage':
                            return <UserMessageComponent key={idx} message={message.content as UserMessage} />;
                        case 'ResultMessage':
                            return <ResultMessageComponent key={idx} message={message.content as ResultMessage} />;
                        case 'SystemMessage':
                            return <SystemMessageComponent key={idx} message={message.content as SystemMessage} />;
                        default:
                            return null;
                    }
                })}
            </div>
            <div className="mx-4 mb-4 mt-2 bg-white border border-gray-200 rounded-lg p-3 shadow-sm">
                <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-gray-500">Current Task:</span>
                    <span className="text-sm text-gray-700">{status.current_prompt}</span>
                </div>
            </div>
        </div>
    );
}

export default function AgentLogs({ status }: { status: AgentStatus }) {
    const [showStopDialog, setShowStopDialog] = useState(false);
    const [coverArtLoaded, setCoverArtLoaded] = useState(false);
    const [coverArtKey, setCoverArtKey] = useState(0);

    // Reset loading state when job changes
    useEffect(() => {
        setCoverArtLoaded(false);
        setCoverArtKey(prev => prev + 1);
    }, [status.current_job_id]);

    // Retry loading cover art every 3 seconds until it loads
    useEffect(() => {
        if (coverArtLoaded || !status.is_running) return;
        const interval = setInterval(() => {
            setCoverArtKey(prev => prev + 1);
        }, 3000);
        return () => clearInterval(interval);
    }, [coverArtLoaded, status.is_running]);

    const stopMutation = useMutation({
        mutationFn: async () => {
            const response = await fetch(`${API_BASE_URL}/agent/stop`, {
                method: 'POST',
            });
            return response.json();
        },
        onSuccess: (data) => {
            console.log('Agent stopped:', data);
            setShowStopDialog(false);
        },
        onError: (error) => {
            console.error('Failed to stop agent:', error);
        }
    });

    return (

        <div className="flex-1 relative flex flex-col min-h-0">
            {status.is_running && status.session_timestamp && status.current_job_id && (
                <div className="w-32 h-32 absolute top-3 right-3 translate-x-1/2 shadow-sm cursor-pointer rounded bg-gray-600 overflow-hidden">
                    {/* Hidden img to detect when cover art loads */}
                    <img
                        key={coverArtKey}
                        src={`${API_BASE_URL}/cartridge_arts/${status.session_timestamp}/${status.current_job_id}/cover_art.png_0`}
                        className="hidden"
                        onLoad={() => setCoverArtLoaded(true)}
                        onError={() => { }}
                    />
                    {coverArtLoaded ? (
                        <div
                            className="absolute inset-0 bg-cover bg-center"
                            style={{
                                backgroundImage: `url(${API_BASE_URL}/cartridge_arts/${status.session_timestamp}/${status.current_job_id}/cover_art.png_0)`,
                                backgroundSize: '150% 120%',
                            }}
                        />
                    ) : (
                        <div className="absolute inset-0 flex items-center justify-center">
                            <Loader2 className="w-6 h-6 text-gray-400 animate-spin" />
                        </div>
                    )}
                    <div className="absolute bottom-0 left-0 right-0 bg-black/70 py-1 px-2">
                        <p className="text-xs text-gray-200">Making Game #{status.current_job_id}</p>
                    </div>
                </div>
            )}
            <Tabs defaultValue="tab1" className="flex-1 flex flex-col min-h-0">
                <div className="flex items-center gap-2">
                    <TabsList className="self-start">
                        <TabsTrigger value="tab1">Daren's Claude Code</TabsTrigger>
                    </TabsList>
                    <Button
                        variant="destructive"
                        size="sm"
                        disabled={stopMutation.isPending || !status.is_running}
                        onClick={() => setShowStopDialog(true)}
                    >
                        {stopMutation.isPending ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                            <Square className="w-4 h-4" />
                        )}
                        <span className="ml-1">Stop</span>
                    </Button>
                </div>
                <TabsContent value="tab1" className="flex-1 min-h-0 bg-gray-100 rounded-lg p-2 overflow-hidden">
                    <ClaudeCodeLogs status={status} />
                </TabsContent>
            </Tabs>

            <Dialog open={showStopDialog} onOpenChange={setShowStopDialog}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Stop Agent</DialogTitle>
                        <DialogDescription>
                            Are you sure you want to stop the agent? This will terminate the current task.
                        </DialogDescription>
                    </DialogHeader>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setShowStopDialog(false)}>
                            Cancel
                        </Button>
                        <Button
                            variant="destructive"
                            onClick={() => stopMutation.mutate()}
                            disabled={stopMutation.isPending}
                        >
                            {stopMutation.isPending ? (
                                <Loader2 className="w-4 h-4 animate-spin mr-1" />
                            ) : null}
                            Stop Agent
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    )
}