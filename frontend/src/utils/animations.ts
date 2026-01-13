import anime from 'animejs';

export const fadeIn = (targets: anime.AnimeAnimParams['targets']) => {
  anime({
    targets,
    opacity: [0, 1],
    translateY: [20, 0],
    duration: 800,
    easing: 'easeOutExpo'
  });
};

export const slideIn = (targets: anime.AnimeAnimParams['targets']) => {
  anime({
    targets,
    translateX: [-50, 0],
    opacity: [0, 1],
    duration: 600,
    delay: anime.stagger(100),
    easing: 'easeOutQuad'
  });
};

export const glowPulse = (targets: anime.AnimeAnimParams['targets']) => {
  anime({
    targets,
    boxShadow: [
      '0 0 0px rgba(255, 215, 0, 0)',
      '0 0 20px rgba(255, 215, 0, 0.4)',
      '0 0 0px rgba(255, 215, 0, 0)'
    ],
    duration: 2000,
    loop: true,
    easing: 'easeInOutQuad'
  });
};

export const popIn = (targets: anime.AnimeAnimParams['targets']) => {
  anime({
    targets,
    scale: [0.9, 1],
    opacity: [0, 1],
    duration: 400,
    easing: 'easeOutBack'
  });
};
