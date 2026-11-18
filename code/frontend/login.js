"use strict";

// Expected server contract (coordinate with backend implementation):
// POST /auth/login, JSON: {username, password}
// Success: 200 {role: "student" | "instructor" | "admin"};
// server sets an HttpOnly session cookie. Failed login: 401/403.
// No client-side role selector or hardcoded credentials.

const form = document.getElementById("login-form");
const message = document.getElementById("login-message");
const button = document.getElementById("sign-in-button");
const passwordField = document.getElementById("password");
const toggle = document.getElementById("toggle-password");

const dashboardByRole = Object.freeze({
  student: "/student",
  instructor: "/dashboard",
  admin: "/admin"
});

function showMessage(text, kind = "error") {
  message.textContent = text;
  message.className = kind === "notice" ? "message notice" : "message";
}

toggle.addEventListener("click", () => {
  const isVisible = passwordField.type === "text";
  passwordField.type = isVisible ? "password" : "text";
  toggle.textContent = isVisible ? "Show" : "Hide";
  toggle.setAttribute("aria-label", isVisible ? "Show password" : "Hide password");
  toggle.setAttribute("aria-pressed", String(!isVisible));
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const username = document.getElementById("username").value.trim();
  const password = passwordField.value;
  if (!username || !password) {
    showMessage("Enter your username and password.");
    return;
  }
  button.disabled = true;
  button.textContent = "Signing in…";
  showMessage("Checking credentials…", "notice");
  try {
    const response = await fetch("/auth/login", {
      method: "POST",
      credentials: "same-origin",
      headers: {"Content-Type": "application/json", "Accept": "application/json"},
      body: JSON.stringify({username, password})
    });
    if (response.status === 401 || response.status === 403) {
      showMessage("Invalid username or password.");
      return;
    }
    if (response.status === 404 || response.status === 405) {
      showMessage("Login is not connected yet. The authentication API is still being implemented.");
      return;
    }
    if (!response.ok) {
      showMessage("Sign-in is temporarily unavailable. Please try again.");
      return;
    }
    const data = await response.json();
    const role = String(data?.role || "").toLowerCase();
    if (!Object.hasOwn(dashboardByRole, role)) {
      showMessage("Server returned an unrecognized account role.");
      return;
    }
    // The server MUST enforce access to these destinations and all related APIs.
    window.location.assign(dashboardByRole[role]);
  } catch (_) {
    showMessage("Couldn't connect to GradeTracker. Check your connection and try again.");
  } finally {
    button.disabled = false;
    button.innerHTML = 'Sign in <span aria-hidden="true">→</span>';
  }
});
