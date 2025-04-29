// Firebase Configuration
const firebaseConfig = {
  apiKey: "AIzaSyCThCejvaE5K7rUwwMcQZYeuGd7rkhqhmQ",
  authDomain: "cashchop-aa33e.firebaseapp.com",
  projectId: "cashchop-aa33e",
  storageBucket: "cashchop-aa33e.appspot.com",
  messagingSenderId: "977465105616",
  appId: "1:977465105616:web:f8dcd659d244c1b5dd52d5",
  measurementId: "G-R471K682RM"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();
const db = firebase.firestore();

// EmailJS Configuration (replace with your own IDs)
const EMAILJS_SERVICE_ID = "your_service_id";
const EMAILJS_TEMPLATE_ID = "your_template_id";
const EMAILJS_PUBLIC_KEY = "your_public_key";

// Generate a random referral code
function generateReferralCode() {
  const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
  let code = "";
  for (let i = 0; i < 6; i++) {
    code += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return code;
}

// Register Form Handler
const registerForm = document.getElementById("register-form");
if (registerForm) {
  registerForm.addEventListener("submit", function (e) {
    e.preventDefault();
    const email = document.getElementById("register-email").value;
    const password = document.getElementById("register-password").value;
    const referralCodeInput = document.getElementById("referral-code").value.trim();
    const userReferralCode = generateReferralCode();

    auth.createUserWithEmailAndPassword(email, password)
      .then((userCredential) => {
        const user = userCredential.user;
        db.collection("users").doc(user.uid).set({
          email: email,
          points: 0,
          referralCode: userReferralCode,
          referredBy: referralCodeInput || null
        }).then(() => {
          if (referralCodeInput) {
            db.collection("users").where("referralCode", "==", referralCodeInput).get()
              .then((querySnapshot) => {
                querySnapshot.forEach((doc) => {
                  db.collection("users").doc(doc.id).update({
                    points: firebase.firestore.FieldValue.increment(10)
                  });
                });
              });
          }
          alert("Account created! You can now log in.");
          window.location.href = "index.html";
        });
      })
      .catch((error) => {
        document.getElementById("register-error").textContent = error.message;
      });
  });
}

// Login Form Handler
const loginForm = document.getElementById("login-form");
if (loginForm) {
  loginForm.addEventListener("submit", function (e) {
    e.preventDefault();
    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;

    auth.signInWithEmailAndPassword(email, password)
      .then(() => {
        window.location.href = "dashboard.html";
      })
      .catch((error) => {
        document.getElementById("login-error").textContent = error.message;
      });
  });
}

// Dashboard logic
auth.onAuthStateChanged((user) => {
  if (!user) return;

  const userPointsDisplay = document.getElementById("user-points");
  if (userPointsDisplay) {
    db.collection("users").doc(user.uid).get().then((doc) => {
      if (doc.exists) {
        userPointsDisplay.textContent = `Your Points: ${doc.data().points}`;
      }
    });
  }

  // Withdraw handler
  const withdrawButton = document.getElementById("withdraw-button");
  if (withdrawButton) {
    withdrawButton.addEventListener("click", () => {
      db.collection("users").doc(user.uid).get().then((doc) => {
        const userData = doc.data();
        if (userData.points >= 10000) {
          const remainingPoints = userData.points - 10000;

          // Send withdrawal email
          emailjs.send(EMAILJS_SERVICE_ID, EMAILJS_TEMPLATE_ID, {
            user_email: user.email,
            remaining_points: remainingPoints,
            time: new Date().toLocaleString()
          }, EMAILJS_PUBLIC_KEY).then(() => {
            alert("Withdrawal request sent successfully!");
            db.collection("users").doc(user.uid).update({
              points: remainingPoints
            });
          }).catch((err) => {
            alert("Failed to send withdrawal request. Please try again.");
            console.error(err);
          });

        } else {
          alert("You need at least 10,000 points (₦1,000) to withdraw.");
        }
      });
    });
  }
});

// Section Navigation on Dashboard
document.addEventListener("DOMContentLoaded", () => {
  const sections = ["tasks", "refer", "withdraw"];
  sections.forEach((section) => {
    const button = document.getElementById(`${section}-button`);
    if (button) {
      button.addEventListener("click", () => {
        sections.forEach((s) => {
          document.getElementById(`${s}-section`).style.display = (s === section) ? "block" : "none";
        });
      });
    }
  });
});
