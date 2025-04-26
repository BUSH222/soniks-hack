function togglePasswordVisibility(id) {
    var input = document.getElementById(id);
    if (input.type === "password") {
        input.type = "text";
    } else {
        input.type = "password";
    }
}

function limitInputLength(input, maxLength) {
    console.log(input.value);
    if (input.value.length > maxLength) {
        input.value = input.value.slice(0, maxLength);
    }
}

document.getElementById("loginForm").addEventListener("submit", function(event) {
    event.preventDefault();
    
    const formData = new FormData();
    formData.append("username", document.getElementById("username").value);
    formData.append("password", document.getElementById("password").value);

    fetch('/login', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.text())
    .then(data => {
        if (data === 'OK') {
            window.location.href = '/account';
        } else {
            alert('Invalid username or password');
        }
    })
    .catch(error => console.error('Error:', error));
});