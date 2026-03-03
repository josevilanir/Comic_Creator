import React, { useRef } from 'react';
import { motion, useInView, useAnimation } from 'framer-motion';

export function BlurFade({
  children,
  className,
  delay = 0,
  yOffset = 6,
  duration = 0.4,
  inView = false,
  blur = '6px',
}) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-50px' });
  const shouldAnimate = inView ? isInView : true;

  return (
    <motion.div
      ref={ref}
      className={className}
      initial={{ opacity: 0, y: yOffset, filter: `blur(${blur})` }}
      animate={
        shouldAnimate
          ? { opacity: 1, y: 0, filter: 'blur(0px)' }
          : { opacity: 0, y: yOffset, filter: `blur(${blur})` }
      }
      transition={{
        delay,
        duration,
        ease: [0.21, 0.47, 0.32, 0.98],
      }}
    >
      {children}
    </motion.div>
  );
}
