const yearEl = document.getElementById("year");
if (yearEl) {
  yearEl.textContent = new Date().getFullYear().toString();
}

const phone = "5491126601086";
const defaultMessage =
  "Hola, vi tu propuesta de armado y diseño para Tiendanube/Empretienda. Quiero coordinar una llamada.";
const waLink = document.getElementById("waLink");

if (waLink) {
  const encoded = encodeURIComponent(defaultMessage);
  waLink.href = `https://wa.me/${phone}?text=${encoded}`;
}