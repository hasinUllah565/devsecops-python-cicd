/* SecureTasks front-end behaviour (no inline scripts, CSP friendly). */
(function () {
  "use strict";

  var STORAGE_KEY = "securetasks-theme";
  var root = document.documentElement;

  function storedTheme() {
    try {
      return window.localStorage.getItem(STORAGE_KEY);
    } catch (err) {
      return null;
    }
  }

  function saveTheme(theme) {
    try {
      window.localStorage.setItem(STORAGE_KEY, theme);
    } catch (err) {
      /* Storage can be unavailable (private mode); the theme still applies. */
    }
  }

  function preferredTheme() {
    var saved = storedTheme();
    if (saved === "light" || saved === "dark") {
      return saved;
    }
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
  }

  // Apply immediately (script is loaded in <head>) to avoid a flash.
  root.setAttribute("data-bs-theme", preferredTheme());

  document.addEventListener("DOMContentLoaded", function () {
    // Theme toggle buttons
    document.querySelectorAll("[data-theme-toggle]").forEach(function (button) {
      button.addEventListener("click", function () {
        var next = root.getAttribute("data-bs-theme") === "dark" ? "light" : "dark";
        root.setAttribute("data-bs-theme", next);
        saveTheme(next);
      });
    });

    // Confirm before destructive form submissions
    document.querySelectorAll("form[data-confirm]").forEach(function (form) {
      form.addEventListener("submit", function (event) {
        if (!window.confirm(form.getAttribute("data-confirm"))) {
          event.preventDefault();
        }
      });
    });

    // Prevent double submissions
    document.querySelectorAll("form").forEach(function (form) {
      form.addEventListener("submit", function (event) {
        if (event.defaultPrevented) {
          return;
        }
        var submit = form.querySelector("button[type='submit']");
        if (submit && form.method.toLowerCase() === "post") {
          window.setTimeout(function () {
            submit.disabled = true;
          }, 0);
        }
      });
    });

    // Auto-dismiss success/info flash messages
    document.querySelectorAll(".alert-success, .alert-info").forEach(function (alertEl) {
      window.setTimeout(function () {
        if (window.bootstrap && window.bootstrap.Alert) {
          window.bootstrap.Alert.getOrCreateInstance(alertEl).close();
        }
      }, 5000);
    });
  });
})();
