document.addEventListener('DOMContentLoaded', function () {
    const rows = document.querySelectorAll('table tbody tr');
    rows.forEach(row => {
        row.addEventListener('click', function () {
            const stationId = row.dataset.stationId;
            window.location.href = `/stations/${stationId}`;
        });
    });
});