function togglePasswordVisibility(id) {
    var input = document.getElementById(id);
    if (input.type === "password") {
        input.type = "text";
    } else {
        input.type = "password";
    }
}

function limitInputLength(input, maxLength) {
    if (input.value.length > maxLength) {
        input.value = input.value.slice(0, maxLength);
    }
}

document.getElementById("loginForm").addEventListener("submit", function(event) {
    event.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    console.log("Username:", username);
    
    if (!username || !password) {
        alert('Please enter both username and password.');
        return;
    }

    const formData = new FormData();
    formData.append("username", username);
    formData.append("password", password);
    
    fetch('/login', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.text())
    .then(data => {
        if (data === 'OK') {
            const path = '/users/' + username
            window.location.href = path;
        } else if (data === 'INVALID_CREDENTIALS') {
            alert('Invalid username or password');
        } else {
            alert('Unexpected error: ' + data);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('There was an error with the login. Please try again.');
    });
});
