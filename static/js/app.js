"use strict";

/* =========================================================
   DOCINTEL AI - ENTERPRISE FRONTEND WORKFLOW LOGIC
   ========================================================= */

let selectedFile = null;
let uploadedDocumentId = null;
let processingStartTime = null;
let currentZoom = 100;
let extractedFieldsData = [];

// DOM Elements
const fileInput = document.getElementById("fileInput");
const dropZone = document.getElementById("dropZone");
const uploadBtn = document.getElementById("uploadBtn");
const selectedFileEl = document.getElementById("selectedFile");
const fileNameEl = document.getElementById("fileName");
const fileSizeEl = document.getElementById("fileSize");
const fileBadgeEl = document.getElementById("fileBadge");
const removeFileBtn = document.getElementById("removeFile");
const uploadMessageEl = document.getElementById("uploadMessage");

const pipelineSection = document.getElementById("pipelineSection");
const pipelineMessageEl = document.getElementById("pipelineMessage");
const processingPercentEl = document.getElementById("processingPercent");
const progressFillEl = document.getElementById("progressFill");

const resultsSection = document.getElementById("resultsSection");
const processingErrorEl = document.getElementById("processingError");
const processingErrorMessageEl = document.getElementById("processingErrorMessage");

// KPI & Tab Elements
const documentTypeEl = document.getElementById("documentType");
const resultFilenameEl = document.getElementById("resultFilename");
const pageCountEl = document.getElementById("pageCount");
const processingTimeEl = document.getElementById("processingTime");
const resultDocumentIdEl = document.getElementById("resultDocumentId");
const extractedFieldsEl = document.getElementById("extractedFields");
const fieldsCountBadgeEl = document.getElementById("fieldsCountBadge");
const fieldSearchInput = document.getElementById("fieldSearchInput");

const ocrTextEl = document.getElementById("ocrText");
const tableContainerEl = document.getElementById("tableContainer");
const jsonOutputEl = document.getElementById("jsonOutput");
const processedImagePreviewEl = document.getElementById("processedImagePreview");
const previewMessageEl = document.getElementById("previewMessage");

// Copy & Download Buttons
const copyJsonBtn = document.getElementById("copyJsonBtn");
const copyOcrBtn = document.getElementById("copyOcrBtn");
const jsonBtn = document.getElementById("jsonBtn");
const excelBtn = document.getElementById("excelBtn");
const imageBtn = document.getElementById("imageBtn");
const textBtn = document.getElementById("textBtn");
const originalBtn = document.getElementById("originalBtn");

// Zoom Buttons
const zoomInBtn = document.getElementById("zoomInBtn");
const zoomOutBtn = document.getElementById("zoomOutBtn");
const zoomResetBtn = document.getElementById("zoomResetBtn");
const zoomLevelText = document.getElementById("zoomLevelText");

/* =========================================================
   INITIALIZATION & EVENT LISTENERS
   ========================================================= */
document.addEventListener("DOMContentLoaded", () => {
    hideElement(pipelineSection);
    hideElement(resultsSection);
    hideElement(processingErrorEl);
    setupTabsNavigation();
    setupDragAndDrop();
    setupZoomControls();
    setupSearchFilter();
    setupCopyButtons();
    setupDownloadButtons();
    setupKeyboardShortcuts();
});

function hideElement(el) {
    if (el) el.classList.add("hidden");
}

function showElement(el) {
    if (el) el.classList.remove("hidden");
}

/* =========================================================
   FILE SELECTION & DRAG AND DROP
   ========================================================= */
function setupDragAndDrop() {
    if (!dropZone) return;

    ["dragenter", "dragover"].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.add("drag-over");
        }, false);
    });

    ["dragleave", "drop"].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove("drag-over");
        }, false);
    });

    dropZone.addEventListener("drop", (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files && files.length > 0) {
            handleFileSelected(files[0]);
        }
    });

    fileInput?.addEventListener("change", (e) => {
        if (e.target.files && e.target.files.length > 0) {
            handleFileSelected(e.target.files[0]);
        }
    });

    removeFileBtn?.addEventListener("click", () => {
        selectedFile = null;
        fileInput.value = "";
        hideElement(selectedFileEl);
        showElement(dropZone);
        uploadBtn.disabled = true;
        hideElement(uploadMessageEl);
    });

    uploadBtn?.addEventListener("click", () => {
        if (selectedFile) {
            startDocumentProcessing();
        }
    });
}

