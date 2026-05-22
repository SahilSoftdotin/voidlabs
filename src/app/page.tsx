'use client';

import { motion } from 'framer-motion';
import AnimatedBackground from '@/components/AnimatedBackground';
import FloatingParticles from '@/components/FloatingParticles';
import AnimatedText from '@/components/AnimatedText';
import AnimatedButton from '@/components/AnimatedButton';

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
      type: 'spring',
      stiffness: 100,
      damping: 30,
    },
  },
};

export default function Home() {
  return (
    <>
      <AnimatedBackground />
      <FloatingParticles />
      
      <main className="flex min-h-screen flex-col items-center justify-center p-6 md:p-24 relative z-10">
        <motion.div
          className="text-center max-w-4xl mx-auto space-y-6"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {/* Animated title */}
          <motion.div variants={itemVariants} className="mb-4">
            <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold text-cyan-400 drop-shadow-lg text-glow animate-glow">
              VOIDLABS
            </h1>
          </motion.div>

          {/* Subtitle with animation */}
          <motion.div variants={itemVariants} className="mb-8">
            <AnimatedText
              text="A creative studio crafting experiences at the intersection of design and technology"
              className="text-xl md:text-2xl text-gray-300 leading-relaxed justify-center"
            />
          </motion.div>

          {/* Description */}
          <motion.p
            variants={itemVariants}
            className="text-base md:text-lg text-gray-400 mb-12 leading-relaxed"
          >
            We specialize in brand identity, UI/UX design, and digital innovation. Explore our
            projects and see what we can create together.
          </motion.p>

          {/* Animated buttons */}
          <motion.nav
            variants={itemVariants}
            className="flex flex-wrap gap-4 justify-center mt-12"
          >
            <AnimatedButton
              href="/voidlabs/projects/void"
              variant="primary"
              className="animate-glow"
            >
              ✨ Explore Projects
            </AnimatedButton>
            <AnimatedButton
              href="https://github.com/SahilSoftdotin"
              variant="secondary"
              isExternal
            >
              → GitHub
            </AnimatedButton>
          </motion.nav>

          {/* Decorative elements */}
          <motion.div
            className="mt-20 pt-12 border-t border-cyan-400/20"
            variants={itemVariants}
          >
            <p className="text-sm md:text-base text-gray-500 animate-pulse-glow">
              ⚡ Scroll to explore more ⚡
            </p>
          </motion.div>
        </motion.div>

        {/* Bottom accent */}
        <motion.div
          className="absolute bottom-10 left-1/2 transform -translate-x-1/2"
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <div className="text-cyan-400/50 text-2xl">↓</div>
        </motion.div>
      </main>

      {/* Additional animated sections */}
      <section className="min-h-screen relative overflow-hidden p-6 md:p-24 flex items-center justify-center">
        <motion.div
          className="absolute inset-0 -z-10"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 1 }}
          viewport={{ once: true }}
        >
          <div className="absolute top-20 right-20 w-80 h-80 bg-purple-500/5 rounded-full blur-3xl animate-pulse-glow" />
          <div className="absolute bottom-20 left-20 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl animate-pulse-glow" />
        </motion.div>

        <motion.div
          className="text-center max-w-3xl mx-auto relative z-10"
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-6 text-glow">
            Why Choose VOIDLABS?
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
            {[
              {
                title: 'Innovative Design',
                desc: 'Cutting-edge visual experiences',
                icon: '🎨',
              },
              {
                title: 'Technology First',
                desc: 'Built on modern tech stack',
                icon: '⚙️',
              },
              {
                title: 'Results Driven',
                desc: 'Measurable impact & growth',
                icon: '📈',
              },
            ].map((item, idx) => (
              <motion.div
                key={idx}
                className="glass glass-hover p-6 rounded-lg"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.2 }}
                viewport={{ once: true }}
              >
                <div className="text-4xl mb-4">{item.icon}</div>
                <h3 className="text-xl font-semibold mb-2 text-cyan-400">{item.title}</h3>
                <p className="text-gray-400">{item.desc}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </section>
    </>
  );
}
