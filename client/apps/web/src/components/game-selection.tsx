import { Button } from '@/components/ui/button'
import type { Idea } from '@/lib/api'
import { ArrowLeftIcon, Loader2 } from 'lucide-react'
import { useState, useEffect } from 'react'
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '@/components/ui/select'
import { useQuery } from '@tanstack/react-query'

interface GameSelectionProps {
    ideas: Idea[]
    onViewList: () => void
}

interface GamePackData {
    timestamp: string
    name: string
    games: any[]
}

interface GamePackProps {
    gamePack: GamePackData
    selectedGameId: number | null
    onSelectGame: (gameId: number) => void
    onStartPlaying: () => void
}

function GamePack({ gamePack, selectedGameId, onSelectGame, onStartPlaying }: GamePackProps) {
    const [expandingGame, setExpandingGame] = useState<number | null>(null)

    const handleGameClick = (gameId: number) => {
        setExpandingGame(gameId)
        setTimeout(() => {
            onSelectGame(gameId)
            setExpandingGame(null)
            onStartPlaying()
        }, 500)
    }

    const games = Array.from({ length: gamePack.games.length }, (_, i) => i + 1)
    console.log(gamePack.games)

    return (
        <div className="mt-6 p-4">
            <div
                className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4"
                style={{
                    imageRendering: 'pixelated',
                }}
            >
                {games.map((gameId) => (
                    <div
                        key={gameId}
                        onClick={() => handleGameClick(gameId)}
                        className={`
                            relative cursor-pointer group
                            border-4 border-black
                            bg-gray-900
                            shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]
                            hover:shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]
                            hover:translate-x-[-2px] hover:translate-y-[-2px]
                            transition-all duration-150
                            ${selectedGameId === gameId ? 'ring-4 ring-yellow-400 ring-offset-2 ring-offset-black' : ''}
                            ${expandingGame === gameId ? 'animate-game-select' : ''}
                        `}
                        style={{
                            aspectRatio: '3/4',
                        }}
                    >
                        <div
                            className="absolute inset-0 bg-cover bg-center"
                            style={{
                                backgroundImage: `url(http://localhost:8000/cartridge_arts/${gamePack.timestamp}/${gameId}/cover_art.png_0)`,
                                backgroundSize: '150% 120%',
                                imageRendering: 'pixelated',
                            }}
                        />
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
                                GAME {gameId}
                            </span>
                        </div>
                    </div>
                ))}
            </div>
            {expandingGame !== null && (
                <div className="fixed inset-0 flex items-end justify-center pointer-events-none z-50">
                    <div
                        className="animate-expand-fade bg-cover bg-center"
                        style={{
                            backgroundImage: `url(http://localhost:8000/cartridge_arts/${gamePack.timestamp}/${expandingGame}/cover_art.png_0)`,
                        }}
                    />
                </div>
            )}
            <style>{`
                @keyframes game-select {
                    0% {
                        transform: scale(1);
                    }
                    50% {
                        transform: scale(1.1);
                    }
                    100% {
                        transform: scale(1);
                    }
                }
                @keyframes expand-fade {
                    0% {
                        width: 15%;
                        height: 26.67%;
                        opacity: 1;
                    }
                    60% {
                        width: 100%;
                        height: 100%;
                        opacity: 1;
                    }
                    100% {
                        width: 100%;
                        height: 100%;
                        opacity: 0;
                    }
                }
                .animate-game-select {
                    animation: game-select 0.2s ease-in;
                }
                .animate-expand-fade {
                    animation: expand-fade 0.5s ease-out forwards;
                }
            `}</style>
        </div>
    )
}

interface GameBoyProps {
    timestamp: string
    gameId: number
    onBack: () => void
}

function GameBoy({ timestamp, gameId, onBack }: GameBoyProps) {
    const { data: entryPoint, isPending } = useQuery({
        queryKey: ['entry-point', timestamp, gameId],
        queryFn: () => fetch(`http://localhost:8000/get-entry-point/${timestamp}/${gameId}`).then(res => res.json()),
    })

    const iframeSrc = entryPoint?.path
        ? `http://localhost:8000${entryPoint.path}`
        : null

    return (
        <div className="flex flex-col items-center p-6">
            <div className="flex flex-row items-center justify-center">
                <img
                    src={`http://localhost:8000/cartridge_arts/${timestamp}/${gameId}/banner_art.png_0`}
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
                        src="http://localhost:8000/assets/border.png"
                        className="bg-black w-[1000px] h-[800px]"
                    />
                </div>
                <img
                    src={`http://localhost:8000/cartridge_arts/${timestamp}/${gameId}/banner_art.png_0`}
                    className="w-52 h-[800px] shrink-0 object-cover"
                />
            </div>
        </div>
    )
}

export default function GameSelection({ ideas, onViewList }: GameSelectionProps) {
    const [selectedGamePack, setSelectedGamePack] = useState<GamePackData | null>(null)
    const [selectedGameId, setSelectedGameId] = useState<number | null>(null)
    const [isPlaying, setIsPlaying] = useState(false)

    const { data: gamePacks, isPending } = useQuery({
        queryKey: ['game-packs'],
        queryFn: () => fetch('http://localhost:8000/projects-list').then(res => res.json()),
    })

    useEffect(() => {
        if (gamePacks && gamePacks.length > 1 && !selectedGamePack) {
            console.log(gamePacks)
            setSelectedGamePack(gamePacks.find((gamePack: any) => gamePack.timestamp === "favorites") || gamePacks[0])
        }
    }, [gamePacks, selectedGamePack])
    console.log(selectedGamePack)

    if (isPending) {
        return (
            <div className="flex flex-col h-[90vh] w-full max-w-[1000px] mx-auto">
                <div className="flex-1 min-h-0 w-full flex p-12 pb-6 items-center justify-center">
                    <Loader2 className="w-12 h-12 text-uchu-blue animate-spin" />
                </div>
            </div>
        )
    }

    return (
        <div>
            <div className="flex justify-between items-center px-6">
                <Button variant='secondary' onClick={onViewList}>
                    <ArrowLeftIcon className="w-4 h-4" /> Current Game Pack
                </Button>
                <div className="flex items-center gap-2 mt-6 justify-center">
                    <h1 className="text-2xl text-uchu-green ml-auto font-bold">Gaming Mode</h1>
                    <Select value={selectedGamePack?.timestamp} onValueChange={(value) => {
                        setSelectedGamePack(gamePacks.find((gamePack: any) => gamePack.timestamp === value) || null)
                        setSelectedGameId(null)
                        setIsPlaying(false)
                    }}>
                        <SelectTrigger className="w-[180px]">
                            <SelectValue placeholder="Select a Game Pack" />
                        </SelectTrigger>
                        <SelectContent>
                            {gamePacks.map((gamePack: any) => (
                                <SelectItem key={gamePack.timestamp} value={gamePack.timestamp}>{gamePack.name}</SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                    {isPlaying && (
                        <Button variant='secondary' onClick={() => setIsPlaying(false)}>
                            Back to Grid
                        </Button>
                    )}
                </div>
            </div>
            {selectedGamePack && !isPlaying && (
                <GamePack
                    gamePack={selectedGamePack}
                    selectedGameId={selectedGameId}
                    onSelectGame={setSelectedGameId}
                    onStartPlaying={() => setIsPlaying(true)}
                />
            )}
            {isPlaying && selectedGamePack && selectedGameId && (
                <GameBoy
                    timestamp={selectedGamePack.timestamp}
                    gameId={selectedGameId}
                    onBack={() => setIsPlaying(false)}
                />
            )}
        </div>
    )

}
