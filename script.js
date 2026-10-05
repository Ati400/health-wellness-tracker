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