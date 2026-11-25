(function () {
  // 1. Tap di HP: aktifkan efek dengan kelas is-on
  var isTouch = !window.matchMedia('(hover: hover)').matches;
  if (isTouch) {
    document.querySelectorAll('.hover-swap').forEach(function (el) {
      el.addEventListener('click', function () {
        // Tutup kartu lain yang sedang aktif
        document.querySelectorAll('.hover-swap.is-on').forEach(function (other) {
          if (other !== el) other.classList.remove('is-on');
        });
        el.classList.toggle('is-on');
      });
    });
  }

  // 2. Reveal saat scroll
  if ('IntersectionObserver' in window) {
    var targets = document.querySelectorAll('.hover-reveal');
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });

    targets.forEach(function (el) { observer.observe(el); });
  } else {
    // Browser lama: tampilkan semua langsung
    document.querySelectorAll('.hover-reveal').forEach(function (el) {
      el.classList.add('is-visible');
    });
  }
})();