function handleFileSelected(file) {
    const allowed = [".pdf", ".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif"];
    const ext = "." + file.name.split(".").pop().toLowerCase();
    
    if (!allowed.includes(ext)) {
        showToast("Unsupported file type: " + ext, "error");
        return;
    }

    selectedFile = file;
    fileNameEl.textContent = file.name;
    fileSizeEl.textContent = formatBytes(file.size);
    if (fileBadgeEl) fileBadgeEl.textContent = ext.replace(".", "").toUpperCase();

    showElement(selectedFileEl);
    hideElement(dropZone);
    uploadBtn.disabled = false;
    hideElement(uploadMessageEl);
    showToast("Document loaded. Click 'Execute AI Analysis' to begin.", "info");
}

function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
}

/* =========================================================
   PROCESS DOCUMENT PIPELINE EXECUTION
   ========================================================= */
async function startDocumentProcessing() {
    if (!selectedFile) return;

    uploadBtn.disabled = true;
    hideElement(resultsSection);
    hideElement(processingErrorEl);
    showElement(pipelineSection);

    resetPipelineSteps();
    updatePipelineProgress(1, 10, "Uploading document to ingestion engine...");
    processingStartTime = Date.now();

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
        // Step 1: Ingest/Upload
        const uploadRes = await fetch("/api/documents/upload", {
            method: "POST",
            body: formData
        });

        if (!uploadRes.ok) {
            const errData = await uploadRes.json();
            throw new Error(errData.detail || "File upload failed.");
        }

        const uploadData = await uploadRes.json();
        uploadedDocumentId = uploadData.document_id;
        
        updatePipelineProgress(2, 30, "Document uploaded. Running PDF & Page Conversion...");

        // Simulate multi-stage visual progress
        await sleep(400);
        updatePipelineProgress(3, 50, "Applying image preprocessing (Denoising & Deskew)...");

        await sleep(400);
        updatePipelineProgress(4, 65, "Executing Vision OCR & Bounding Box extraction...");

        await sleep(400);
        updatePipelineProgress(5, 80, "Detecting document layout, key-value pairs & tables...");

        // Step 2: Trigger Backend Processing
        const processRes = await fetch(`/api/documents/process/${uploadedDocumentId}`, {
            method: "POST"
        });

        if (!processRes.ok) {
            const errData = await processRes.json();
            throw new Error(errData.detail || "Document processing failed.");
        }

        const processData = await processRes.json();

        updatePipelineProgress(6, 92, "Aligning AI contextual corrections...");
        await sleep(300);

        updatePipelineProgress(7, 100, "Extraction complete! Generating workstation results...");
        await sleep(300);

        hideElement(pipelineSection);
        renderDocumentResults(processData.result);
        showElement(resultsSection);
        showToast("AI Document Analysis Completed Successfully!", "success");

    } catch (err) {
        hideElement(pipelineSection);
        showElement(processingErrorEl);
        processingErrorMessageEl.textContent = err.message || "An unexpected processing error occurred.";
        uploadBtn.disabled = false;
        showToast("Processing failed: " + err.message, "error");
    }
}

function updatePipelineProgress(stepNum, percent, message) {
    if (processingPercentEl) processingPercentEl.textContent = percent + "%";
    if (progressFillEl) progressFillEl.style.width = percent + "%";
    if (pipelineMessageEl) pipelineMessageEl.textContent = message;

    for (let i = 1; i <= 7; i++) {
        const stepEl = document.getElementById(`step${i}`);
        if (!stepEl) continue;

        if (i < stepNum) {
            stepEl.className = "step-card completed";
            stepEl.querySelector(".step-icon-status").textContent = "✓";
        } else if (i === stepNum) {
            stepEl.className = "step-card active";
            stepEl.querySelector(".step-icon-status").textContent = "⏳";
        } else {
            stepEl.className = "step-card";
            stepEl.querySelector(".step-icon-status").textContent = "○";
        }
    }
}

