import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useInfiniteQuery } from '@tanstack/react-query'
import { createFileRoute } from '@tanstack/react-router'
import { useEffect, useRef, useState } from 'react'
import { Loader2, X } from 'lucide-react'
import claudeMathGamesLogo from '@/assets/claudemathgames.png'
import { useNavigate } from '@tanstack/react-router'

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8001"

// Daren's curated recommendations - games that have been tested
const RECOMMENDED_GAMES = [
    { timestamp: "20251125_155759", id: "43" },
    { timestamp: "20251125_115145", id: "17" },
    { timestamp: "20251125_155759", id: "26" },
    { timestamp: "20251125_155759", id: "17" },
    { timestamp: "20251125_155759", id: "57" },
    { timestamp: "20251125_155759", id: "19" },
    { timestamp: "20251125_155759", id: "20" },
    { timestamp: "20251125_155759", id: "34" },
    { timestamp: "20251125_155759", id: "39" },
    { timestamp: "20251125_115145", id: "20" },
    { timestamp: "20251125_155759", id: "2" },
    { timestamp: "20251125_155759", id: "4" },
    { timestamp: "20251125_155759", id: "49" },
    { timestamp: "20251125_155759", id: "52" },
    { timestamp: "20251125_115145", id: "9" },
    { timestamp: "20251125_115145", id: "10" },
    { timestamp: "20251125_115145", id: "21" },
    { timestamp: "20251125_031027", id: "22" },
]

type GameMetadata = {
    name: string
    summary: string
    base_game: string
    genre: string[]
    prompt: string
}

type Project = {
    id: string
    path_to_index_html: string
    path_to_banner_art: string | null
    path_to_cover_art: string | null
    metadata: GameMetadata
    gamePackId?: string
}

type GamePack = {
    index: number
    id: string
    projects: Project[]
}

const ITEMS_PER_PAGE = 12

function isRecommended(project: Project): boolean {
    return RECOMMENDED_GAMES.some(
        rec => rec.timestamp === project.gamePackId && rec.id === project.id
    )
}

function filterProjects(projects: Project[], filters: { genres: string[], baseGames: string[] }): Project[] {
    let filtered = projects

    if (filters.genres.length > 0) {
        filtered = filtered.filter(project =>
            project.metadata.genre.some(genre => filters.genres.includes(genre))
        )
    }

    if (filters.baseGames.length > 0) {
        filtered = filtered.filter(project =>
            filters.baseGames.includes(project.metadata.base_game)
        )
    }

    return filtered
}

async function fetchManifest(): Promise<{ recommended: Project[], notTested: Project[] }> {
    const res = await fetch(`${API_BASE_URL}/projects/manifest.json`)
    const gamePacks: GamePack[] = await res.json()

    // Flatten all projects from all game packs
    const allProjects = gamePacks.flatMap(pack =>
        pack.projects.map(project => ({
            ...project,
            gamePackId: pack.id
        }))
    )

    // Partition into recommended and not tested
    const recommended: Project[] = []
    const notTested: Project[] = []

    allProjects.forEach(project => {
        if (isRecommended(project)) {
            recommended.push(project)
        } else {
            notTested.push(project)
        }
    })

    // Sort each list: projects with cover art first, then without
    const sortByCoverArt = (a: Project, b: Project) => {
        const aHasCover = a.path_to_cover_art ? 1 : 0
        const bHasCover = b.path_to_cover_art ? 1 : 0
        return bHasCover - aHasCover
    }

    recommended.sort(sortByCoverArt)
    notTested.sort(sortByCoverArt)

    return { recommended, notTested }
}

async function fetchRecommendedGames({ pageParam }: { pageParam: number }) {
    const { recommended } = await fetchManifest()
    const start = pageParam * ITEMS_PER_PAGE
    const end = start + ITEMS_PER_PAGE
    const projects = recommended.slice(start, end)

    return {
        projects,
        nextCursor: end < recommended.length ? pageParam + 1 : undefined,
        totalCount: recommended.length
    }
}

async function fetchNotTestedGames({ pageParam }: { pageParam: number }) {
    const { notTested } = await fetchManifest()
    const start = pageParam * ITEMS_PER_PAGE
    const end = start + ITEMS_PER_PAGE
    const projects = notTested.slice(start, end)

    return {
        projects,
        nextCursor: end < notTested.length ? pageParam + 1 : undefined,
        totalCount: notTested.length
    }
}

