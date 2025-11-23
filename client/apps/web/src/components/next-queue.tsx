export default function NextQueue() {
    return (
        <div className="flex gap-2 hover:bg-gray-100 hover:dark:bg-gray-800 p-2 rounded-lg transition-all duration-200">
            <div className="w-16 h-16 bg-red-300  cursor-pointer   border rounded hover:bg-red-200"></div>
            <div className="w-16 h-16 bg-blue-300 cursor-pointer border rounded hover:bg-blue-200"></div>
            <div className="w-16 h-16 bg-green-300 cursor-pointer border rounded hover:bg-green-200"></div>
        </div>
    )
}