// Open links to other hosts in a new tab
document$.subscribe(function () {
  document.querySelectorAll("a[href]").forEach(function (link) {
    if (link.hostname && link.hostname !== window.location.hostname) {
      link.target = "_blank";
      link.rel = "noopener noreferrer";
    }
  });
});
