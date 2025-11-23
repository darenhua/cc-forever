// API client with OpenAPI-compatible types

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Types matching the FastAPI backend models
export interface UsageStats {
    session: number; // 0-100
    weekly: number; // 0-100
}

export interface WorkSession {
    start_time: string | null;
    end_time: string | null;
    idea_id: number | null;
    duration_seconds: number;
}

export interface StatsResponse {
    usage_stats: UsageStats;
    work_session: WorkSession;
}

export interface Idea {
    id: number;
    prompt: string;
    repos: string[];
    state: string;
}

export interface QueueStatusResponse {
    is_full: boolean;
    size: number;
    max_size: number;
}

export interface ConversationMessage {
    timestamp: string;
    type: string;
    content: string;
}

export interface AgentStatus {
    is_online: boolean;
    is_running: boolean;
    current_job_id: string | null;
    current_prompt: string | null;
    started_at: string | null;
    message_count: number;
    conversation_log: ConversationMessage[];
}

export interface AgentControlResponse {
    status: string;
    message: string;
}

// API error class
export class ApiError extends Error {
    constructor(public status: number, message: string) {
        super(message);
        this.name = "ApiError";
    }
}

// Generic fetch wrapper with type safety
async function apiFetch<T>(
    endpoint: string,
    options?: RequestInit
): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
            "Content-Type": "application/json",
            ...options?.headers,
        },
        ...options,
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new ApiError(response.status, errorText || response.statusText);
    }

    return response.json();
}

// Stats API
export const statsApi = {
    getStats: () => apiFetch<StatsResponse>("/stats/"),

    startSession: (ideaId: number) =>
        apiFetch<{ status: string; idea_id: number }>(
            `/stats/session/start?idea_id=${ideaId}`,
            { method: "POST" }
        ),

    endSession: () =>
        apiFetch<{ status: string }>("/stats/session/end", { method: "POST" }),
};

// Ideas API
export const ideasApi = {
    list: () => apiFetch<Idea[]>("/ideas/"),

    get: (id: number) => apiFetch<Idea>(`/ideas/${id}`),

    create: (data: { prompt: string; repos: string[] }) =>
        apiFetch<void>("/ideas/", {
            method: "POST",
            body: JSON.stringify(data),
        }),

    pop: () => apiFetch<Idea>("/ideas/pop"),

    getQueueStatus: () => apiFetch<QueueStatusResponse>("/ideas/status"),
};

// Agent API
export const agentApi = {
    getStatus: () => apiFetch<AgentStatus>("/agent/status"),

    start: () =>
        apiFetch<AgentControlResponse>("/agent/start", { method: "POST" }),

    stop: () =>
        apiFetch<AgentControlResponse>("/agent/stop", { method: "POST" }),
};
