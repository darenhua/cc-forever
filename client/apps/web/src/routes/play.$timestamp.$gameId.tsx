import { createFileRoute } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'
import { Loader2 } from 'lucide-react'

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8001"

export const Route = createFileRoute('/play/$timestamp/$gameId')({
    component: PlayGame,
})

function PlayGame() {
    const { timestamp, gameId } = Route.useParams()
    const gameIdNumber = Number(gameId)

    const { data: entryPoint, isPending } = useQuery({
        queryKey: ['entry-point', timestamp, gameIdNumber],
        queryFn: () => fetch(`${API_BASE_URL}/get-entry-point/${timestamp}/${gameIdNumber}`).then(res => res.json()),
    })

    const iframeSrc = entryPoint?.path
        ? `${API_BASE_URL}${entryPoint.path}`
        : null

    return (
        <div className="flex flex-col items-center p-6">
            <div className="flex flex-row items-center justify-center">
                <img
                    src={`${API_BASE_URL}/cartridge_arts/${timestamp}/${gameIdNumber}/banner_art.png_0`}
                    className="w-52 h-[800px] shrink-0 object-cover"
                />
                <div className="relative">
                    {isPending ? (
                        <div className="absolute inset-0 flex items-center justify-center">
                            <Loader2 className="w-8 h-8 animate-spin" />
                        </div>
                    ) : iframeSrc ? (
                        <iframe
                            src={iframeSrc}
                            className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[700px]"
                        />
                    ) : (
                        <div className="absolute inset-0 flex items-center justify-center text-red-500">
                            No game found
                        </div>
                    )}
                    <img
                        src={`${API_BASE_URL}/assets/border.png`}
                        className="bg-black w-[1000px] h-[800px]"
                    />
                </div>
                <img
                    src={`${API_BASE_URL}/cartridge_arts/${timestamp}/${gameIdNumber}/banner_art.png_0`}
                    className="w-52 h-[800px] shrink-0 object-cover"
                />
            </div>
        </div>
    )
}
