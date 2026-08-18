const headlineInput = document.getElementById("headlineInput");
const generateBtn = document.getElementById("generateBtn");
const copyBtn = document.getElementById("copyBtn");
const resetBtn = document.getElementById("resetBtn");
const statusText = document.getElementById("statusText");
const errorText = document.getElementById("errorText");
const outputBox = document.getElementById("outputBox");
const loadingBadge = document.getElementById("loadingBadge");

const initialOutput = `
  <div class="empty-state">
    <div class="empty-icon">AI</div>
    <p class="empty-title">Your generated news article will appear here.</p>
    <p class="empty-copy">Enter a headline, generate the article, and review the draft in this panel.</p>
  </div>
`;

let currentArticleText = "";
let currentCopyConfirmation = null;

function escapeHtml(value) {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function setLoadingState(isLoading) {
  generateBtn.disabled = isLoading;
  copyBtn.disabled = isLoading || !currentArticleText;
  resetBtn.disabled = isLoading;
  headlineInput.disabled = isLoading;
  loadingBadge.hidden = !isLoading;

  if (isLoading) {
    generateBtn.textContent = "Generating...";
    outputBox.innerHTML = `
      <div class="loading-frame" aria-label="Generating article">
        <div class="skeleton-line title"></div>
        <div class="skeleton-line body"></div>
        <div class="skeleton-line body"></div>
        <div class="skeleton-line body"></div>
        <div class="skeleton-line body"></div>
      </div>
    `;
  } else {
    generateBtn.textContent = "Generate Article";
  }
}

function clearMessages() {
  errorText.textContent = "";
  statusText.textContent = "";
}

function showError(message) {
  errorText.textContent = message;
}

function showEmptyState() {
  currentArticleText = "";
  currentCopyConfirmation = null;
  outputBox.className = "output-box output-empty";
  outputBox.innerHTML = initialOutput;
  copyBtn.disabled = true;
}

async function copyCurrentArticle() {
  if (!currentArticleText) {
    return;
  }

  try {
    await navigator.clipboard.writeText(currentArticleText);

    if (currentCopyConfirmation) {
      currentCopyConfirmation.textContent = "Article copied to clipboard.";
    } else {
      statusText.textContent = "Article copied to clipboard.";
    }
  } catch {
    showError("Copying is unavailable in this browser.");
  }
}

function getArticleDisplayText(articleText) {
  const headlineMarker = "News article:";
  const markerIndex = articleText.toLowerCase().indexOf(headlineMarker.toLowerCase());

  if (markerIndex === -1) {
    return {
      headline: headlineInput.value.trim(),
      body: articleText.trim(),
    };
  }

  return {
    headline: headlineInput.value.trim(),
    body: articleText.slice(markerIndex + headlineMarker.length).trim() || articleText.trim(),
  };
}

function buildParagraphs(articleText) {
  const cleanedText = articleText.replace(/\r/g, "").trim();

  return cleanedText
    .split(/\n{2,}/)
    .map((paragraph) => paragraph.replace(/\n/g, " ").trim())
    .filter(Boolean)
    .map((paragraph) => `<p>${escapeHtml(paragraph)}</p>`)
    .join("");
}

function renderArticle(articleText) {
  currentArticleText = articleText.trim();
  const articleDisplay = getArticleDisplayText(articleText);
  const bodyHtml = buildParagraphs(articleDisplay.body);

  outputBox.className = "output-box";
  outputBox.innerHTML = `
    <article class="generated-card">
      <div class="generated-meta">
        <span class="generated-tag">HuggingFace DistilGPT-2</span>
        <span class="generated-tag">News Draft</span>
        <span class="generated-tag">Auto Generated</span>
      </div>
      <h3 class="generated-headline">${escapeHtml(articleDisplay.headline)}</h3>
      <div class="generated-body">${bodyHtml}</div>
      <div class="generated-actions">
        <button id="inlineCopyBtn" class="secondary-btn" type="button">Copy Article</button>
      </div>
      <p id="copyConfirmation" class="copy-confirmation" aria-live="polite"></p>
    </article>
  `;

  copyBtn.disabled = false;

  const inlineCopyBtn = document.getElementById("inlineCopyBtn");
  const copyConfirmation = document.getElementById("copyConfirmation");
  currentCopyConfirmation = copyConfirmation;

  inlineCopyBtn.addEventListener("click", copyCurrentArticle);
}

function resetInterface() {
  headlineInput.value = "";
  headlineInput.disabled = false;
  currentArticleText = "";
  clearMessages();
  generateBtn.disabled = false;
  generateBtn.textContent = "Generate Article";
  copyBtn.disabled = true;
  resetBtn.disabled = false;
  loadingBadge.hidden = true;
  showEmptyState();
  headlineInput.focus();
}

async function generateArticle() {
  const headline = headlineInput.value.trim();
  clearMessages();

  if (!headline) {
    showError("Please enter a news headline or topic before generating.");
    return;
  }

  setLoadingState(true);
  statusText.textContent = "Generating a newsroom-style article draft...";

  try {
    const response = await fetch("http://127.0.0.1:5000/generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ headline }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Unable to generate article.");
    }

    renderArticle(data.generated_article);
    statusText.textContent = "Article generated successfully.";
  } catch (error) {
    showEmptyState();
    showError(error.message || "Something went wrong while generating the article.");
  } finally {
    setLoadingState(false);
  }
}

generateBtn.addEventListener("click", generateArticle);
copyBtn.addEventListener("click", async () => {
  await copyCurrentArticle();
});

resetBtn.addEventListener("click", resetInterface);

showEmptyState();
