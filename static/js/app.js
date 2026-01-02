/* Decision-Minutes Copilot - Frontend Application */

// State
let currentJobId = null;
let currentResults = null;

// DOM Elements
const uploadSection = document.getElementById('upload-section');
const processingSection = document.getElementById('processing-section');
const resultsSection = document.getElementById('results-section');
const confirmedSection = document.getElementById('confirmed-section');
const fileInput = document.getElementById('file-input');
const dropZone = document.getElementById('drop-zone');
const fileInfo = document.getElementById('file-info');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupDragAndDrop();
    setupFileInput();
});

// Drag and Drop
function setupDragAndDrop() {
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.add('drag-over');
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.remove('drag-over');
        });
    });

    dropZone.addEventListener('drop', (e) => {
        const file = e.dataTransfer.files[0];
        if (file) handleFile(file);
    });
}

// File Input
function setupFileInput() {
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) handleFile(file);
    });
}

// Handle File Selection
function handleFile(file) {
    // Validate file type
    const validTypes = ['audio/mpeg', 'audio/wav', 'audio/x-m4a', 'audio/webm', 'audio/ogg', 'audio/flac'];
    const ext = file.name.split('.').pop().toLowerCase();
    const validExts = ['mp3', 'wav', 'm4a', 'webm', 'ogg', 'flac'];

    if (!validExts.includes(ext)) {
        alert('Invalid file type. Please upload an audio file (MP3, WAV, M4A, WebM, OGG, or FLAC).');
        return;
    }

    // Validate file size (25MB limit)
    if (file.size > 25 * 1024 * 1024) {
        alert('File too large. Maximum size is 25MB.');
        return;
    }

    // Show file info
    fileInfo.classList.remove('hidden');
    fileInfo.querySelector('.file-name').textContent = file.name;

    // Start upload
    uploadFile(file);
}

// Clear File
function clearFile() {
    fileInput.value = '';
    fileInfo.classList.add('hidden');
}

// Upload File
async function uploadFile(file) {
    showSection('processing');
    updateProgress(0, 'Uploading audio file...');

    const formData = new FormData();
    formData.append('audio', file);

    try {
        // Upload
        updateProgress(20, 'Uploading...');
        const uploadRes = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        if (!uploadRes.ok) {
            const err = await uploadRes.json();
            throw new Error(err.error || 'Upload failed');
        }

        const uploadData = await uploadRes.json();
        currentJobId = uploadData.job_id;

        // Process
        updateProgress(40, 'Transcribing audio with Whisper AI...');
        const processRes = await fetch(`/process/${currentJobId}`, {
            method: 'POST'
        });

        if (!processRes.ok) {
            const err = await processRes.json();
            throw new Error(err.error || 'Processing failed');
        }

        const processData = await processRes.json();
        updateProgress(100, 'Done!');

        // Show results
        setTimeout(() => {
            displayResults(processData);
        }, 500);

    } catch (error) {
        console.error('Error:', error);
        alert('Error: ' + error.message);
        showSection('upload');
    }
}

// Update Progress
function updateProgress(percent, message) {
    document.getElementById('progress-fill').style.width = percent + '%';
    document.getElementById('processing-message').textContent = message;

    if (percent < 40) {
        document.getElementById('processing-status').textContent = 'Uploading...';
    } else if (percent < 80) {
        document.getElementById('processing-status').textContent = 'Processing...';
    } else {
        document.getElementById('processing-status').textContent = 'Almost done!';
    }
}

// Display Results
function displayResults(data) {
    currentResults = data.results;

    // Summary
    document.getElementById('meeting-summary').textContent =
        data.results.summary || 'No summary generated.';

    // Decisions
    const decisionsBlock = document.getElementById('decisions-block');
    const decisionsList = document.getElementById('decisions-list');
    decisionsList.innerHTML = '';

    if (data.results.decisions && data.results.decisions.length > 0) {
        decisionsBlock.classList.remove('hidden');
        data.results.decisions.forEach(d => {
            const li = document.createElement('li');
            li.textContent = d.description;
            decisionsList.appendChild(li);
        });
    } else {
        decisionsBlock.classList.add('hidden');
    }

    // Action Items
    const tbody = document.getElementById('action-items-body');
    tbody.innerHTML = '';

    if (data.results.action_items && data.results.action_items.length > 0) {
        data.results.action_items.forEach((item, index) => {
            const tr = document.createElement('tr');
            const confidence = item.confidence || 0;
            const confClass = confidence >= 0.8 ? 'high' : confidence >= 0.6 ? 'medium' : 'low';

            tr.innerHTML = `
                <td>${index + 1}</td>
                <td>${escapeHtml(item.description)}</td>
                <td>${escapeHtml(item.owner || '-')}</td>
                <td>${escapeHtml(item.deadline || '-')}</td>
                <td>
                    <span class="confidence-badge confidence-${confClass}">
                        ${Math.round(confidence * 100)}%
                    </span>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } else {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--text-muted)">No action items found</td></tr>';
    }

    // Transcript
    document.getElementById('transcript-text').textContent = data.transcript || 'No transcript available.';

    showSection('results');
}

// Escape HTML
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Toggle Transcript
function toggleTranscript() {
    const content = document.getElementById('transcript-content');
    const icon = document.getElementById('transcript-toggle-icon');

    if (content.classList.contains('hidden')) {
        content.classList.remove('hidden');
        icon.textContent = '▼';
    } else {
        content.classList.add('hidden');
        icon.textContent = '▶';
    }
}

// Confirm Results
async function confirmResults() {
    if (!currentJobId) return;

    try {
        const res = await fetch(`/confirm/${currentJobId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ results: currentResults })
        });

        if (!res.ok) {
            throw new Error('Confirmation failed');
        }

        showSection('confirmed');

    } catch (error) {
        alert('Error confirming: ' + error.message);
    }
}

// Export Markdown
async function exportMarkdown() {
    if (!currentJobId) return;

    try {
        const res = await fetch(`/export/${currentJobId}`);
        const data = await res.json();

        // Download as file
        const blob = new Blob([data.markdown], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `meeting-minutes-${data.filename.split('.')[0]}.md`;
        a.click();
        URL.revokeObjectURL(url);

    } catch (error) {
        alert('Export failed: ' + error.message);
    }
}

// Copy to Clipboard
async function copyToClipboard() {
    if (!currentJobId) return;

    try {
        const res = await fetch(`/export/${currentJobId}`);
        const data = await res.json();

        await navigator.clipboard.writeText(data.markdown);

        // Show feedback
        const btn = event.target;
        const originalText = btn.textContent;
        btn.textContent = '✓ Copied!';
        setTimeout(() => btn.textContent = originalText, 2000);

    } catch (error) {
        alert('Copy failed: ' + error.message);
    }
}

// Reset App
function resetApp() {
    currentJobId = null;
    currentResults = null;
    clearFile();
    document.getElementById('progress-fill').style.width = '0%';
    showSection('upload');
}

// Show Section
function showSection(section) {
    uploadSection.classList.add('hidden');
    processingSection.classList.add('hidden');
    resultsSection.classList.add('hidden');
    confirmedSection.classList.add('hidden');

    switch (section) {
        case 'upload':
            uploadSection.classList.remove('hidden');
            break;
        case 'processing':
            processingSection.classList.remove('hidden');
            break;
        case 'results':
            resultsSection.classList.remove('hidden');
            break;
        case 'confirmed':
            confirmedSection.classList.remove('hidden');
            break;
    }
}
