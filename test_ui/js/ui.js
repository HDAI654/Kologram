export function $(sel, root = document) {
  return root.querySelector(sel);
}

export function el(html) {
  const t = document.createElement("template");
  t.innerHTML = html.trim();
  return t.content.firstElementChild;
}

export function toast(message, kind = "info") {
  const host = document.getElementById("toasts");
  if (!host) return;
  const n = el(`<div class="toast ${kind === "error" ? "error" : kind === "ok" ? "ok" : ""}"></div>`);
  n.textContent = message;
  host.appendChild(n);
  setTimeout(() => n.remove(), 4200);
}

export function escapeHtml(s) {
  return String(s ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

export function fmtMoney(amount, currency) {
  if (amount == null) return "—";
  try {
    return new Intl.NumberFormat(undefined, {
      style: "currency",
      currency: currency || "USD",
    }).format(Number(amount));
  } catch {
    return `${amount} ${currency || ""}`;
  }
}

export function statusBadge(status) {
  const s = (status || "").toLowerCase();
  return `<span class="badge ${s}">${escapeHtml(status || "—")}</span>`;
}
