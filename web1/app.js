const API_URL =
    window.location.hostname === "localhost" && window.location.port === "8080"
        ? "http://localhost:5050/story"
        : "/story";
const WORD_LIMIT = 500;

function escapeHtml(text) {
    return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

function getWordCount(text) {
    const trimmed = text.trim();
    return trimmed ? trimmed.split(/\s+/).length : 0;
}

function updateWordCount() {
    const contentInput = document.getElementById("content");
    const wordCount = document.getElementById("word-count");
    const count = getWordCount(contentInput.value);

    wordCount.textContent = `${count} / ${WORD_LIMIT} words`;
    wordCount.className = count > WORD_LIMIT ? "count-error" : "count-ok";
}

function renderStories(stories) {
    const list = document.getElementById("story-list");
    if (!stories.length) {
        list.innerHTML = '<p class="empty-state">No stories yet. Be the first to publish one.</p>';
        return;
    }

    const ordered = [...stories].reverse();
    list.innerHTML = ordered
        .map(
            (s, index) => `
            <article class="story reveal" style="animation-delay:${index * 80}ms">
                <h3>${escapeHtml(s.title)}</h3>
                <p>${escapeHtml(s.content)}</p>
            </article>
        `
        )
        .join("");
}

async function loadStories() {
    const list = document.getElementById("story-list");
    try {
        const response = await fetch(API_URL);
        if (!response.ok) {
            throw new Error("Failed to fetch stories");
        }
        const stories = await response.json();
        renderStories(Array.isArray(stories) ? stories : []);
    } catch (_error) {
        list.innerHTML = '<p class="empty-state">Could not load stories right now.</p>';
    }
}

async function submitStory(event) {
    event.preventDefault();

    const titleInput = document.getElementById("title");
    const contentInput = document.getElementById("content");
    const status = document.getElementById("form-status");

    const title = titleInput.value.trim();
    const content = contentInput.value.trim();
    const words = getWordCount(content);

    if (!title || !content) {
        status.textContent = "Please fill in both title and story.";
        status.className = "status-error";
        return;
    }

    if (words > WORD_LIMIT) {
        status.textContent = `Please keep your story within ${WORD_LIMIT} words.`;
        status.className = "status-error";
        return;
    }

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title, content })
        });

        if (!response.ok) {
            throw new Error("Failed to save story");
        }

        titleInput.value = "";
        contentInput.value = "";
        updateWordCount();
        status.textContent = "Story published successfully.";
        status.className = "status-success";
        await loadStories();
    } catch (_error) {
        status.textContent = "Could not save your story. Try again.";
        status.className = "status-error";
    }
}

document.getElementById("content").addEventListener("input", updateWordCount);
document.getElementById("story-form").addEventListener("submit", submitStory);
updateWordCount();
loadStories();
