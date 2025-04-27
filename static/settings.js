document.addEventListener("DOMContentLoaded", function() {
    const saveButton = document.getElementById("saveSettings");

    saveButton.addEventListener("click", function() {
        const emailEnabled = document.getElementById("emailSwitch").checked;
        const telegramEnabled = document.getElementById("telegramSwitch").checked;
        const notifyMinutes = document.getElementById("notifyMinutes").value;
        const api_key = document.getElementById("apiKeyInput").value;

        const data = {
            notify_mail: emailEnabled,
            notify_tg: telegramEnabled,
            early_time: notifyMinutes,
            api_key:api_key
        };

        fetch(window.location.href , {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (response.ok) {
                alert("Настройки усепшно сохранены");
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
