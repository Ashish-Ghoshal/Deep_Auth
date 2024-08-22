// Element selectors for handling UI interactions
const textFields = document.querySelectorAll("input");
const passwordField = document.querySelector('.pwd-input');
const togglePasswordBtn = document.querySelector('.toggle-pwd-btn');
const switchToSignUpBtn = document.querySelector('.switch-sign-up');
const switchToSignInBtn = document.querySelector('.switch-sign-in');
const signUpFormContainer = document.querySelector('.sign-up-container');
const signInFormContainer = document.querySelector('.sign-in-container');

// Function to handle focus events on input fields
textFields.forEach(inputField => {
    inputField.addEventListener("focus", () => highlightParentContainer(inputField));
    inputField.addEventListener("blur", () => removeHighlightFromContainer(inputField));
});

// Highlight the parent container when the input field is focused
function highlightParentContainer(field) {
    let parentDiv = field.parentNode;
    parentDiv.classList.add("active");
}

// Remove highlight when the input field loses focus
function removeHighlightFromContainer(field) {
    let parentDiv = field.parentNode;
    parentDiv.classList.remove("active");
}

// Toggle password visibility in the password field
togglePasswordBtn.addEventListener("click", togglePasswordVisibility);

// Toggles between showing and hiding the password
function togglePasswordVisibility() {
    if (passwordField.type === 'password') {
        passwordField.type = 'text';
        togglePasswordBtn.innerHTML = "<i class='icon-eye-open'></i>";
    } else {
        passwordField.type = 'password';
        togglePasswordBtn.innerHTML = "<i class='icon-eye-close'></i>";
    }
}

// Switch to the sign-up form
switchToSignUpBtn.addEventListener("click", displaySignUpForm);

// Displays the sign-up form and hides the sign-in form
function displaySignUpForm() {
    signInFormContainer.classList.add('hide');
    signUpFormContainer.classList.add('show');
    signInFormContainer.classList.remove('show');
}

// Switch to the sign-in form
switchToSignInBtn.addEventListener("click", displaySignInForm);

// Displays the sign-in form and hides the sign-up form
function displaySignInForm() {
    signInFormContainer.classList.remove('hide');
    signUpFormContainer.classList.remove('show');
    signInFormContainer.classList.add('show');
}

// Handle error messages based on the status code
const errorMsgElement = document.querySelector('#error-message');
const statusCodeElement = document.querySelector('#status-code');
if (statusCodeElement && statusCodeElement.value == 404) {
    displayErrorMessage(errorMsgElement.value);
}

// Displays an error message using an alert
function displayErrorMessage(message) {
    swal("Oops!", message, "error");
}
