// --- Exporter Logic ---
const exportBtn = document.getElementById('export-btn');
const urlInput = document.getElementById('playlist-url');
const statusEl = document.getElementById('status');

// Use a relative path for the API endpoint
const API_ENDPOINT = '/api/export';

exportBtn.addEventListener('click', async () => {
    const playlistUrl = urlInput.value.trim();
    if (!playlistUrl) {
        statusEl.textContent = 'Please enter a YouTube playlist URL.';
        statusEl.style.color = '#f87171'; // red-400
        return;
    }

    statusEl.textContent = 'Processing... This may take a moment for large playlists.';
    statusEl.style.color = '#60a5fa'; // blue-400
    exportBtn.disabled = true;
    exportBtn.classList.add('opacity-50', 'cursor-not-allowed');

    try {
        const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ playlist_url: playlistUrl }),
        });

        if (!response.ok) {
            let errorMessage = `Server Error: ${response.status}`;
            try {
                // Try to get a specific error message from the JSON body
                const errorData = await response.json();
                errorMessage = errorData.error || 'An unknown server error occurred.';
            } catch (e) {
                // This catch block is crucial for handling timeouts
                if (e instanceof SyntaxError) {
                    errorMessage = "Request timed out, which can happen with very large playlists. Please try again.";
                } else {
                    errorMessage = "The server returned an unexpected response. Please check server logs.";
                }
            }
            throw new Error(errorMessage);
        }

        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = 'playlist.csv';
        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename="(.+?)"/);
            if (filenameMatch && filenameMatch.length > 1) {
                filename = filenameMatch[1];
            }
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        statusEl.textContent = 'Download started successfully!';
        statusEl.style.color = '#4ade80'; // green-400

    } catch (error) {
        statusEl.textContent = `Error: ${error.message}`;
        statusEl.style.color = '#f87171';
    } finally {
        exportBtn.disabled = false;
        exportBtn.classList.remove('opacity-50', 'cursor-not-allowed');
        setTimeout(() => { statusEl.textContent = ''; }, 8000);
    }
});

// --- Mobile Menu Logic ---
const mobileMenuButton = document.getElementById('mobile-menu-button');
const mobileMenu = document.getElementById('mobile-menu');
const openIcon = document.getElementById('menu-open-icon');
const closeIcon = document.getElementById('menu-close-icon');

mobileMenuButton.addEventListener('click', () => {
    mobileMenu.classList.toggle('hidden');
    openIcon.classList.toggle('hidden');
    closeIcon.classList.toggle('hidden');
});