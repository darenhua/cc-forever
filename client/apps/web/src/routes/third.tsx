import type { Idea } from '@/lib/api'
import { useQuery } from '@tanstack/react-query'
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/third')({
    component: RouteComponent,
})

function RouteComponent() {
    const { data: ideas } = useQuery<Idea[]>({
        queryKey: ['finished'],
        queryFn: () => fetch('http://localhost:8000/finished-projects').then(res => res.json()),
    })
    console.log(ideas)
    if (!ideas) {
        return <div>Loading...</div>
    }
    return (
        <div>
            <div className="flex justify-between  px-6">
                <h1 className="text-2xl text-uchu-green mt-6 ml-auto font-bold">Finished Projects ({ideas.length})</h1>
            </div>
            <div className="flex flex-col gap-4">
                {ideas.map((idea) => (
                    <div key={idea.id}>
                        <div className="my-6">
                            <iframe
                                src={`http://localhost:8000/projects/${idea.id}/index.html`}
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
                        </div>
                        <h2 className="text-xl font-bold">#{idea.id}: {idea.prompt}</h2>
                        <p className="text-sm text-gray-500">{idea.created_at}</p>
                    </div>
                ))}
            </div>
        </div>
    )
}