function resetPipelineSteps() {
    updatePipelineProgress(1, 0, "Initializing Document Processing Pipeline...");
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/* =========================================================
   RESULTS RENDERING
   ========================================================= */
function renderDocumentResults(data) {
    if (!data) return;

    const elapsedTime = ((Date.now() - processingStartTime) / 1000).toFixed(2);

    // Render KPI Cards
    if (documentTypeEl) documentTypeEl.textContent = data.document_type || data.classification || "General Document";
    if (resultFilenameEl) resultFilenameEl.textContent = selectedFile ? selectedFile.name : (data.filename || "-");
    if (pageCountEl) pageCountEl.textContent = data.page_count || data.pages || "1";
    if (processingTimeEl) processingTimeEl.textContent = `${elapsedTime}s`;
    if (resultDocumentIdEl) resultDocumentIdEl.textContent = uploadedDocumentId || "-";

    // Render Extracted Fields Grid
    extractedFieldsData = [];
    const fieldsContainer = extractedFieldsEl;
    fieldsContainer.innerHTML = "";

    const rawFields = data.extracted_fields || data.structured_data || data.fields || data.key_value_pairs || {};

    if (typeof rawFields === "object" && rawFields !== null) {
        Object.entries(rawFields).forEach(([k, v]) => {
            if (typeof v !== "object") {
                extractedFieldsData.push({ key: k, value: String(v) });
            } else if (v !== null && v.value !== undefined) {
                extractedFieldsData.push({ key: k, value: String(v.value) });
            }
        });
    }

    if (fieldsCountBadgeEl) fieldsCountBadgeEl.textContent = extractedFieldsData.length;

    renderFieldsGrid(extractedFieldsData);

    // Render OCR Text
    const rawOcr = data.ocr_text || data.text || (typeof data.ocr === "string" ? data.ocr : JSON.stringify(data.ocr || {}, null, 2));
    if (ocrTextEl) ocrTextEl.textContent = rawOcr || "No text extracted.";

    // Render Table Data
    if (tableContainerEl) {
        const tables = data.tables || data.detected_tables || [];
        if (Array.isArray(tables) && tables.length > 0) {
            tableContainerEl.innerHTML = renderTablesHTML(tables);
        } else {
            tableContainerEl.innerHTML = `<div class="empty-table-placeholder">No structured tables detected in this document.</div>`;
        }
    }

    // Render Formatted JSON
    if (jsonOutputEl) {
        jsonOutputEl.textContent = JSON.stringify(data, null, 2);
    }

    // Render Processed Image Preview
    if (processedImagePreviewEl) {
        const imgUrl = `/api/documents/${uploadedDocumentId}/download/image?t=` + new Date().getTime();
        processedImagePreviewEl.src = imgUrl;
        processedImagePreviewEl.onload = () => {
            showElement(processedImagePreviewEl);
            hideElement(previewMessageEl);
        };
        processedImagePreviewEl.onerror = () => {
            hideElement(processedImagePreviewEl);
            showElement(previewMessageEl);
            if (previewMessageEl) previewMessageEl.textContent = "Processed document preview image unavailable.";
        };
    }
}

function renderFieldsGrid(fieldsList) {
    if (!extractedFieldsEl) return;
    extractedFieldsEl.innerHTML = "";

    if (fieldsList.length === 0) {
        extractedFieldsEl.innerHTML = `<div class="empty-state-placeholder"><p>No key-value fields detected.</p></div>`;
        return;
    }

    fieldsList.forEach(item => {
        const card = document.createElement("div");
        card.className = "field-card";
        card.innerHTML = `
            <span class="field-key">${escapeHtml(item.key.replace(/_/g, " "))}</span>
            <span class="field-val">${escapeHtml(item.value)}</span>
        `;
        extractedFieldsEl.appendChild(card);
    });
}

function renderTablesHTML(tables) {
    return tables.map((tbl, idx) => {
        if (!Array.isArray(tbl) || tbl.length === 0) return "";
        let html = `<h5 style="color: var(--accent-purple); margin-bottom: 8px;">Table #${idx + 1}</h5>`;
        html += `<table class="rendered-table">`;
        tbl.forEach((row, rIdx) => {
            html += `<tr>`;
            if (Array.isArray(row)) {
                row.forEach(cell => {
                    if (rIdx === 0) {
                        html += `<th>${escapeHtml(String(cell))}</th>`;
                    } else {
                        html += `<td>${escapeHtml(String(cell))}</td>`;
                    }
                });
            } else if (typeof row === "object" && row !== null) {
                Object.values(row).forEach(val => {
                    html += `<td>${escapeHtml(String(val))}</td>`;
                });
            }
            html += `</tr>`;
        });
        html += `</table><br>`;
        return html;
    }).join("");
}

function escapeHtml(str) {
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

/* =========================================================
   SEARCH & FILTERING
   ========================================================= */
function setupSearchFilter() {
    fieldSearchInput?.addEventListener("input", (e) => {
        const query = e.target.value.toLowerCase().trim();
        if (!query) {
            renderFieldsGrid(extractedFieldsData);
            return;
        }
        const filtered = extractedFieldsData.filter(item => 
            item.key.toLowerCase().includes(query) || item.value.toLowerCase().includes(query)
        );
        renderFieldsGrid(filtered);
    });
}

/* =========================================================
   TABS NAVIGATION
   ========================================================= */
function setupTabsNavigation() {
    const tabBtns = document.querySelectorAll(".tab-btn");
    const tabPanes = document.querySelectorAll(".tab-content-pane");

    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            tabBtns.forEach(b => b.classList.remove("active"));
            tabPanes.forEach(p => p.classList.remove("active"));

            btn.classList.add("active");
            const targetPaneId = btn.getAttribute("data-tab");
            const targetPane = document.getElementById(targetPaneId);
            if (targetPane) targetPane.classList.add("active");
        });
    });
}

