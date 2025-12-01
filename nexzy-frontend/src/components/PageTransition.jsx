import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { animate } from 'animejs';

const PageTransition = ({ children }) => {
  const location = useLocation();
  const [displayChildren, setDisplayChildren] = useState(children);

  useEffect(() => {
    if (location.pathname !== window.location.pathname) return;

    const transitionFlow = async () => {
      // 1. Curtain Up (Cover Screen)
      await animate('.page-curtain', {
        scaleY: [0, 1],
        transformOrigin: 'bottom',
        duration: 500,
        ease: 'inOutQuart'
      }).finished;

      // 2. Swap Content
      setDisplayChildren(children);
      window.scrollTo(0, 0);

      // 3. Curtain Down (Reveal New Page)
      await animate('.page-curtain', {
        scaleY: [1, 0],
        transformOrigin: 'top',
        delay: 200, // Slight pause
        duration: 600,
        ease: 'inOutQuart'
      }).finished;
    };

    transitionFlow();
  }, [location, children]);

  return (
    <>
      <div className="page-curtain fixed inset-0 bg-white z-[9999] pointer-events-none scale-y-0" />
      {displayChildren}
    </>
  );
};

export default PageTransition;