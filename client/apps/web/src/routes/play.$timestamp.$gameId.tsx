import { createFileRoute } from '@tanstack/react-router'

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8001"
const USE_S3 = import.meta.env.VITE_USE_S3 === "true"
const ASSETS_BASE_URL = USE_S3 ? `${API_BASE_URL}/s3` : API_BASE_URL

type PlaySearchParams = {
    path?: string
    banner?: string | null
}

export const Route = createFileRoute('/play/$timestamp/$gameId')({
    component: PlayGame,
    validateSearch: (search: Record<string, unknown>): PlaySearchParams => {
        return {
            path: search.path as string | undefined,
            banner: search.banner as string | null | undefined
        }
    }
})

function PlayGame() {
    const { timestamp, gameId } = Route.useParams()
    const { path, banner } = Route.useSearch()

    // Build iframe src from path - handle both relative paths and full URLs
    const iframeSrc = path
        ? (path.startsWith('http') ? path : `${ASSETS_BASE_URL}/projects/${path.replace(/^\.?\/?(projects\/)?/, '')}`)
        : null

    // Build banner src - use search param if available, fallback to constructed path
    const bannerSrc = banner
        ? `${ASSETS_BASE_URL}${banner}`
        : `${ASSETS_BASE_URL}/cartridge_arts/${timestamp}/${gameId}/banner_art.png_0`

    return (
        <div className="flex flex-col items-center p-6">
            <div className="flex flex-row items-center justify-center">
                <img
                    src={bannerSrc}
                    className="w-52 h-[800px] shrink-0 object-cover"
                />
                <div className="relative">
                    {iframeSrc ? (
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
                        src={`${ASSETS_BASE_URL}/assets/border.png`}
                        className="bg-black w-[1000px] h-[800px]"
                    />
                </div>
                <img
                    src={bannerSrc}
                    className="w-52 h-[800px] shrink-0 object-cover"
                />
            </div>
        </div>
    )
}
