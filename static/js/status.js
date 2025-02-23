function fetchPumpStatus() {
    fetch("/pump_status")  // Endpoint that returns the pump's current status
        .then(response => {
            if (!response.ok) {
                throw new Error("Failed to fetch pump status");
            }
            return response.json();
        })
        .then(status => {
            if (status.error) {
                updatePumpStatus("error");
            } else if (status.paused) {
                updatePumpStatus("paused");
            } else if (status.running) {
                updatePumpStatus("running");
            } else if (status.enabled) {
                updatePumpStatus("enabled");
            }
        })
        .catch(err => {
            console.error("Error fetching pump status:", err);
            updatePumpStatus("error"); // Default to error if fetch fails
        });
}

// Poll the backend every second to update the status
setInterval(fetchPumpStatus, 1000);
