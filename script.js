// JavaScript for the Health and Wellness Tracker

// --------------------------------
// DASHBOARD WELCOME MESSAGE
// --------------------------------

// Find the welcome message
const welcomeMessage =
    document.getElementById("welcomeMessage");


// Only run this code on the dashboard
if (welcomeMessage) {

    // Ask the backend for the logged-in user's information
    fetch("/user")

        // Change the response into JSON data
        .then(response => response.json())

        .then(data => {

            // Make sure we received a name
            if (data.name) {

                // Show the user's name
                welcomeMessage.textContent =
                    "Welcome, " + data.name + "!";

            }

        });

}

// --------------------------------
// PROFILE INFORMATION
// --------------------------------

// Find the profile information
const profileName =
    document.getElementById("profileName");

const profileEmail =
    document.getElementById("profileEmail");


// Only run this code on the profile page
if (profileName && profileEmail) {

    // Ask the backend for the user's information
    fetch("/user")

        .then(response => response.json())

        .then(data => {

            // Show the user's name
            profileName.textContent =
                data.name;

            // Show the user's email
            profileEmail.textContent =
                data.email;

        });

}

// --------------------------------
// LOGOUT
// --------------------------------

// Find the logout button
const logoutButton =
    document.getElementById("logoutButton");


// Only run if a logout button exists
if (logoutButton) {

    logoutButton.addEventListener(
        "click",
        function() {

            // Send the user to the logout route
            window.location.href = "/logout";

        }
    );

}

// --------------------------------
// PAGE MESSAGES
// --------------------------------

// Read information from the page address
const pageUrl =
    new URLSearchParams(window.location.search);


// Find our message elements
const loginError =
    document.getElementById("loginError");

const accountCreated =
    document.getElementById("accountCreated");

const emailError =
    document.getElementById("emailError");


// Show incorrect login message
if (
    pageUrl.get("error") === "1"
    && loginError
) {

    loginError.style.display = "block";

}


// Show account created message
if (
    pageUrl.get("created") === "1"
    && accountCreated
) {

    accountCreated.style.display = "block";

}


// Show duplicate email message
if (
    pageUrl.get("error") === "email"
    && emailError
) {

    emailError.style.display = "block";

}