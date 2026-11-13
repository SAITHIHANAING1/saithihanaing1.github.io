// Optional: draw the detection boxes in once the photo is on screen.
// The page is complete without this; CSS skips the animation for reduced motion.
document.querySelectorAll('.frame').forEach((frame) => {
  const img = frame.querySelector('img');
  const draw = () => frame.classList.add('is-drawn');
  if (!img || img.complete) draw();
  else img.addEventListener('load', draw, { once: true });
});
