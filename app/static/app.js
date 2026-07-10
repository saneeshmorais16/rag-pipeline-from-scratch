async function refreshHealth() {
  const response = await fetch("/health");
  const data = await response.json();
  document.querySelector("#health").textContent = `${data.status.toUpperCase()} - ${data.chunks_indexed} chunks indexed`;
}

document.querySelector("#folderForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const result = document.querySelector("#ingestResult");
  result.textContent = "Ingesting...";
  const response = await fetch("/ingest", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ path: document.querySelector("#path").value }),
  });
  const data = await response.json();
  result.textContent = response.ok
    ? `Found ${data.documents_found} document(s), added ${data.chunks_added} chunk(s).`
    : data.detail;
  refreshHealth();
});

document.querySelector("#uploadForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const result = document.querySelector("#uploadResult");
  const fileInput = document.querySelector("#file");
  if (!fileInput.files.length) {
    result.textContent = "Choose a file first.";
    return;
  }
  const formData = new FormData();
  formData.append("file", fileInput.files[0]);
  result.textContent = "Uploading...";
  const response = await fetch("/ingest/upload", { method: "POST", body: formData });
  const data = await response.json();
  result.textContent = response.ok
    ? `Added ${data.chunks_added} chunk(s) from ${data.documents_found} document(s).`
    : data.detail;
  refreshHealth();
});

document.querySelector("#queryForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const answer = document.querySelector("#answer");
  const sources = document.querySelector("#sources");
  answer.textContent = "Retrieving...";
  sources.innerHTML = "";
  const response = await fetch("/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question: document.querySelector("#question").value, top_k: 4 }),
  });
  const data = await response.json();
  answer.textContent = data.answer || data.detail;
  sources.innerHTML = (data.sources || [])
    .map(
      (source) => `
        <article class="source">
          <strong>${source.document_name}</strong>
          <span>chunk ${source.chunk_index} - score ${source.score.toFixed(3)}</span>
          <p>${source.text.slice(0, 420)}</p>
        </article>
      `
    )
    .join("");
});

refreshHealth();
