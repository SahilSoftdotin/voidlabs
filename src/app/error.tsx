'use client'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-6 md:p-24">
      <div className="text-center max-w-2xl mx-auto space-y-6">
        <h1 className="text-6xl font-bold text-red-500">Oops!</h1>
        <p className="text-xl text-gray-300">
          Something went wrong. Please try again.
        </p>
        {error.message && (
          <p className="text-sm text-gray-500 bg-gray-900 p-4 rounded-lg font-mono">
            {error.message}
          </p>
        )}
        <button
          onClick={() => reset()}
          className="px-6 py-3 bg-cyan-500 hover:bg-cyan-400 text-black font-semibold rounded-lg transition-colors duration-200"
        >
          Try Again
        </button>
        <p className="text-sm text-gray-400">
          Error ID: {error.digest || 'unknown'}
        </p>
      </div>
    </main>
  )
}
