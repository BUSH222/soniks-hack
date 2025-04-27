document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.getElementById('sidebar');
    let draggedElement = null;

    // Add dragstart and dragend event listeners to panels
    sidebar.addEventListener('dragstart', (event) => {
        draggedElement = event.target;
        event.target.style.opacity = '0.5';
    });

    sidebar.addEventListener('dragend', (event) => {
        event.target.style.opacity = '';
        draggedElement = null;
    });

    // Add dragover and drop event listeners to the sidebar
    sidebar.addEventListener('dragover', (event) => {
        event.preventDefault(); // Allow dropping
        const afterElement = getDragAfterElement(sidebar, event.clientY);
        const draggable = document.querySelector('.dragging');
        if (afterElement == null) {
            sidebar.appendChild(draggedElement);
        } else {
            sidebar.insertBefore(draggedElement, afterElement);
        }
    });

    sidebar.addEventListener('drop', (event) => {
        event.preventDefault();
    });

    // Helper function to determine the element after which the dragged element should be inserted
    function getDragAfterElement(container, y) {
        const draggableElements = [...container.querySelectorAll('.panel:not(.dragging)')];

        return draggableElements.reduce(
            (closest, child) => {
                const box = child.getBoundingClientRect();
                const offset = y - box.top - box.height / 2;
                if (offset < 0 && offset > closest.offset) {
                    return { offset: offset, element: child };
                } else {
                    return closest;
                }
            },
            { offset: Number.NEGATIVE_INFINITY }
        ).element;
    }

    // Add event listener to the "Stop SDR" button
    const stopSDRButton = document.getElementById('stopSDR');
    stopSDRButton.addEventListener('click', () => {
        fetch('/stop_sdr')
            .then(response => response.text())
            .then(data => {
                alert(`Response from server: ${data}`);
            })
            .catch(error => {
                alert(`Error: ${error}`);
            });
    });

    const setFrequencyButton = document.getElementById('setFrequency');
    setFrequencyButton.addEventListener('click', () => {
        const frequency = document.getElementById('mhzAmount').value;
        fetch(`/change_freq?frequency=${encodeURIComponent(parseFloat(frequency)*1000000)}`)
            .then(response => response.text())
            .then(data => {
                alert(`Response from server: ${data}`);
            })
            .catch(error => {
                alert(`Error: ${error}`);
            });
    });
});