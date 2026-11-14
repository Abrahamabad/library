document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.getElementById("sidebar");
  const menuToggle = document.getElementById("menu-toggle");
  const backdrop = document.getElementById("sidebar-backdrop");

  const setSidebarOpen = (isOpen) => {
    if (!sidebar || !menuToggle || !backdrop) return;
    sidebar.classList.toggle("open", isOpen);
    menuToggle.setAttribute("aria-expanded", String(isOpen));
    menuToggle.setAttribute("aria-label", isOpen ? "Close navigation" : "Open navigation");
    backdrop.hidden = !isOpen;
  };

  if (sidebar && menuToggle && backdrop) {
    menuToggle.addEventListener("click", () => {
      setSidebarOpen(!sidebar.classList.contains("open"));
    });
    backdrop.addEventListener("click", () => setSidebarOpen(false));
    sidebar.querySelectorAll(".nav-link").forEach((link) => {
      link.addEventListener("click", () => setSidebarOpen(false));
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") setSidebarOpen(false);
    });
  }

  document.querySelectorAll(".alert").forEach((alert) => {
    const dismissButton = alert.querySelector("button");
    if (dismissButton) dismissButton.addEventListener("click", () => alert.remove());
  });
});
