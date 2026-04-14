const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("fileInput");
const runBtn = document.getElementById("runBtn");
const clearBtn = document.getElementById("clearBtn");
const previewImage = document.getElementById("previewImage");
const textOutput = document.getElementById("textOutput");
const metaEl = document.getElementById("meta");
const statusEl = document.getElementById("status");
const rawApiBase =
  document.querySelector('meta[name="api-base"]')?.content || "";
const apiBase = rawApiBase ? rawApiBase.replace(/\/+$/, "") : "";

let selectedFile = null;

const setStatus = (text) => {
  statusEl.textContent = text;
};

const setPreview = (src) => {
  if (src) {
    previewImage.src = src;
    previewImage.style.display = "block";
  } else {
    previewImage.removeAttribute("src");
    previewImage.style.display = "none";
  }
};

const setButtons = (ready) => {
  runBtn.disabled = !ready;
  clearBtn.disabled = !ready;
};

const resetOutput = () => {
  textOutput.textContent = "";
  metaEl.textContent = "No data yet";
};

const handleFile = (file) => {
  if (!file) return;
  selectedFile = file;
  setButtons(true);
  setStatus(`Selected: ${file.name}`);
  const reader = new FileReader();
  reader.onload = (event) => {
    setPreview(event.target.result);
  };
  reader.readAsDataURL(file);
};

fileInput.addEventListener("change", (event) => {
  const file = event.target.files[0];
  handleFile(file);
});

["dragenter", "dragover"].forEach((eventName) => {
  dropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    event.stopPropagation();
    dropzone.classList.add("dragover");
  });
});

["dragleave", "drop"].forEach((eventName) => {
  dropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    event.stopPropagation();
    dropzone.classList.remove("dragover");
  });
});

dropzone.addEventListener("drop", (event) => {
  const file = event.dataTransfer.files[0];
  handleFile(file);
});

runBtn.addEventListener("click", async () => {
  if (!selectedFile) return;
  setStatus("Running OCR...");
  runBtn.disabled = true;
  resetOutput();

  const formData = new FormData();
  formData.append("file", selectedFile);

  try {
    const url = `${apiBase}/api/ocr`;
    console.log("Calling API:", url);
    const response = await fetch(url, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(text || "Request failed");
    }

    const payload = await response.json();
    metaEl.textContent = `${payload.lines} lines detected`;
    
    // Display categorized content
    let output = "=== EXTRACTED & CATEGORIZED TEXT ===\n\n";
    
    if (payload.categories) {
      const { header, items, amounts, footer } = payload.categories;
      
      if (header.length > 0) {
        output += "📋 HEADER INFORMATION\n" + header.join("\n") + "\n\n";
      }
      if (items.length > 0) {
        output += "📦 ITEMS/PRODUCTS\n" + items.join("\n") + "\n\n";
      }
      if (amounts.length > 0) {
        output += "💰 AMOUNTS & TOTALS\n" + amounts.join("\n") + "\n\n";
      }
      if (footer.length > 0) {
        output += "📝 OTHER INFORMATION\n" + footer.join("\n");
      }
    } else {
      output += payload.text || "";
    }
    
    textOutput.textContent = output;
    setStatus("Done");
  } catch (error) {
    setStatus("Error");
    metaEl.textContent = "Failed to run OCR";
    textOutput.textContent = error.message;
  } finally {
    runBtn.disabled = false;
  }
});

clearBtn.addEventListener("click", () => {
  selectedFile = null;
  fileInput.value = "";
  setButtons(false);
  setPreview(null);
  resetOutput();
  setStatus("Ready");
});

setButtons(false);
resetOutput();
