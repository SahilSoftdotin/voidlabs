'use client';

import { motion } from 'framer-motion';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.2,
      delayChildren: 0.3,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 50 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.6,
    },
  },
};

interface Project {
  id: string;
  title: string;
  description: string;
  tags: string[];
  image?: string;
  url?: string;
}

const projects: Project[] = [
  {
    id: '1',
    title: 'VOIDLABS Website',
    description: 'A modern, animated portfolio website built with Next.js, React, and Tailwind CSS.',
    tags: ['Next.js', 'React', 'Tailwind', 'Animation'],
  },
  {
    id: '2',
    title: 'Brand Identity System',
    description: 'Complete design system for creative studios with modern UI components.',
    tags: ['Design', 'UI/UX', 'System Design'],
  },
  {
    id: '3',
    title: 'Digital Innovation Platform',
    description: 'Interactive platform showcasing latest trends in digital design and technology.',
    tags: ['Platform', 'Interactive', 'Design'],
  },
];

export default function ProjectsPage() {
  return (
    <main className="min-h-screen p-6 md:p-24 relative z-10">
      <motion.div
        className="max-w-6xl mx-auto"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Page Header */}
        <motion.div variants={itemVariants} className="mb-16 text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-cyan-400 mb-4 text-glow animate-glow">
            Our Projects
          </h1>
          <p className="text-xl text-gray-300">
            Explore our portfolio of innovative design and development solutions
          </p>
        </motion.div>

        {/* Projects Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
          {projects.map((project) => (
            <motion.div
              key={project.id}
              className="glass glass-hover p-6 rounded-lg min-h-96 flex flex-col justify-between"
              variants={itemVariants}
              whileHover={{ y: -10 }}
            >
              <div>
                <h3 className="text-2xl font-bold text-cyan-400 mb-3">{project.title}</h3>
                <p className="text-gray-300 mb-4">{project.description}</p>
              </div>

              <div className="mt-auto">
                <div className="flex flex-wrap gap-2">
                  {project.tags.map((tag) => (
                    <span
                      key={tag}
                      className="px-3 py-1 bg-cyan-400/20 text-cyan-300 text-sm rounded-full"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Call to Action */}
        <motion.div
          className="text-center py-12 border-t border-cyan-400/20"
          variants={itemVariants}
        >
          <p className="text-gray-400 mb-6">
            Interested in working together? Let's create something amazing.
          </p>
          <motion.a
            href="https://github.com/SahilSoftdotin"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block px-8 py-3 border-2 border-cyan-400 text-cyan-400 hover:bg-cyan-400 hover:text-black font-semibold rounded-lg transition-colors duration-200"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Get in Touch
          </motion.a>
        </motion.div>
      </motion.div>
    </main>
  );
}
