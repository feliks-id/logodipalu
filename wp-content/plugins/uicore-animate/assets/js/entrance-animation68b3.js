document.addEventListener('DOMContentLoaded', () => {
  // Select all elements with the data-animation attribute
  const elementsToAnimate = document.querySelectorAll('[data-ui-animation]');

  // Create an Intersection Observer instance
  const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      const el = entry.target;
      const animationName = el.getAttribute("data-ui-animation");
      const animationSpeed = el.getAttribute("data-ui-duration");

      // 1. Add animation speed class
      if (animationSpeed === "fast") {
        el.classList.add("animated", "animated-fast");
      } else if (animationSpeed === "slow") {
        el.classList.add("animated", "animated-slow");
      } else {
        el.classList.add("animated");
      }

      // 2. Add animation name class(es)
      if (animationName) {
        el.classList.add(...animationName.split(" "));
      }

      // 3. Remove hide ONLY when animation really starts
      const onStart = () => {
        el.classList.remove("uicore-animate-hide");
        el.removeEventListener("animationstart", onStart);
      };
      el.addEventListener("animationstart", onStart, {
        once: true
      });

      // 4. Safety fallback: if animation has NO delay, remove instantly next frame
      requestAnimationFrame(() => {
        if (getComputedStyle(el).animationDelay === "0s") {
          el.classList.remove("uicore-animate-hide");
        }
      });

      // 5. Stop observing after trigger
      observer.unobserve(el);
    });
  }, {
    rootMargin: '10px',
    // Adjust the root margin as needed
    threshold: 0 // Adjust threshold as needed to control when animation is triggered
  });

  // Observe each element that should be animated
  elementsToAnimate.forEach(element => {
    observer.observe(element);
  });
});