import { useEffect, useRef } from 'react';
import { animate } from 'animejs';

export const useMagnetic = (ref) => {
  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const handleMouseMove = (e) => {
      const { left, top, width, height } = element.getBoundingClientRect();
      const centerX = left + width / 2;
      const centerY = top + height / 2;
      
      // Calculate distance from center
      const x = (e.clientX - centerX) * 0.5; // 0.5 = Magnetic strength
      const y = (e.clientY - centerY) * 0.5;

      // Animate with Spring physics (Anime.js v4)
      animate(element, {
        x: x,
        y: y,
        duration: 100, // Quick response
        ease: 'outQuad'
      });
    };

    const handleMouseLeave = () => {
      // Snap back to center with elasticity
      animate(element, {
        x: 0,
        y: 0,
        duration: 800,
        ease: 'outElastic(1, .5)'
      });
    };

    element.addEventListener('mousemove', handleMouseMove);
    element.addEventListener('mouseleave', handleMouseLeave);

    return () => {
      element.removeEventListener('mousemove', handleMouseMove);
      element.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, [ref]);
};