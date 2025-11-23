import { Button } from '@/components/ui/button'
import GameSelection from '@/components/game-selection'
import type { Idea } from '@/lib/api'
import { useQuery } from '@tanstack/react-query'
import { createFileRoute } from '@tanstack/react-router'
import { useState } from 'react'
import { Loader2 } from 'lucide-react'

function IframeWithEntryPoint({ projectPath }: { projectPath: string }) {
    // projectPath is in format "timestamp/job_id"
    const parts = projectPath.split('/')
    const timestamp = parts[0]
    const jobId = parts[1] || '1'

    const { data: entryPoint, isPending } = useQuery({
        queryKey: ['entry-point', timestamp, jobId],
        queryFn: () => fetch(`http://localhost:8000/get-entry-point/${timestamp}/${jobId}`).then(res => res.json()),
    })

    if (isPending) {
        return (
            <div className="w-full flex items-center justify-center" style={{ height: '600px' }}>
                <Loader2 className="w-8 h-8 animate-spin" />
            </div>
        )
    }

    const iframeSrc = entryPoint?.path
        ? `http://localhost:8000${entryPoint.path}`
        : null

    if (!iframeSrc) {
        return (
            <div className="w-full flex items-center justify-center text-red-500" style={{ height: '600px' }}>
                No game found
            </div>
        )
    }

    return (
        <iframe
            src={iframeSrc}
            className="w-full border-0"
            style={{ height: '600px' }}
            onLoad={(e) => {
                try {
                    const iframe = e.target as HTMLIFrameElement;
                    const height = iframe.contentWindow?.document.body.scrollHeight;
                    if (height) {
                        iframe.style.height = `${height}px`;
                    }
                } catch {
                    // Cross-origin restriction, keep default height
                }
            }}
        />
    )
}

export const Route = createFileRoute('/third')({
    component: RouteComponent,
})

type ViewState = 'selection' | 'list'

function RouteComponent() {
    const [viewState, setViewState] = useState<ViewState>('selection')

    const { data: ideas } = useQuery<Idea[]>({
        queryKey: ['finished'],
        queryFn: () => fetch('http://localhost:8000/finished-projects').then(res => res.json()),
    })

    if (!ideas) {
        return <div>Loading...</div>
    }

    if (viewState === 'selection') {
        return <GameSelection ideas={ideas} onViewList={() => setViewState('list')} />
    }

    return (
        <div>
            <div className="flex justify-between items-center px-6">
                <Button variant='secondary' onClick={() => setViewState('selection')}>
                    All Game Packs
                </Button>
                <h1 className="text-2xl text-uchu-green mt-6 ml-auto font-bold">Finished Projects ({ideas.length})</h1>
            </div>
            <div className="flex flex-col gap-4">
                {ideas.map((idea) => (
                    <div key={idea.id}>
                        <div className="my-6">
                            <IframeWithEntryPoint
                                projectPath={idea.project_path || String(idea.id)}
                            />
                        </div>
                        <h2 className="text-xl font-bold">#{idea.id}: {idea.prompt}</h2>
                        <p className="text-sm text-gray-500">{idea.created_at}</p>
                    </div>
                ))}
            </div>
        </div>
    )
}
