import type { AgentStatus } from "@/routes/second";
import { useState } from "react";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";

type Idea = {
    id: number;
    prompt: string;
    repos: string[];
    state: string;
    created_at: string;
};

export default function NextQueue({ status }: { status: AgentStatus }) {
    const [selectedIdea, setSelectedIdea] = useState<Idea | null>(null);

    if (!status.is_running) {
        return <div className="flex gap-2 hover:bg-gray-100 dark:bg-gray-800 hover:dark:bg-gray-900 p-2 rounded-lg transition-all duration-200">
            <div className="w-16 h-16   cursor-pointer   border rounded "></div>
            <div className="w-16 h-16 cursor-pointer border rounded "></div>
            <div className="w-16 h-16  cursor-pointer border rounded "></div>
        </div>
    }

    return (
        <>
            <div className="flex gap-2 hover:bg-gray-100 hover:dark:bg-gray-800 p-2 rounded-lg transition-all duration-200">
                {
                    status.ideas_queue.map((idea) => (
                        <div
                            key={idea.id}
                            className="w-16 h-16 cursor-pointer border rounded hover:bg-gray-200 bg-gray-300"
                            onClick={() => setSelectedIdea(idea)}
                        >
                            <p className="text-sm text-gray-500 ml-1">#{idea.id}</p>
                        </div>
                    ))
                }
            </div>

            <Dialog open={selectedIdea !== null} onOpenChange={(open: boolean) => !open && setSelectedIdea(null)}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Idea #{selectedIdea?.id}</DialogTitle>
                    </DialogHeader>
                    <div className="mt-4">
                        <p className="text-sm text-muted-foreground mb-2">Prompt:</p>
                        <p className="text-sm">{selectedIdea?.prompt}</p>
                    </div>
                </DialogContent>
            </Dialog>
        </>
    )
}
