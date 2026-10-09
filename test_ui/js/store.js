const KEY = "kologram.session";

export function loadSession() {
  try {
    return JSON.parse(localStorage.getItem(KEY) || "null");
  } catch {
    return null;
  }
}

export function saveSession(s) {
  localStorage.setItem(KEY, JSON.stringify(s));
}

export function clearSession() {
  localStorage.removeItem(KEY);
}

export function parseJwt(token) {
  try {
    const payload = token.split(".")[1];
    const json = atob(payload.replace(/-/g, "+").replace(/_/g, "/"));
    return JSON.parse(json);
  } catch {
    return null;
  }
}

export function getTheme() {
  return localStorage.getItem("kologram.theme") || "light";
}

export function setTheme(t) {
  localStorage.setItem("kologram.theme", t);
  document.documentElement.setAttribute("data-theme", t === "dark" ? "dark" : "light");
}
