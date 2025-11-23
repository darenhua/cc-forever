import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import Markdown from 'react-markdown'

// Type definitions for conversation messages
interface TextBlock {
    text: string;
}

interface ToolUseBlock {
    id: string;
    name: string;
    input: Record<string, unknown>;
}

interface ToolResultBlock {
    tool_use_id: string;
    content: string;
    is_error: boolean | null;
}

interface AssistantMessage {
    type: 'assistant';
    content: (TextBlock | ToolUseBlock)[];
    model: string;
}

interface UserMessage {
    type: 'user';
    content: (ToolResultBlock | { text: string })[];
}

interface ResultMessage {
    type: 'result';
    subtype: string;
    duration_ms: number;
    total_cost_usd: number;
    result: string;
}

type ConversationMessage = AssistantMessage | UserMessage | ResultMessage;

// Sample data based on the provided example
const sampleMessages: ConversationMessage[] = [
    {
        type: 'assistant',
        content: [{
            id: 'toolu_01TWibWBDoUY6Xh9wgp2Ekgm',
            name: 'StructuredOutput',
            input: {
                summary: 'I created a complete registration page website with HTML, CSS, and JavaScript. The page features:\n\n**HTML Structure:**\n- A modern registration form with fields for full name, email, phone number, password, and password confirmation\n- Terms and conditions checkbox\n- Success modal that appears after successful registration\n\n**CSS Styling:**\n- Beautiful purple gradient background\n- Clean white card design with rounded corners and shadow\n- Responsive layout that works on mobile devices\n- Custom styled form inputs with focus and validation states (error/success)\n- Password strength indicator bar\n- Loading spinner animation for the submit button\n- Smooth animations for the success modal\n\n**JavaScript Functionality:**\n- Real-time form validation on blur for all fields\n- Email format validation using regex\n- Phone number validation (optional field)\n- Password strength checker that shows Weak/Medium/Strong\n- Password visibility toggle\n- Confirm password matching validation\n- Loading state simulation (2 seconds) on form submission\n- Success modal with multiple close options (button, click outside, Escape key)\n- Form reset after successful submission\n\nThe registration page is fully functional and provides a great user experience with visual feedback for all interactions.',
                entry_point: './projects/2/index.html'
            }
        }],
        model: 'claude-sonnet-4-5-20250929'
    },
    {
        type: 'user',
        content: [{
            tool_use_id: 'toolu_01TWibWBDoUY6Xh9wgp2Ekgm',
            content: 'Structured output provided successfully',
            is_error: null
        }]
    },
    {
        type: 'assistant',
        content: [{
            text: "I've created a complete registration page website for you! Here's what I built:\n\n## Summary\n\n**HTML Structure:**\n- Registration form with fields for full name, email, phone, password, and confirm password\n- Terms and conditions checkbox\n- Success modal popup\n\n**CSS Styling:**\n- Modern purple gradient background\n- Clean white card with shadows and rounded corners\n- Responsive design for mobile devices\n- Visual feedback for form validation (green for success, red for errors)\n- Password strength indicator bar\n- Loading spinner animation\n- Smooth modal animations\n\n**JavaScript Features:**\n- Real-time validation on each field\n- Email format validation\n- Password strength meter (Weak/Medium/Strong)\n- Password visibility toggle\n- Passwords match checking\n- 2-second loading simulation on submit\n- Success modal with multiple close options\n- Form reset after successful registration\n\nThe page is fully functional and provides a polished user experience with instant feedback on all interactions!"
        }],
        model: 'claude-sonnet-4-5-20250929'
    },
    {
        type: 'result',
        subtype: 'success',
        duration_ms: 120225,
        total_cost_usd: 0.24706390000000003,
        result: "I've created a complete registration page website for you!"
    }
];

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
                        return (
                            <div key={idx} className="space-y-1">
                                <div className="flex items-center gap-2">
                                    <span className="text-xs text-muted-foreground">Tool Result:</span>
                                    <span className="text-xs font-mono text-muted-foreground">
                                        {block.tool_use_id.slice(0, 12)}...
                                    </span>
                                </div>
                                <div className="text-sm text-black">{block.content}</div>
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
function ClaudeCodeLogs() {
    return (
        <div className="h-full flex flex-col">
            <div className="flex-1 max-w-[800px] overflow-y-scroll space-y-4 p-2 mx-auto w-full">
                {sampleMessages.map((message, idx) => {
                    switch (message.type) {
                        case 'assistant':
                            return <AssistantMessageComponent key={idx} message={message} />;
                        case 'user':
                            return <UserMessageComponent key={idx} message={message} />;
                        case 'result':
                            return <ResultMessageComponent key={idx} message={message} />;
                        default:
                            return null;
                    }
                })}
            </div>
            <div className="mx-4 mb-4 mt-2 bg-white border border-gray-200 rounded-lg p-3 shadow-sm">
                <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-gray-500">Current Task:</span>
                    <span className="text-sm text-gray-700">Making a html page</span>
                </div>
            </div>
        </div>
    );
}

export default function AgentLogs() {
    return (
        <div className="flex-1 flex flex-col min-h-0">
            <Tabs defaultValue="tab1" className="flex-1 flex flex-col min-h-0">
                <TabsList className="self-start">
                    <TabsTrigger value="tab1">Daren's Claude Code</TabsTrigger>
                </TabsList>
                <TabsContent value="tab1" className="flex-1 min-h-0 bg-gray-100 rounded-lg p-2 overflow-hidden">
                    <ClaudeCodeLogs />
                </TabsContent>
            </Tabs>
        </div>
    )
}