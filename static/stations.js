const editButton = document.getElementById('editButton');
const locatorField = document.getElementById('locator');
const coordinatesField = document.getElementById('coordinates');
const altitudeField = document.getElementById('altitude');

editButton.addEventListener('click', function() {
    if (editButton.textContent === 'Редактировать') {
        editButton.textContent = 'Сохранить';

        locatorField.disabled = false;
        coordinatesField.disabled = false;
        altitudeField.disabled = false;
    } else if (editButton.textContent === 'Сохранить') {
        editButton.textContent = 'Редактировать';

        locatorField.disabled = true;
        coordinatesField.disabled = true;
        altitudeField.disabled = true;

        const updatedData = {
            locator: locatorField.value,
            coordinates: coordinatesField.value,
            altitude: altitudeField.value
        };

        fetch('/save_station_info', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(updatedData),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Информация успешно сохранена');
            } else {
                alert('Ошибка при сохранении информации');
            }
        });
    }
});