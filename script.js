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
registerForm.addEventListener("submit", function (e) {
  e.preventDefault();
  const email = document.getElementById("register-email").value;
  const password = document.getElementById("register-password").value;
  const referralCodeInput = document.getElementById("referral-code").value.trim();

  const userReferralCode = generateReferralCode();

  auth.createUserWithEmailAndPassword(email, password)
    .then((userCredential) => {
      const user = userCredential.user;

      // Save user data with referral information
      db.collection("users").doc(user.uid).set({
        email: email,
        points: 0,
        referralCode: userReferralCode,
        referredBy: referralCodeInput || null
      })
      .then(() => {
        // If referral code is provided, update referrer's points
        if (referralCodeInput) {
          db.collection("users").where("referralCode", "==", referralCodeInput).get()
            .then((querySnapshot) => {
              querySnapshot.forEach((doc) => {
                const referrer = doc.id;
                // Add 10% of the referred user's points to the referrer
                db.collection("users").doc(referrer).update({
                  points: firebase.firestore.FieldValue.increment(10) // Assuming referred user gets points later
                });
              });
            })
            .catch((error) => {
              console.error("Error updating referrer points: ", error);
            });
        }
        alert("Account Created Successfully! You can now log in.");
        window.location.href = "index.html";
      })
      .catch((error) => {
        document.getElementById("register-error").textContent = error.message;
      });
    })
    .catch((error) => {
      document.getElementById("register-error").textContent = error.message;
    });
});

// Login Form Handler
const loginForm = document.getElementById("login-form");
loginForm.addEventListener("submit", function (e) {
  e.preventDefault();
  const email = document.getElementById("login-email").value;
  const password = document.getElementById("login-password").value;

  auth.signInWithEmailAndPassword(email, password)
    .then(() => {
      window.location.href = "dashboard.html"; // Redirect to dashboard
    })
    .catch((error) => {
      document.getElementById("login-error").textContent = error.message;
    });
});

// Dashboard: Show user points
const userPointsDisplay = document.getElementById("user-points");
auth.onAuthStateChanged((user) => {
  if (user) {
    db.collection("users").doc(user.uid).get()
      .then((doc) => {
        if (doc.exists) {
          userPointsDisplay.textContent = `Your Points: ${doc.data().points}`;
        }
      });
  }
});

// Dashboard: Handle Paystack Withdrawals
const withdrawButton = document.getElementById("withdraw-button");
if (withdrawButton) {
  withdrawButton.addEventListener("click", () => {
    const user = auth.currentUser;
    if (user) {
      db.collection("users").doc(user.uid).get()
        .then((doc) => {
          const points = doc.data().points;
          if (points >= 500) {
            let handler = PaystackPop.setup({
              key: 'pk_live_b5fa4e730d9baa38f7ff012ad4d263d5d3459c5b', // Live key
              email: user.email,
              amount: points * 100, // Convert points to amount
              currency: "NGN",
              ref: 'cashchop-' + Math.floor((Math.random() * 1000000000) + 1),
              callback: function(response) {
                alert('Withdrawal successful. Reference: ' + response.reference);
                // Update user points after withdrawal
                db.collection("users").doc(user.uid).update({
                  points: 0 // Reset points after withdrawal
                });
              },
              onClose: function() {
                alert('Transaction not completed.');
              }
            });
            handler.openIframe();
          } else {
            alert('You need at least 500 points to withdraw.');
          }
        })
        .catch((error) => {
          console.error("Error fetching user points: ", error);
        });
    } else {
      alert('Please log in to withdraw.');
    }
  });
                                    }
