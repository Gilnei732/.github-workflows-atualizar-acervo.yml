(function () {
  if (!('IntersectionObserver' in window)) {
    document.querySelectorAll('.fade-in').forEach(function (el) { el.classList.add('visible'); });
    return;
  }
  const io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0, rootMargin: '0px 0px 200px 0px' });

  function observe() {
    document.querySelectorAll('.fade-in:not(.visible)').forEach(function (el) {
      var rect = el.getBoundingClientRect();
      if (rect.top < window.innerHeight + 100 && rect.bottom > -100) {
        el.classList.add('visible');
      } else {
        io.observe(el);
      }
    });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { setTimeout(observe, 300); });
  } else {
    setTimeout(observe, 300);
  }
  window.observeFadeIn = function () {
    setTimeout(observe, 300);
  };
})();