export const Route = createFileRoute('/games')({
    component: RouteComponent,
})

type FetchResult = {
    projects: Project[]
    nextCursor?: number
    totalCount: number
}

function GameGrid({
    title,
    queryKey,
    queryFn,
    filters
}: {
    title: string
    queryKey: string[]
    queryFn: (context: { pageParam: number }) => Promise<FetchResult>
    filters: { genres: string[], baseGames: string[] }
}) {
    const observerTarget = useRef<HTMLDivElement>(null)
    const navigate = useNavigate()
    const {
        data,
        error,
        fetchNextPage,
        hasNextPage,
        isFetching,
        isFetchingNextPage,
        status,
    } = useInfiniteQuery({
        queryKey: [...queryKey, filters],
        queryFn: ({ pageParam }: { pageParam: number }) => queryFn({ pageParam }),
        initialPageParam: 0,
        getNextPageParam: (lastPage: FetchResult) => lastPage.nextCursor,
    })

    // Filter projects client-side
    const filteredPages = data?.pages.map(page => ({
        ...page,
        projects: filterProjects(page.projects, filters)
    }))

    // Infinite scroll observer
    useEffect(() => {
        const observer = new IntersectionObserver(
            (entries) => {
                if (entries[0].isIntersecting && hasNextPage && !isFetching) {
                    fetchNextPage()
                }
            },
            { threshold: 0.1 }
        )

        if (observerTarget.current) {
            observer.observe(observerTarget.current)
        }

        return () => observer.disconnect()
    }, [hasNextPage, isFetching, fetchNextPage])

    if (status === 'pending') {
        return (
            <div className="w-full flex items-center justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin" />
            </div>
        )
    }

    if (status === 'error') {
        return (
            <div className="w-full flex items-center justify-center py-12 text-red-500">
                Error: {error.message}
            </div>
        )
    }

    const totalCount = data.pages[0]?.totalCount || 0
    const filteredCount = filteredPages?.reduce((acc, page) => acc + page.projects.length, 0) || 0

    if (filteredCount === 0) {
        return null
    }

    return (
        <div className="mb-3">
            <h2 className="text-2xl font-bold mb-6">
                {title} ({filteredCount}{filteredCount !== totalCount ? ` of ${totalCount}` : ''})
            </h2>

            <div
                className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4"
                style={{
                    imageRendering: 'pixelated',
                }}
            >
                {filteredPages?.map((page, pageIndex) => (
                    <div key={pageIndex} className="contents">
                        {page.projects.map((project) => (
                            <div
                                onClick={() => {
                                    navigate({ to: '/play/$timestamp/$gameId', params: { timestamp: project.gamePackId, gameId: project.id } })
                                }}
                                key={`${project.gamePackId}-${project.id}`}
                                className="
                                    relative cursor-pointer group
                                    border-4 border-black
                                    bg-gray-900
                                    shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]
                                    hover:shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]
                                    hover:translate-x-[-2px] hover:translate-y-[-2px]
                                    transition-all duration-150
                                "
                                style={{
                                    aspectRatio: '3/4',
                                }}
                            >
                                {project.path_to_cover_art ? (
                                    <div
                                        className="absolute inset-0 bg-cover bg-center"
                                        style={{
                                            backgroundImage: `url(${API_BASE_URL}/cartridge_arts/${project.path_to_cover_art})`,
                                            backgroundSize: '150% 120%',
                                            imageRendering: 'pixelated',
                                        }}
                                    />
                                ) : (
                                    <div
                                        className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent transition-opacity flex items-center justify-center"
                                        style={{
                                            imageRendering: 'pixelated',
                                        }}
                                    >
                                        <span className="text-white text-6xl font-bold">
                                            {project.metadata.name.charAt(0)}
                                        </span>
                                    </div>
                                )}
                                <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                                <div className="absolute bottom-0 left-0 right-0 p-2 text-center">
                                    <span
                                        className="text-xs font-bold text-white opacity-0 group-hover:opacity-100 transition-opacity"
                                        style={{
                                            fontFamily: '"Press Start 2P", monospace',
                                            textShadow: '2px 2px 0 #000',
                                            fontSize: '8px',
                                        }}
                                    >
                                        {project.metadata.name.toUpperCase()}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                ))}
            </div>

            {/* Intersection observer target */}
            <div ref={observerTarget} className="h-20 flex items-center justify-center mt-8">
                {isFetchingNextPage && (
                    <Loader2 className="w-6 h-6 animate-spin text-uchu-green" />
                )}
            </div>

            {!hasNextPage && data.pages.length > 0 && totalCount > ITEMS_PER_PAGE && (
                <p className="text-center text-gray-500 mt-4">
                    All {totalCount} games loaded
                </p>
            )}
        </div>
    )
}

function RouteComponent() {
    const [selectedGenres, setSelectedGenres] = useState<string[]>([])
    const [selectedBaseGames, setSelectedBaseGames] = useState<string[]>([])
    const [allGenres, setAllGenres] = useState<string[]>([])
    const [allBaseGames, setAllBaseGames] = useState<string[]>([])

    // Fetch and extract all unique genres and base games
    useEffect(() => {
        const loadFilters = async () => {
            const { recommended, notTested } = await fetchManifest()
            const allProjects = [...recommended, ...notTested]

            const genres = new Set<string>()
            const baseGames = new Set<string>()

            allProjects.forEach(project => {
                project.metadata.genre.forEach(g => genres.add(g))
                baseGames.add(project.metadata.base_game)
            })

            setAllGenres(Array.from(genres).sort())
            setAllBaseGames(Array.from(baseGames).sort())
        }

        loadFilters()
    }, [])

    const handleGenreChange = (genre: string) => {
        if (genre === "all") {
            setSelectedGenres([])
        } else {
            setSelectedGenres([genre])
        }
    }

    const handleBaseGameChange = (baseGame: string) => {
        if (baseGame === "all") {
            setSelectedBaseGames([])
        } else {
            setSelectedBaseGames([baseGame])
        }
    }

    const clearFilters = () => {
        setSelectedGenres([])
        setSelectedBaseGames([])
    }

    const hasActiveFilters = selectedGenres.length > 0 || selectedBaseGames.length > 0

    return (
        <div className="container mx-auto px-6 py-8 pb-32">

            <GameGrid
                title="Daren's Recommendations"
                queryKey={['recommended-games']}
                queryFn={fetchRecommendedGames}
                filters={{ genres: selectedGenres, baseGames: selectedBaseGames }}
            />

            <GameGrid
                title="Not tested, might be buggy"
                queryKey={['not-tested-games']}
                queryFn={fetchNotTestedGames}
                filters={{ genres: selectedGenres, baseGames: selectedBaseGames }}
            />

            {/* Fixed Filter Bar - Floating Pill */}
            <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50">
                <div className="bg-white border-4 border-black rounded-full shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] px-6">
                    <div className="flex items-center gap-4 overflow-scroll">
                        <img src={claudeMathGamesLogo} alt="Claude CoolMathGames" className="h-20 w-20 object-contain" />

                        {/* Genre Filter */}
                        <div className="flex items-center gap-2">
                            <span className="text-black text-sm font-bold whitespace-nowrap">Genre:</span>
                            <Select
                                value={selectedGenres[0] || "all"}
                                onValueChange={handleGenreChange}
                            >
                                <SelectTrigger className="w-[140px] rounded-full border-2 border-black
                                text-black bg-white hover:bg-gray-50">
                                    <SelectValue
                                        className="" placeholder="All Genres" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="all">All Genres</SelectItem>
                                    {allGenres.map(genre => (
                                        <SelectItem key={genre} value={genre}>
                                            {genre}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        {/* Divider */}
                        <div className="h-6 w-px bg-black" />

                        {/* Base Game Filter */}
                        <div className="flex items-center gap-2">
                            <span className="text-black  text-sm font-bold whitespace-nowrap">Type:</span>
                            <Select
                                value={selectedBaseGames[0] || "all"}
                                onValueChange={handleBaseGameChange}
                            >
                                <SelectTrigger className="w-[140px] rounded-full text-black border-2 border-black bg-white hover:bg-gray-50">
                                    <SelectValue placeholder="All Types" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="all">All Types</SelectItem>
                                    {allBaseGames.map(baseGame => (
                                        <SelectItem key={baseGame} value={baseGame}>
                                            {baseGame}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        {/* Clear Filters Button */}
                        {hasActiveFilters && (
                            <>
                                <div className="h-6 w-px bg-black" />
                                <button
                                    onClick={clearFilters}
                                    className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                                    title="Clear filters"
                                >
                                    <X className="w-4 h-4" />
                                </button>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}
