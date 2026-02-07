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
const apiBase = rawApiBase.replace(/\/+$/, "");

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
    const response = await fetch(`${apiBase}/api/ocr`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(text || "Request failed");
    }

    const payload = await response.json();
    metaEl.textContent = `${payload.lines} lines`;
    textOutput.textContent = payload.text || "";
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
