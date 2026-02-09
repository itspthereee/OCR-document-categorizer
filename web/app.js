const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("fileInput");
const languageSelect = document.getElementById("languageSelect");
const runBtn = document.getElementById("runBtn");
const clearBtn = document.getElementById("clearBtn");
const previewImage = document.getElementById("previewImage");
const cropCanvas = document.getElementById("cropCanvas");
const cropBtn = document.getElementById("cropBtn");
const resetCropBtn = document.getElementById("resetCropBtn");
const textOutput = document.getElementById("textOutput");
const metaEl = document.getElementById("meta");
const statusEl = document.getElementById("status");
const apiBase = document.querySelector('meta[name="api-base"]')?.content?.trim() || window.location.origin;
let selectedFile = null;
let croppedBlob = null;

console.log('API Base URL:', apiBase);

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
  croppedBlob = null;
  setButtons(true);
  setStatus(`Selected: ${file.name}`);
  const reader = new FileReader();
  reader.onload = (event) => {
    setPreview(event.target.result);
    setupCropTool(event.target.result);
  };
  reader.readAsDataURL(file);
};

const setupCropTool = (imageSrc) => {
  const img = new Image();
  img.onload = () => {
    cropCanvas.width = img.width;
    cropCanvas.height = img.height;
    const ctx = cropCanvas.getContext('2d');
    ctx.drawImage(img, 0, 0);
    cropBtn.style.display = 'inline-block';
  };
  img.src = imageSrc;
};

cropBtn.addEventListener("click", () => {
  previewImage.style.display = 'none';
  cropCanvas.style.display = 'block';
  cropBtn.style.display = 'none';
  resetCropBtn.style.display = 'inline-block';
  
  let isDrawing = false;
  let startX, startY, rect = {};
  const ctx = cropCanvas.getContext('2d');
  const imgData = ctx.getImageData(0, 0, cropCanvas.width, cropCanvas.height);
  
  cropCanvas.onmousedown = (e) => {
    const bounds = cropCanvas.getBoundingClientRect();
    const scaleX = cropCanvas.width / bounds.width;
    const scaleY = cropCanvas.height / bounds.height;
    startX = (e.clientX - bounds.left) * scaleX;
    startY = (e.clientY - bounds.top) * scaleY;
    isDrawing = true;
  };
  
  cropCanvas.onmousemove = (e) => {
    if (!isDrawing) return;
    const bounds = cropCanvas.getBoundingClientRect();
    const scaleX = cropCanvas.width / bounds.width;
    const scaleY = cropCanvas.height / bounds.height;
    const currentX = (e.clientX - bounds.left) * scaleX;
    const currentY = (e.clientY - bounds.top) * scaleY;
    
    ctx.putImageData(imgData, 0, 0);
    ctx.strokeStyle = '#4f46e5';
    ctx.lineWidth = 2;
    rect = {
      x: Math.min(startX, currentX),
      y: Math.min(startY, currentY),
      w: Math.abs(currentX - startX),
      h: Math.abs(currentY - startY)
    };
    ctx.strokeRect(rect.x, rect.y, rect.w, rect.h);
  };
  
  cropCanvas.onmouseup = () => {
    if (isDrawing && rect.w > 10 && rect.h > 10) {
      const croppedCanvas = document.createElement('canvas');
      croppedCanvas.width = rect.w;
      croppedCanvas.height = rect.h;
      const croppedCtx = croppedCanvas.getContext('2d');
      croppedCtx.drawImage(cropCanvas, rect.x, rect.y, rect.w, rect.h, 0, 0, rect.w, rect.h);
      
      croppedCanvas.toBlob((blob) => {
        croppedBlob = new File([blob], selectedFile.name, { type: selectedFile.type });
        previewImage.src = croppedCanvas.toDataURL();
        previewImage.style.display = 'block';
        cropCanvas.style.display = 'none';
        cropBtn.style.display = 'inline-block';
        resetCropBtn.style.display = 'none';
        setStatus('Cropped - ready to OCR');
      });
    }
    isDrawing = false;
  };
});

resetCropBtn.addEventListener("click", () => {
  croppedBlob = null;
  cropCanvas.style.display = 'none';
  resetCropBtn.style.display = 'none';
  const reader = new FileReader();
  reader.onload = (e) => {
    setPreview(e.target.result);
    setupCropTool(e.target.result);
  };
  reader.readAsDataURL(selectedFile);
});

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
  formData.append("file", croppedBlob || selectedFile);
  formData.append("languages", languageSelect.value);

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
  croppedBlob = null;
  fileInput.value = "";
  setButtons(false);
  setPreview(null);
  cropCanvas.style.display = 'none';
  cropBtn.style.display = 'none';
  resetCropBtn.style.display = 'none';
  resetOutput();
  setStatus("Ready");
});

setButtons(false);
resetOutput();
