/**
 * Registro y ciclo de vida del Service Worker para soporte PWA Offline.
 * Conforme a SIGE_Arquitectura_Frontend_y_PWA_v1.md §5.3.3
 */

export function registerServiceWorker(): void {
  if (typeof window !== "undefined" && "serviceWorker" in navigator) {
    window.addEventListener("load", () => {
      navigator.serviceWorker
        .register("/sw.js")
        .then((registration) => {
          registration.addEventListener("updatefound", () => {
            const installingWorker = registration.installing;
            if (installingWorker) {
              installingWorker.addEventListener("statechange", () => {
                if (installingWorker.state === "installed" && navigator.serviceWorker.controller) {
                  // Nueva versión detectada disponible
                  window.dispatchEvent(new CustomEvent("sige:sw-update-available"));
                }
              });
            }
          });
        })
        .catch((error) => {
          console.warn("Fallo al registrar Service Worker:", error);
        });
    });
  }
}
