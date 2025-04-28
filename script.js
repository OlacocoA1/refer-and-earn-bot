// =============== General Site Scripts ===============

// Example Login Function (Replace with real backend later)
function loginUser(event) {
    event.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    if (email && password) {
        alert('Login successful!');
        window.location.href = "dashboard.html"; // Redirect to dashboard
    } else {
        alert('Please fill in all fields.');
    }
}

// Example Register Function (Replace with real backend later)
function registerUser(event) {
    event.preventDefault();
    const email = document.getElementById('register-email').value;
    const username = document.getElementById('register-username').value;
    const password = document.getElementById('register-password').value;

    if (email && username && password) {
        alert('Registration successful!');
        window.location.href = "dashboard.html"; // Redirect to dashboard
    } else {
        alert('Please fill in all fields.');
    }
}

// Paystack Payment Integration
function payWithPaystack() {
    var handler = PaystackPop.setup({
        key: 'pk_live_b5fa4e730d9baa38f7ff012ad4d263d5d3459c5b', // Paystack public key
        email: 'user@example.com',
        amount: 50000, // 500 NGN
        currency: "NGN",
        callback: function(response) {
            alert('Payment complete! Reference: ' + response.reference);
            // Here you can verify payment on server if you want
        },
        onClose: function() {
            alert('Transaction was not completed, window closed.');
        }
    });
    handler.openIframe();
}

// =============== CPX Research Integration ===============

const script1 = {
    div_id: "fullscreen",
    theme_style: 1,
    order_by: 2,
    limit_surveys: 7
};

const config = {
    general_config: {
        app_id: 1234567, // replace with your actual app ID
        ext_user_id: "user123",
        email: "",
        username: "",
        secure_hash: "",
        subid_1: "",
        subid_2: "",
    },
    style_config: {
        text_color: "#2b2b2b",
        survey_box: {
            topbar_background_color: "#ffaf20",
            box_background_color: "white",
            rounded_borders: true,
            stars_filled: "black",
        },
    },
    script_config: [script1],
    debug: false,
    useIFrame: true,
    iFramePosition: 1,
    functions: {
        no_surveys_available: () => {
            console.log("No surveys available");
        },
        count_new_surveys: (countsurveys) => {
            console.log("New surveys count:", countsurveys);
        },
        get_all_surveys: (surveys) => {
            console.log("Survey list:", surveys);
        },
        get_transaction: (transactions) => {
            console.log("Transactions:", transactions);
        }
    }
};

window.config = config;

// =============== Adstera Integration ===============

// This Adstera script automatically loads from their server
var adsteraScript = document.createElement('script');
adsteraScript.type = 'text/javascript';
adsteraScript.src = '//pl16213274.profitableratecpm.com/97/df/7b/97df7bff03132071f1f31973f5ddc233.js';
document.head.appendChild(adsteraScript);

// =============== Dashboard Logic ===============

// Example dashboard logic (simple task selection)
function completeTask(taskId) {
    alert("Task " + taskId + " completed! Earnings added to your balance.");
    // You would normally also update this in your database/server
}

// Example for handling payment
document.addEventListener('DOMContentLoaded', function () {
    const payButton = document.getElementById('paystack-btn');
    if (payButton) {
        payButton.addEventListener('click', payWithPaystack);
    }
});