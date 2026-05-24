'use client';

import { useEffect, useState } from 'react';
import { throttle } from '@/lib/utils';

interface ScrollPosition {
  x: number;
  y: number;
  progress: number; // 0-1, percentage of page scrolled
}

export const useScrollAnimation = () => {
  const [scroll, setScroll] = useState<ScrollPosition>({
    x: 0,
    y: 0,
    progress: 0,
  });

  useEffect(() => {
    const handleScroll = throttle(() => {
      const window_height = document.documentElement.scrollHeight - window.innerHeight;
      const scrolled = window.scrollY / window_height;

      setScroll({
        x: window.scrollX,
        y: window.scrollY,
        progress: Math.min(scrolled, 1),
      });
    }, 16); // ~60fps

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return scroll;
};

export const useElementInView = (ref: React.RefObject<HTMLElement>, threshold = 0.1) => {
  const [isInView, setIsInView] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observer.unobserve(entry.target);
        }
      },
      { threshold }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, [ref, threshold]);

  return isInView;
};
