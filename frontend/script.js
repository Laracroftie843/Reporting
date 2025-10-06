document.getElementById("uploadForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const files = document.getElementById("files").files;
  if (files.length === 0) {
    alert("Please select at least one CSV file");
    return;
  }

  const formData = new FormData();
  for (let file of files) {
    formData.append("files[]", file);
  }

  const messageDiv = document.getElementById("message");
  messageDiv.textContent = "Uploading and processing...";

  try {
    const res = await fetch("/upload", { method: "POST", body: formData });
    const data = await res.json();

    if (data.error) throw new Error(data.error);

    messageDiv.innerHTML = `
      ✅ ${data.message}<br>
      <a href="${data.pdf_download}" target="_blank">Download PDF Report</a>
    `;
  } catch (err) {
    messageDiv.textContent = `❌ Error: ${err.message}`;
  }
});

