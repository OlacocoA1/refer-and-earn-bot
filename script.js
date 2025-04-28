// Initialize Firebase
import { initializeApp } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-app.js";
import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword, signOut, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-auth.js";

const firebaseConfig = {
  apiKey: "AIzaSyCThCejvaE5K7rUwwMcQZYeuGd7rkhqhmQ",
  authDomain: "cashchop-aa33e.firebaseapp.com",
  projectId: "cashchop-aa33e",
  storageBucket: "cashchop-aa33e.firebasestorage.app",
  messagingSenderId: "977465105616",
  appId: "1:977465105616:web:f8dcd659d244c1b5dd52d5",
  measurementId: "G-R471K682RM"
};

// Initialize Firebase App and Auth
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

// Handle user registration
const registerForm = document.getElementById('register-form');
if (registerForm) {
  registerForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;

    createUserWithEmailAndPassword(auth, email, password)
      .then((userCredential) => {
        alert('Account created successfully!');
        window.location.href = 'dashboard.html';
      })
      .catch((error) => {
        document.getElementById('register-error').textContent = error.message;
      });
  });
}

// Handle user login
const loginForm = document.getElementById('login-form');
if (loginForm) {
  loginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    signInWithEmailAndPassword(auth, email, password)
      .then((userCredential) => {
        alert('Login successful!');
        window.location.href = 'dashboard.html';
      })
      .catch((error) => {
        document.getElementById('login-error').textContent = error.message;
      });
  });
}

// Check authentication state (only runs on dashboard)
const userInfo = document.getElementById('user-info');
if (userInfo) {
  onAuthStateChanged(auth, (user) => {
    if (user) {
      userInfo.innerHTML = `<p>Welcome, ${user.email}</p>`;
    } else {
      window.location.href = 'index.html';
    }
  });
}

// Handle logout
const logoutButton = document.getElementById('logout-button');
if (logoutButton) {
  logoutButton.addEventListener('click', () => {
    signOut(auth)
      .then(() => {
        alert('You have been logged out.');
        window.location.href = 'index.html';
      })
      .catch((error) => {
        alert('Error logging out: ' + error.message);
      });
  });
}

// Paystack Payment Integration
const payButton = document.getElementById('payButton');
if (payButton) {
  payButton.addEventListener('click', () => {
    let handler = PaystackPop.setup({
      key: 'pk_live_b5fa4e730d9baa38f7ff012ad4d263d5d3459c5b', // Live key
      email: auth.currentUser.email,
      amount: 500 * 100, // Amount in Kobo (₦500)
      currency: "NGN",
      ref: 'cashchop-' + Math.floor((Math.random() * 1000000000) + 1),
      callback: function(response) {
        alert('Payment successful. Reference: ' + response.reference);
      },
      onClose: function() {
        alert('Transaction was not completed.');
      }
    });
    handler.openIframe();
  });
}
