import os
import json
import re

IMAGE_DIR = "brawler_images_default"
OUTPUT_HTML = "index.html"

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def pretty_name_from_filename(filename: str) -> str:
    base = os.path.splitext(filename)[0]
    base = re.sub(r"_default$", "", base, flags=re.IGNORECASE)
    base = base.replace("_", " ")
    return base.strip()


def collect_brawlers():
    if not os.path.isdir(IMAGE_DIR):
        raise SystemExit(
            f"Image directory '{IMAGE_DIR}' not found. "
            f"Make sure it's next to this script."
        )

    entries = []
    for fname in sorted(os.listdir(IMAGE_DIR)):
        ext = os.path.splitext(fname)[1].lower()
        if ext not in IMAGE_EXTS:
            continue
        name = pretty_name_from_filename(fname)
        rel_path = f"{IMAGE_DIR}/{fname}"
        entries.append({"name": name, "file": rel_path})

    if not entries:
        raise SystemExit(
            f"No images found in '{IMAGE_DIR}' with extensions: {IMAGE_EXTS}"
        )

    return entries


def generate_html(brawlers):
    data_json = json.dumps(brawlers, ensure_ascii=False, indent=2)

    # Plain triple-quoted string (NOT an f-string).
    # We concatenate data_json once into the JS.
    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Brawler Rater</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    * {
      box-sizing: border-box;
    }
    body {
      margin: 0;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #0f172a;
      color: #e5e7eb;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      padding: 16px;
    }
    .app {
      background: #020617;
      border-radius: 16px;
      padding: 24px;
      max-width: 900px;
      width: 100%;
      box-shadow: 0 20px 35px rgba(0,0,0,0.6);
    }
    h1 {
      margin-top: 0;
      margin-bottom: 4px;
      font-size: 1.6rem;
    }
    .subtitle-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
      margin-bottom: 16px;
    }
    .subtitle {
      font-size: 0.9rem;
      color: #9ca3af;
    }
    .top-controls button {
      border-radius: 999px;
      border: 1px solid #4b5563;
      background: transparent;
      color: #e5e7eb;
      font-size: 0.85rem;
      padding: 6px 12px;
      cursor: pointer;
    }
    .top-controls button:hover {
      background: #111827;
    }
    .card {
      display: flex;
      gap: 24px;
      flex-wrap: wrap;
      align-items: center;
    }
    .image-wrapper {
      flex: 0 0 260px;
      max-width: 100%;
      background: radial-gradient(circle at top, #0ea5e9, #020617);
      border-radius: 16px;
      padding: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .image-wrapper img {
      max-width: 100%;
      max-height: 320px;
      display: block;
    }
    .info {
      flex: 1;
      min-width: 220px;
    }
    .brawler-name {
      font-size: 1.4rem;
      font-weight: 600;
      margin-bottom: 8px;
    }
    .question {
      font-size: 1.05rem;
      margin-bottom: 12px;
    }
    .buttons {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 12px;
    }
    button.rate-btn {
      border: none;
      border-radius: 999px;
      padding: 8px 16px;
      cursor: pointer;
      font-size: 0.95rem;
      font-weight: 500;
      background: #1f2937;
      color: #e5e7eb;
      transition: transform 0.05s ease-out, box-shadow 0.05s ease-out, background 0.1s;
    }
    button.rate-btn:hover {
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(0,0,0,0.5);
      background: #111827;
    }
    button.rate-btn.selected {
      background: #0ea5e9;
      color: #022c22;
    }
    .progress {
      font-size: 0.85rem;
      color: #9ca3af;
      margin-bottom: 8px;
    }
    .nav-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 8px;
      font-size: 0.85rem;
      color: #9ca3af;
      gap: 8px;
      flex-wrap: wrap;
    }
    .nav-row button {
      border-radius: 999px;
      border: 1px solid #4b5563;
      background: transparent;
      color: #e5e7eb;
      font-size: 0.85rem;
      padding: 6px 12px;
      cursor: pointer;
    }
    .nav-row button:hover {
      background: #111827;
    }
    .hidden {
      display: none !important;
    }
    #resultsView {
      margin-top: 12px;
    }
    .results-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
      gap: 8px;
      flex-wrap: wrap;
    }
    .results-header h2 {
      margin: 0;
      font-size: 1.2rem;
    }
    .results-header button {
      border-radius: 999px;
      border: 1px solid #4b5563;
      background: transparent;
      color: #e5e7eb;
      font-size: 0.85rem;
      padding: 6px 12px;
      cursor: pointer;
    }
    .results-header button:hover {
      background: #111827;
    }
    .buckets {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 12px;
    }
    .bucket {
      background: #020617;
      border: 1px solid #1f2937;
      border-radius: 12px;
      padding: 8px;
    }
    .bucket-title {
      font-size: 0.95rem;
      margin-bottom: 8px;
      color: #e5e7eb;
      font-weight: 600;
    }
    .bucket-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(64px, 1fr));
      gap: 6px;
    }
    .bucket-item {
      text-align: center;
      font-size: 0.7rem;
      color: #d1d5db;
    }
    .bucket-item img {
      width: 64px;
      height: 64px;
      object-fit: contain;
      display: block;
      margin: 0 auto 4px;
    }
    .bucket-empty {
      font-size: 0.8rem;
      color: #6b7280;
      font-style: italic;
    }
    @media print {
      body {
        background: #ffffff;
        color: #000000;
        min-height: auto;
      }
      .app {
        box-shadow: none;
        max-width: 100%;
        border-radius: 0;
      }
      #ratingView {
        display: none !important;
      }
      #resultsView {
        display: block !important;
      }
    }
  </style>