/* =========================================================
   ZOOM CONTROLS FOR IMAGE PREVIEW
   ========================================================= */
function setupZoomControls() {
    zoomInBtn?.addEventListener("click", () => {
        if (currentZoom < 250) {
            currentZoom += 25;
            updateImageZoom();
        }
    });

    zoomOutBtn?.addEventListener("click", () => {
        if (currentZoom > 50) {
            currentZoom -= 25;
            updateImageZoom();
        }
    });

    zoomResetBtn?.addEventListener("click", () => {
        currentZoom = 100;
        updateImageZoom();
    });
}

function updateImageZoom() {
    if (processedImagePreviewEl) {
        processedImagePreviewEl.style.transform = `scale(${currentZoom / 100})`;
    }
    if (zoomLevelText) {
        zoomLevelText.textContent = `${currentZoom}%`;
    }
}

/* =========================================================
   COPY & DOWNLOAD BUTTONS
   ========================================================= */
function setupCopyButtons() {
    copyJsonBtn?.addEventListener("click", () => {
        if (jsonOutputEl && jsonOutputEl.textContent) {
            navigator.clipboard.writeText(jsonOutputEl.textContent);
            showToast("Structured JSON copied to clipboard!", "success");
        }
    });

    copyOcrBtn?.addEventListener("click", () => {
        if (ocrTextEl && ocrTextEl.textContent) {
            navigator.clipboard.writeText(ocrTextEl.textContent);
            showToast("OCR raw text copied to clipboard!", "success");
        }
    });
}

function setupDownloadButtons() {
    jsonBtn?.addEventListener("click", () => {
        if (uploadedDocumentId) window.open(`/api/documents/${uploadedDocumentId}/download/json`, "_blank");
    });
    excelBtn?.addEventListener("click", () => {
        if (uploadedDocumentId) window.open(`/api/documents/${uploadedDocumentId}/download/excel`, "_blank");
    });
    imageBtn?.addEventListener("click", () => {
        if (uploadedDocumentId) window.open(`/api/documents/${uploadedDocumentId}/download/image`, "_blank");
    });
    textBtn?.addEventListener("click", () => {
        if (uploadedDocumentId) window.open(`/api/documents/${uploadedDocumentId}/download/text`, "_blank");
    });
    originalBtn?.addEventListener("click", () => {
        if (uploadedDocumentId) window.open(`/api/documents/${uploadedDocumentId}/download/original`, "_blank");
    });
}

function setupKeyboardShortcuts() {
    document.addEventListener("keydown", (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
            if (selectedFile && !uploadBtn.disabled) {
                startDocumentProcessing();
            }
        }
    });
}

/* =========================================================
   TOAST ALERTS
   ========================================================= */
function showToast(message, type = "info") {
    const container = document.getElementById("toastContainer");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    
    let icon = "ℹ️";
    if (type === "success") icon = "✅";
    if (type === "error") icon = "⚠️";

    toast.innerHTML = `<span>${icon}</span> <span>${escapeHtml(message)}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateY(20px)";
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}