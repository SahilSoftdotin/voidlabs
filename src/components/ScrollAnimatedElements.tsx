'use client';

import { motion, useScroll, useTransform } from 'framer-motion';
import { useRef } from 'react';

export default function ScrollAnimatedElements() {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll();
  
  const y = useTransform(scrollYProgress, [0, 1], [0, 100]);
  const opacity = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [1, 1, 1, 0.5]);

  return (
    <div ref={ref} className="relative w-full">
      <motion.div
        style={{ y, opacity }}
        className="fixed inset-0 pointer-events-none -z-10"
      >
        {/* Parallax background effect */}
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-purple-900/5 to-transparent" />
      </motion.div>
    </div>
  );
}
