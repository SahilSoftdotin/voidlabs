export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-6 md:p-24">
      <div className="text-center max-w-4xl mx-auto space-y-6">
        <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold mb-4 text-cyan-400 drop-shadow-lg">
          VOIDLABS
        </h1>
        
        <p className="text-xl md:text-2xl text-gray-300 mb-8 leading-relaxed">
          A creative studio crafting experiences at the intersection of design and technology
        </p>
        
        <p className="text-base md:text-lg text-gray-400 mb-12 leading-relaxed">
          We specialize in brand identity, UI/UX design, and digital innovation. 
          Explore our projects and see what we can create together.
        </p>

        <nav className="flex flex-wrap gap-4 justify-center mt-12">
          <a 
            href="/voidlabs/projects/void" 
            className="px-6 py-3 bg-cyan-500 hover:bg-cyan-400 text-black font-semibold rounded-lg transition-colors duration-200"
            aria-label="View Void project"
          >
            Explore Projects
          </a>
          <a 
            href="https://github.com/SahilSoftdotin" 
            target="_blank"
            rel="noopener noreferrer"
            className="px-6 py-3 border-2 border-cyan-400 text-cyan-400 hover:bg-cyan-400 hover:text-black font-semibold rounded-lg transition-colors duration-200"
            aria-label="Visit GitHub profile"
          >
            GitHub
          </a>
        </nav>
      </div>
    </main>
  )
}