</head>
<body>
  <div class="app">
    <h1>Brawler Rater</h1>
    <div class="subtitle-row">
      <div class="subtitle">
        Rate each brawler one by one. Your ratings are saved locally in this browser, and you can export/import them as JSON.
      </div>
      <div class="top-controls">
        <button id="uploadBtnTop" type="button">Load results (JSON)</button>
      </div>
    </div>

    <!-- Hidden file input (shared by top + results upload buttons) -->
    <input type="file" id="uploadInput" accept="application/json" style="display:none" />

    <div id="ratingView">
      <div class="card">
        <div class="image-wrapper">
          <img id="brawlerImage" src="" alt="Brawler" />
        </div>
        <div class="info">
          <div class="brawler-name" id="brawlerName"></div>
          <div class="question">Rate this brawler:</div>
          <div class="buttons">
            <button class="rate-btn" data-rating="Love">Love</button>
            <button class="rate-btn" data-rating="Like">Like</button>
            <button class="rate-btn" data-rating="Ok">Ok</button>
            <button class="rate-btn" data-rating="Dont like">Don't like</button>
            <button class="rate-btn" data-rating="Not familiar">Not familiar</button>
          </div>
          <div class="progress" id="progressText"></div>
          <div class="nav-row">
            <div>
              <button id="prevBtn" type="button">&larr; Previous</button>
              <button id="summaryBtn" type="button">View summary so far</button>
            </div>
            <div id="statusText"></div>
            <button id="nextBtn" type="button">Skip / Next &rarr;</button>
          </div>
        </div>
      </div>
    </div>

    <div id="resultsView" class="hidden">
      <div class="results-header">
        <h2>Results by rating</h2>
        <div style="display:flex; gap:8px; flex-wrap:wrap;">
          <button id="backToRatingBtn" type="button">Back to rating</button>
          <button id="downloadBtn" type="button">Download results (JSON)</button>
          <button id="uploadBtn" type="button">Load results (JSON)</button>
          <button id="printBtn" type="button">Print / Save as PDF</button>
          <button id="restartBtn" type="button">Start over</button>
        </div>
      </div>
      <div class="buckets" id="bucketsContainer"></div>
    </div>
  </div>

  <script>
    // Base set of brawlers from the image folder.
    const BASE_BRAWLERS = """ + data_json + """;
    let BRAWLERS = BASE_BRAWLERS.slice();

    const RATINGS_ORDER = [
      "Love",
      "Like",
      "Ok",
      "Dont like",
      "Not familiar"
    ];

    let currentIndex = 0;
    let ratings = {};

    const imgEl = document.getElementById("brawlerImage");
    const nameEl = document.getElementById("brawlerName");
    const progressEl = document.getElementById("progressText");
    const statusEl = document.getElementById("statusText");
    const ratingButtons = Array.from(document.querySelectorAll("button.rate-btn"));
    const prevBtn = document.getElementById("prevBtn");
    const nextBtn = document.getElementById("nextBtn");
    const summaryBtn = document.getElementById("summaryBtn");
    const ratingView = document.getElementById("ratingView");
    const resultsView = document.getElementById("resultsView");
    const bucketsContainer = document.getElementById("bucketsContainer");
    const downloadBtn = document.getElementById("downloadBtn");
    const uploadBtn = document.getElementById("uploadBtn");
    const uploadBtnTop = document.getElementById("uploadBtnTop");
    const uploadInput = document.getElementById("uploadInput");
    const printBtn = document.getElementById("printBtn");
    const restartBtn = document.getElementById("restartBtn");
    const backToRatingBtn = document.getElementById("backToRatingBtn");

    function loadStored() {
      try {
        const raw = window.localStorage.getItem("brawlerRatings");
        if (raw) {
          const parsed = JSON.parse(raw);
          if (parsed && typeof parsed === "object") {
            ratings = parsed;
          }
        }
      } catch (e) {
        console.warn("Failed to load stored ratings:", e);
      }

      try {
        const idxRaw = window.localStorage.getItem("brawlerCurrentIndex");
        if (idxRaw !== null) {
          const idx = parseInt(idxRaw, 10);
          if (!Number.isNaN(idx) && idx >= 0 && idx < BRAWLERS.length) {
            currentIndex = idx;
          }
        }
      } catch (e) {
        console.warn("Failed to load stored index:", e);
      }
    }

    function saveStored() {
      try {
        window.localStorage.setItem("brawlerRatings", JSON.stringify(ratings));
        window.localStorage.setItem("brawlerCurrentIndex", String(currentIndex));
      } catch (e) {
        console.warn("Failed to save ratings:", e);
      }
    }

    function setSelectedButton(rating) {
      ratingButtons.forEach(btn => {
        const r = btn.getAttribute("data-rating");
        if (r === rating) {
          btn.classList.add("selected");
        } else {
          btn.classList.remove("selected");
        }
      });
    }

    function showBrawler(index) {
      const total = BRAWLERS.length;
      if (index < 0 || index >= total) {
        showResults();
        return;
      }

      const b = BRAWLERS[index];
      imgEl.src = b.file;
      imgEl.alt = b.name;
      nameEl.textContent = b.name;

      progressEl.textContent = "Brawler " + (index + 1) + " of " + total;
      const existingRating = ratings[b.name] || null;
      setSelectedButton(existingRating);

      const ratedCount = Object.keys(ratings).length;
      statusEl.textContent = ratedCount === total
        ? "All brawlers rated."
        : ratedCount + " / " + total + " rated";

      prevBtn.disabled = index === 0;
      nextBtn.textContent = index === total - 1 ? "Finish" : "Skip / Next";
    }

    function showResults() {
      ratingView.classList.add("hidden");
      resultsView.classList.remove("hidden");
      buildBuckets();
    }

    function restart() {
      ratings = {};
      currentIndex = 0;
      BRAWLERS = BASE_BRAWLERS.slice();
      saveStored();
      ratingView.classList.remove("hidden");
      resultsView.classList.add("hidden");
      showBrawler(currentIndex);
    }

    function handleRatingClick(ratingValue) {
      const b = BRAWLERS[currentIndex];
      ratings[b.name] = ratingValue;
      saveStored();
      setSelectedButton(ratingValue);
      currentIndex++;
      if (currentIndex >= BRAWLERS.length) {
        showResults();
      } else {
        showBrawler(currentIndex);
      }
    }

    function buildBuckets() {
      bucketsContainer.innerHTML = "";
      const byRating = {};
      RATINGS_ORDER.forEach(r => byRating[r] = []);

      for (const b of BRAWLERS) {
        const r = ratings[b.name] || "Not familiar";
        if (!byRating[r]) byRating[r] = [];
        byRating[r].push(b);
      }

      RATINGS_ORDER.forEach(rating => {
        const bucket = document.createElement("div");
        bucket.className = "bucket";

        const title = document.createElement("div");
        title.className = "bucket-title";
        title.textContent = rating === "Dont like" ? "Don't like" : rating;

        const grid = document.createElement("div");
        grid.className = "bucket-grid";

        const list = byRating[rating] || [];
        if (list.length === 0) {
          const empty = document.createElement("div");
          empty.className = "bucket-empty";
          empty.textContent = "No brawlers in this category yet.";
          bucket.appendChild(title);
          bucket.appendChild(empty);
        } else {
          list.forEach(b => {
            const item = document.createElement("div");
            item.className = "bucket-item";

            const img = document.createElement("img");
            img.src = b.file;
            img.alt = b.name;

            const name = document.createElement("div");
            name.textContent = b.name;

            item.appendChild(img);
            item.appendChild(name);
            grid.appendChild(item);
          });
          bucket.appendChild(title);
          bucket.appendChild(grid);
        }

        bucketsContainer.appendChild(bucket);
      });
    }

    function triggerUploadDialog() {
      uploadInput.click();
    }

    function handleUploadFile(event) {
      const file = event.target.files && event.target.files[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const text = e.target.result;
          const data = JSON.parse(text);

          if (!data || typeof data !== "object") {
            alert("Invalid JSON format.");
            return;
          }

          if (data.brawlers && Array.isArray(data.brawlers)) {
            BRAWLERS = data.brawlers;
          } else {
            BRAWLERS = BASE_BRAWLERS.slice();
          }

          if (data.ratings && typeof data.ratings === "object") {
            ratings = data.ratings;
          } else {
            ratings = {};
          }

          currentIndex = 0;
          saveStored();
          showResults();
          alert("Results loaded from JSON.");
        } catch (err) {
          console.error("Failed to parse JSON:", err);
          alert("Failed to parse JSON file.");
        } finally {
          uploadInput.value = "";
        }
      };
      reader.readAsText(file);
    }

    // Event wiring
    ratingButtons.forEach(btn => {
      btn.addEventListener("click", () => {
        const rating = btn.getAttribute("data-rating");
        handleRatingClick(rating);
      });
    });

    prevBtn.addEventListener("click", () => {
      if (currentIndex > 0) {
        currentIndex--;
        saveStored();
        showBrawler(currentIndex);
      }
    });

    nextBtn.addEventListener("click", () => {
      currentIndex++;
      if (currentIndex >= BRAWLERS.length) {
        showResults();
      } else {
        saveStored();
        showBrawler(currentIndex);
      }
    });

    if (summaryBtn) {
      summaryBtn.addEventListener("click", () => {
        showResults();
      });
    }

    downloadBtn.addEventListener("click", () => {
      const data = {
        ratings,
        brawlers: BRAWLERS
      };
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "brawler_ratings.json";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });

    if (uploadBtn) {
      uploadBtn.addEventListener("click", triggerUploadDialog);
    }
    if (uploadBtnTop) {
      uploadBtnTop.addEventListener("click", triggerUploadDialog);
    }

    uploadInput.addEventListener("change", handleUploadFile);

    printBtn.addEventListener("click", () => {
      showResults();
      window.print();
    });

    restartBtn.addEventListener("click", () => {
      if (confirm("Clear all ratings and start over?")) {
        restart();
      }
    });

    if (backToRatingBtn) {
      backToRatingBtn.addEventListener("click", () => {
        if (BRAWLERS.length === 0) return;

        // Clamp currentIndex into a valid range
        if (currentIndex >= BRAWLERS.length) {
          currentIndex = BRAWLERS.length - 1;
        }
        if (currentIndex < 0) {
          currentIndex = 0;
        }

        resultsView.classList.add("hidden");
        ratingView.classList.remove("hidden");
        showBrawler(currentIndex);
      });
    }

    // Init
    loadStored();

    if (Object.keys(ratings).length === BRAWLERS.length && BRAWLERS.length > 0) {
      ratingView.classList.add("hidden");
      resultsView.classList.remove("hidden");
      buildBuckets();
    } else {
      ratingView.classList.remove("hidden");
      resultsView.classList.add("hidden");
      showBrawler(currentIndex);
    }
  </script>
</body>
</html>
"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)


def main():
    brawlers = collect_brawlers()
    print(f"Found {len(brawlers)} images in '{IMAGE_DIR}'.")
    generate_html(brawlers)
    print(f"Wrote {OUTPUT_HTML}. Open it in a browser to start rating.")


if __name__ == "__main__":
    main()