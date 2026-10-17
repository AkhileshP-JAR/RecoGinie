const BASE_URL = 'http://127.0.0.1:8000/api';

document.addEventListener('DOMContentLoaded', () => {
    const loadProfileBtn = document.getElementById('loadProfileBtn');
    const sendBtn = document.getElementById('sendBtn');
    const getRecsBtn = document.getElementById('getRecsBtn');
    const chatInput = document.getElementById('chatInput');
    const messagesContainer = document.getElementById('messagesContainer');

    // Load Profile
    loadProfileBtn.addEventListener('click', async () => {
        const userId = document.getElementById('userIdInput').value;
        try {
            const res = await fetch(`${BASE_URL}/profile/${userId}`);
            const data = await res.json();
            document.getElementById('userPreferences').textContent = data.preferences || "No specific preferences.";
            // Also store for editing
            document.getElementById('userPreferences').dataset.rawPrefs = data.preferences || "";
        } catch (e) {
            console.error(e);
        }
    });

    // Edit Preferences Logic
    const editPrefBtn = document.getElementById('editPrefBtn');
    const savePrefBtn = document.getElementById('savePrefBtn');
    const cancelPrefBtn = document.getElementById('cancelPrefBtn');
    const prefSpan = document.getElementById('userPreferences');
    const prefInput = document.getElementById('editPreferencesInput');

    editPrefBtn.addEventListener('click', () => {
        let currentText = "";
        if (prefSpan.dataset.rawPrefs !== undefined) {
            currentText = prefSpan.dataset.rawPrefs;
        } else {
            let spanText = prefSpan.textContent;
            if (spanText !== "No preferences yet. Start chatting!") {
                currentText = spanText;
            }
        }

        prefInput.value = currentText;
        prefSpan.style.display = 'none';
        prefInput.style.display = 'block';
        editPrefBtn.style.display = 'none';
        savePrefBtn.style.display = 'inline-block';
        cancelPrefBtn.style.display = 'inline-block';
    });

    cancelPrefBtn.addEventListener('click', () => {
        prefSpan.style.display = 'inline';
        prefInput.style.display = 'none';
        editPrefBtn.style.display = 'inline-block';
        savePrefBtn.style.display = 'none';
        cancelPrefBtn.style.display = 'none';
    });

    savePrefBtn.addEventListener('click', async () => {
        const userId = document.getElementById('userIdInput').value;
        const newPrefs = prefInput.value.trim();
        try {
            const res = await fetch(`${BASE_URL}/profile`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: userId, preferences: newPrefs })
            });
            if (res.ok) {
                // Return to view mode and reload
                cancelPrefBtn.click();
                loadProfileBtn.click();
                getRecsBtn.click(); // Auto refresh recs
            }
        } catch (e) {
            console.error("Error saving preferences", e);
        }
    });

    // Send Chat
    const sendMessage = async () => {
        const text = chatInput.value.trim();
        const userId = document.getElementById('userIdInput').value;
        if (!text) return;

        // User Message
        appendMessage('user', text);
        chatInput.value = '';

        try {
            const res = await fetch(`${BASE_URL}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: userId, message: text })
            });
            const data = await res.json();
            appendMessage('system', data.reply);

            // Auto reload profile to show updated likes
            loadProfileBtn.click();
        } catch (e) {
            appendMessage('system', 'Error connecting to AI backend.');
        }
    };

    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    // Get Static Recommendations (Sidebar)
    getRecsBtn.addEventListener('click', async () => {
        const userId = document.getElementById('userIdInput').value;
        const recList = document.getElementById('recsList');
        recList.innerHTML = '<p class="placeholder-text">Loading...</p>';
        try {
            const res = await fetch(`${BASE_URL}/recommend`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: userId })
            });
            const data = await res.json();
            recList.innerHTML = '';
            data.recommendations.forEach(movie => {
                const card = document.createElement('div');
                card.className = 'movie-card';
                card.innerHTML = `
                    <div class="movie-title">${movie.title}</div>
                    <div class="movie-genres">${movie.genres.join(', ')}</div>
                `;
                recList.appendChild(card);
            });
            if (data.recommendations.length === 0) {
                recList.innerHTML = '<p class="placeholder-text">No recommendations found.</p>';
            }
        } catch (e) {
            recList.innerHTML = '<p class="placeholder-text">Failed to fetch list.</p>';
        }
    });

    function appendMessage(sender, text) {
        const el = document.createElement('div');
        el.className = `message ${sender}`;
        el.innerHTML = `<div class="bubble">${text}</div>`;
        messagesContainer.appendChild(el);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
});
