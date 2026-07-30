// Deterministic starfield. Seeded so the same slide spec always renders identically —
// a re-render after a copy tweak shouldn't reshuffle the background.
(function () {
  function rng(seed) {
    let s = seed >>> 0;
    return function () {
      s = (s * 1664525 + 1013904223) >>> 0;
      return s / 4294967296;
    };
  }

  function build(el, seed) {
    const r = rng(seed);
    const stars = el.querySelector(".stars");
    const bokeh = el.querySelector(".bokeh");

    if (stars) {
      // ~260 fine dots, most of them very small and dim
      let html = "";
      for (let i = 0; i < 260; i++) {
        const x = (r() * 100).toFixed(2);
        const y = (r() * 100).toFixed(2);
        const d = (0.9 + r() * 2.4).toFixed(2);
        const o = (0.25 + r() * 0.7).toFixed(2);
        html += `<i style="left:${x}%;top:${y}%;width:${d}px;height:${d}px;opacity:${o}"></i>`;
      }
      stars.innerHTML = html;
    }

    if (bokeh) {
      // a handful of larger soft glows, kept away from the centre so they don't
      // compete with the headline
      let html = "";
      const spots = [
        [4, 22], [11, 74], [24, 12], [88, 30], [95, 66], [72, 92], [6, 47], [93, 8],
      ];
      for (const [x, y] of spots) {
        const d = (26 + r() * 30).toFixed(0);
        const o = (0.5 + r() * 0.45).toFixed(2);
        html += `<i style="left:${x}%;top:${y}%;width:${d}px;height:${d}px;margin:-${d / 2}px 0 0 -${d / 2}px;opacity:${o}"></i>`;
      }
      bokeh.innerHTML = html;
    }
  }

  window.PLAY3_starfield = build;
})();
