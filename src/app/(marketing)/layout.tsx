'use client';

import { ReactNode } from 'react';
import { AnimatedBackground, FloatingParticles } from '@/components/animations';

export default function MarketingLayout({ children }: { children: ReactNode }) {
  return (
    <>
      <AnimatedBackground />
      <FloatingParticles />
      {children}
    </>
  );
}
