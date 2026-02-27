// Global state
let statusUpdateInterval = null;

/**
 * Initialize the application
 */
function initializeApp() {
    console.log('Initializing News Auto Collector UI');
    updateStatus();
    statusUpdateInterval = setInterval(updateStatus, 500);
}

/**
 * Update status from server
 */
function updateStatus() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => updateUI(data))
        .catch(error => {
            console.error('Error fetching status:', error);
            showError('Failed to connect to server');
        });
}

/**
 * Update UI based on status
 */
function updateUI(status) {
    // Update status text
    const statusMap = {
        'idle': '🟢 Ready',
        'initializing': '🟡 Initializing...',
        'fetching_data': '🟡 Fetching Data...',
        'searching': '🟡 Searching...',
        'deduplicating': '🟡 Deduplicating...',
        'exporting': '🟡 Exporting...',
        'complete': '✅ Complete',
        'error': '❌ Error'
    };

    const statusText = document.getElementById('statusText');
    statusText.textContent = statusMap[status.status] || status.status;
    statusText.className = `value status-${status.status}`;

    // Update progress bar
    const progressBar = document.getElementById('progressBar');
    const progressPercent = document.getElementById('progressPercent');
    progressBar.style.width = status.progress + '%';
    progressPercent.textContent = status.progress + '%';

    // Update message
    const messageText = document.getElementById('messageText');
    messageText.textContent = status.message || 'Ready to start';

    // Update button states
    const runBtn = document.getElementById('runBtn');
    const resetBtn = document.getElementById('resetBtn');

    runBtn.disabled = status.running || status.status === 'complete';
    resetBtn.disabled = status.running;

    // Handle completion
    if (status.status === 'complete' && status.doc_url) {
        showResults(status.doc_url);
        clearInterval(statusUpdateInterval);
    }

    // Handle errors
    if (status.status === 'error' && status.error) {
        showError(status.error);
        clearInterval(statusUpdateInterval);
    }
}

/**
 * Start collection
 */
function startCollection() {
    const runBtn = document.getElementById('runBtn');
    runBtn.disabled = true;

    // Clear previous results
    document.getElementById('resultsContent').innerHTML =
        '<p class="placeholder">Results will appear here after completion</p>';
    document.getElementById('errorSection').style.display = 'none';

    // Send request
    fetch('/api/run', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Collection started');
                // Resume polling
                if (statusUpdateInterval) clearInterval(statusUpdateInterval);
                statusUpdateInterval = setInterval(updateStatus, 500);
            } else {
                showError(data.message || 'Failed to start collection');
                runBtn.disabled = false;
            }
        })
        .catch(error => {
            console.error('Error starting collection:', error);
            showError('Failed to start collection: ' + error.message);
            runBtn.disabled = false;
        });
}

/**
 * Reset status
 */
function resetStatus() {
    if (confirm('Are you sure you want to reset the status?')) {
        fetch('/api/reset', {
            method: 'POST'
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('statusText').textContent = '🟢 Ready';
                    document.getElementById('progressBar').style.width = '0%';
                    document.getElementById('progressPercent').textContent = '0%';
                    document.getElementById('messageText').textContent = 'Ready to start';
                    document.getElementById('resultsContent').innerHTML =
                        '<p class="placeholder">Results will appear here after completion</p>';
                    document.getElementById('errorSection').style.display = 'none';
                    document.getElementById('runBtn').disabled = false;
                    console.log('Status reset');
                }
            })
            .catch(error => {
                console.error('Error resetting status:', error);
                showError('Failed to reset status');
            });
    }
}

/**
 * Show results
 */
function showResults(docUrl) {
    const resultsContent = document.getElementById('resultsContent');
    resultsContent.innerHTML = `
        <div class="result-item">
            <span class="result-label">✅ Collection Successful!</span>
            <span class="result-value">
                Google Document created and saved.
            </span>
        </div>
        <div class="result-item">
            <span class="result-label">📄 Document Link</span>
            <span class="result-value">
                <a href="${docUrl}" target="_blank" rel="noopener noreferrer">
                    Open Document ↗
                </a>
            </span>
        </div>
        <div class="result-item">
            <span class="result-label">📋 What's in the Document?</span>
            <span class="result-value">
                • Article titles with clickable links<br>
                • Website source information<br>
                • Article summaries<br>
                • Organized by language (English/Hindi)<br>
                • Automatic duplicate removal applied
            </span>
        </div>
    `;
}

/**
 * Show error
 */
function showError(errorMessage) {
    const errorSection = document.getElementById('errorSection');
    const errorText = document.getElementById('errorText');

    errorText.textContent = errorMessage;
    errorSection.style.display = 'block';

    // Scroll to error
    errorSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initializeApp);

// Clean up interval on page unload
window.addEventListener('beforeunload', () => {
    if (statusUpdateInterval) {
        clearInterval(statusUpdateInterval);
    }
});
