document.addEventListener("DOMContentLoaded", function() {
    const saveButton = document.getElementById("saveSettings");

    saveButton.addEventListener("click", function() {
        const emailEnabled = document.getElementById("emailSwitch").checked;
        const telegramEnabled = document.getElementById("telegramSwitch").checked;
        const notifyMinutes = document.getElementById("notifyMinutes").value;

        const data = {
            email_enabled: emailEnabled,
            telegram_enabled: telegramEnabled,
            notify_minutes: notifyMinutes
        };

        fetch("/save_settings", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (response.ok) {
                window.location.href = "/settings";
            } else {
                alert("Ошибка сохранения настроек!");
            }
        })
        .catch(error => {
            console.error("Ошибка:", error);
            alert("Ошибка соединения с сервером!");
        });
    });
});