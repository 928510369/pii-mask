# User Guide

## Overview

Alta-Lex PII Shield is a web application that detects and masks Personally Identifiable Information (PII) in text and documents. It uses the Qwen3-0.6B language model to identify sensitive data and replaces it with ████ blocks.

---

## Getting Started

Open the application in your browser at `http://localhost:5173`. You'll see a two-panel interface:

- **Left panel:** Input (text entry + file upload + PII categories)
- **Right panel:** Masked output

---

## Inputting Text

### Direct Text Entry

1. Click the large text area on the left panel
2. Type or paste text containing PII
3. The "Mask PII" button becomes active when text is present

**Example input:**
```
My name is John Smith, email john@example.com, phone 138-1234-5678.
I live at 123 Main Street, New York, NY 10001.
```

### File Upload

Supported formats: **TXT, PDF, DOCX, CSV, XLSX**

**Drag and Drop:**
1. Drag a file from your file manager
2. Drop it onto the upload zone (shows "Drop a file here or click to upload")
3. The file's text content is extracted and placed in the text area

**Click to Upload:**
1. Click the upload zone
2. Select a file from the file chooser dialog
3. Text is extracted automatically

**After upload:**
- The file name appears with a remove (✕) button
- Click ✕ to remove the file and clear the text

---

## Configuring PII Categories

The categories section shows which types of PII to detect:

### Default Categories (all enabled)

| Category | Description | Example |
|----------|-------------|---------|
| Name | Person names | John Smith, 张三 |
| Phone | Phone numbers | 138-1234-5678 |
| Email | Email addresses | user@example.com |
| Address | Physical addresses | 123 Main St, NY |
| ID Number | Government ID numbers | 110101199001011234 |
| Bank Card | Credit/debit card numbers | 6222 0200 1234 5678 |
| Social Media | Social media handles | @johndoe123 |

### Toggling Categories

- Click a category tag to toggle it **off** (turns gray)
- Click again to toggle it **on** (turns highlighted)
- The active count updates: "PII Categories (N active)"
- Only active categories are sent to the masking API

### Adding Custom Categories

1. Type a category name in the "Add custom category..." field
2. Click **+ Add** or press **Enter**
3. The new category appears as an active tag
4. Duplicates and empty values are rejected

---

## Masking PII

1. Enter text (type, paste, or upload a file)
2. Configure PII categories (optional - all are on by default)
3. Click the **Mask PII** button
4. Wait for processing (spinner shows "Analyzing...")

---

## Reading the Output

### Masked Text

- PII is replaced with red-highlighted **████** blocks
- Non-PII text remains unchanged
- The output preserves the original text structure

### Detection Summary

Below the masked text, colored badges show:
- The **type** of each detected PII category
- The **count** of detections per category

Example: `name 2` `email 1` `phone 1`

### Copy to Clipboard

- Click **Copy** in the output panel header
- The full masked text is copied (████ blocks as unicode text)
- Button briefly shows "Copied!" to confirm

---

## Error Handling

| Error | Meaning |
|-------|---------|
| "Please enter or upload text to mask" | No text in the input area |
| "Please select at least one PII category" | All categories are toggled off |
| "Upload failed" | File upload or parsing error |
| "API connection failed" | Backend API is not reachable |
| "LLM service error" | The language model returned an error |

---

## Tips

- **Longer text with multiple PII types** tends to produce better detection results
- **Chinese text** is supported natively by the Qwen3 model
- The 0.6B model works best with **structured PII** (phone numbers, emails, ID numbers)
- For better name detection, consider using a larger model (Qwen3-4B+)
- Custom categories work best with clear, single-word descriptions
