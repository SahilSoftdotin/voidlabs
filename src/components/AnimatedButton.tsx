'use client';

import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface AnimatedButtonProps {
  href: string;
  children: ReactNode;
  isExternal?: boolean;
  className?: string;
  variant?: 'primary' | 'secondary';
}

export default function AnimatedButton({
  href,
  children,
  isExternal = false,
  className = '',
  variant = 'primary',
}: AnimatedButtonProps) {
  const baseStyles =
    variant === 'primary'
      ? 'bg-cyan-500 hover:bg-cyan-400 text-black'
      : 'border-2 border-cyan-400 text-cyan-400 hover:bg-cyan-400 hover:text-black';

  const props = isExternal
    ? {
        href,
        target: '_blank',
        rel: 'noopener noreferrer',
      }
    : { href };

  return (
    <motion.a
      {...(props as any)}
      className={`px-6 py-3 font-semibold rounded-lg transition-colors duration-200 block relative overflow-hidden ${baseStyles} ${className}`}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Animated background shine effect */}
      <motion.div
        className="absolute inset-0 bg-white/10 -left-full"
        whileHover={{ left: 'full' }}
        transition={{ duration: 0.5 }}
      />
      <span className="relative z-10 flex items-center justify-center gap-2">{children}</span>
    </motion.a>
  );
}
