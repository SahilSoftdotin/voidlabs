import Link from 'next/link'

export default function NotFound() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-6 md:p-24">
      <div className="text-center max-w-2xl mx-auto space-y-6">
        <h1 className="text-6xl font-bold text-cyan-400">404</h1>
        <h2 className="text-3xl font-bold text-white">Page Not Found</h2>
        <p className="text-lg text-gray-300">
          The page you're looking for doesn't exist or has been moved.
        </p>

        <nav className="flex flex-wrap gap-4 justify-center mt-12">
          <Link
            href="/"
            className="px-6 py-3 bg-cyan-500 hover:bg-cyan-400 text-black font-semibold rounded-lg transition-colors duration-200"
          >
            Back to Home
          </Link>
          <Link
            href="/projects/void"
            className="px-6 py-3 border-2 border-cyan-400 text-cyan-400 hover:bg-cyan-400 hover:text-black font-semibold rounded-lg transition-colors duration-200"
          >
            View Projects
          </Link>
        </nav>

        <p className="text-sm text-gray-500">
          If you believe this is a mistake, please contact us.
        </p>
      </div>
    </main>
  )
}
