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

export default function AboutPage() {
  return (
    <main className="min-h-screen p-6 md:p-24 relative z-10">
      <motion.div
        className="max-w-4xl mx-auto"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Page Header */}
        <motion.div variants={itemVariants} className="mb-16 text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-cyan-400 mb-4 text-glow animate-glow">
            About VOIDLABS
          </h1>
          <p className="text-xl text-gray-300">
            Crafting digital experiences at the intersection of design and technology
          </p>
        </motion.div>

        {/* Mission Section */}
        <motion.section variants={itemVariants} className="mb-12">
          <h2 className="text-3xl font-bold text-cyan-400 mb-6">Our Mission</h2>
          <p className="text-lg text-gray-300 leading-relaxed mb-4">
            VOIDLABS is a creative studio dedicated to transforming ideas into compelling digital
            experiences. We combine cutting-edge design with innovative technology to create
            solutions that inspire and engage.
          </p>
          <p className="text-lg text-gray-300 leading-relaxed">
            Our team of designers and developers work collaboratively to deliver projects that
            exceed expectations and create lasting impact for our clients.
          </p>
        </motion.section>

        {/* Values Section */}
        <motion.section variants={itemVariants} className="mb-12">
          <h2 className="text-3xl font-bold text-cyan-400 mb-6">Our Values</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {[
              {
                title: 'Innovation',
                description: 'Always pushing boundaries and exploring new possibilities in design and technology.',
              },
              {
                title: 'Excellence',
                description: 'Commitment to delivering high-quality work that stands the test of time.',
              },
              {
                title: 'Collaboration',
                description: 'Working closely with clients to understand their vision and bring it to life.',
              },
              {
                title: 'Integrity',
                description: 'Building trust through transparent communication and honest partnerships.',
              },
            ].map((value, idx) => (
              <motion.div
                key={idx}
                className="glass p-6 rounded-lg"
                whileHover={{ scale: 1.02 }}
              >
                <h3 className="text-xl font-semibold text-cyan-400 mb-2">{value.title}</h3>
                <p className="text-gray-300">{value.description}</p>
              </motion.div>
            ))}
          </div>
        </motion.section>

        {/* Services Section */}
        <motion.section variants={itemVariants} className="mb-12">
          <h2 className="text-3xl font-bold text-cyan-400 mb-6">Our Services</h2>
          <ul className="space-y-4 text-lg text-gray-300">
            <li className="flex items-start gap-4">
              <span className="text-cyan-400 text-2xl">→</span>
              <span>
                <strong>Brand Identity Design</strong> - Creating unique and memorable brand
                identities that resonate with your audience
              </span>
            </li>
            <li className="flex items-start gap-4">
              <span className="text-cyan-400 text-2xl">→</span>
              <span>
                <strong>UI/UX Design</strong> - Designing intuitive and engaging user experiences
                that drive results
              </span>
            </li>
            <li className="flex items-start gap-4">
              <span className="text-cyan-400 text-2xl">→</span>
              <span>
                <strong>Web Development</strong> - Building fast, modern, and scalable web
                applications
              </span>
            </li>
            <li className="flex items-start gap-4">
              <span className="text-cyan-400 text-2xl">→</span>
              <span>
                <strong>Digital Innovation</strong> - Exploring emerging technologies and trends
                to keep your brand ahead
              </span>
            </li>
          </ul>
        </motion.section>

        {/* CTA Section */}
        <motion.section
          variants={itemVariants}
          className="text-center py-12 border-t border-cyan-400/20"
        >
          <p className="text-gray-400 mb-6">
            Ready to start your next project? Let's collaborate and create something extraordinary.
          </p>
          <motion.a
            href="https://github.com/SahilSoftdotin"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block px-8 py-3 bg-cyan-500 hover:bg-cyan-400 text-black font-semibold rounded-lg transition-colors duration-200"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Let's Talk
          </motion.a>
        </motion.section>
      </motion.div>
    </main>
  );
}
