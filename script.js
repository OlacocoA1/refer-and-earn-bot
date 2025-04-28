// Firebase Authentication

// Initialize Firebase App (Make sure this script comes AFTER the Firebase SDK is loaded)
import { initializeApp } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-app.js";
import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword, signOut } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-auth.js";

const firebaseConfig = {
  apiKey: "AIzaSyCThCejvaE5K7rUwwMcQZYeuGd7rkhqhmQ",
  authDomain: "cashchop-aa33e.firebaseapp.com",
  projectId: "cashchop-aa33e",
  storageBucket: "cashchop-aa33e.appspot.com",
  messagingSenderId: "977465105616",
  appId: "1:977465105616:web:f8dcd659d244c1b5dd52d5",
  measurementId: "G-R471K682RM"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

// --- For Register Page ---
const registerForm = document.getElementById("register-form");
if (registerForm) {
  registerForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const email = document.getElementById("register-email").value;
    const password = document.getElementById("register-password").value;

    createUserWithEmailAndPassword(auth, email, password)
      .then((userCredential) => {
        window.location.href = "dashboard.html"; // Redirect to dashboard
      })
      .catch((error) => {
        document.getElementById("register-error").textContent = error.message;
      });
  });
}

// --- For Login Page ---
const loginForm = document.getElementById("login-form");
if (loginForm) {
  loginForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;

    signInWithEmailAndPassword(auth, email, password)
      .then((userCredential) => {
        window.location.href = "dashboard.html"; // Redirect to dashboard
      })
      .catch((error) => {
        document.getElementById("login-error").textContent = error.message;
      });
  });
}

// --- For Dashboard Page ---
const logoutBtn = document.getElementById("logout-btn");
if (logoutBtn) {
  logoutBtn.addEventListener("click", () => {
    signOut(auth).then(() => {
      window.location.href = "index.html"; // Redirect to login
    }).catch((error) => {
      alert("Error logging out: " + error.message);
    });
  });
}
