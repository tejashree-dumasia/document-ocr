# 🚀 Dynamic AI Document Extraction API

An end-to-end REST API that extracts text from scanned documents using Optical Character Recognition (OCR) and leverages Generative AI to transform unstructured content into structured JSON based on a user-defined schema.

![Demo](./assets/demo.gif)

## 📌 Overview

Traditional document extraction systems often rely on predefined templates, making them difficult to adapt to different document formats. This project addresses that limitation by allowing clients to upload a scanned document and specify the exact fields they want to extract.

The API processes the image using computer vision, extracts text with EasyOCR, and uses Google's Gemini API to map the extracted information into the requested JSON structure.

The result is a flexible document extraction pipeline suitable for invoices, receipts, forms, and other image-based documents.

## ✨ Key Features

- **In-Memory Image Processing:** Processes uploaded images using OpenCV without requiring temporary image files on disk.
- **Deep Learning-Based OCR:** Uses EasyOCR to extract text from documents with varying fonts and layouts.
- **Dynamic JSON Schema:** Allows clients to define the fields they need for each extraction request.
- **Generative AI Integration:** Uses Google Gemini to convert raw OCR text into structured JSON.
- **Fault-Tolerant API Calls:** Implements retry logic with Tenacity to handle transient failures and rate limits.
- **Interactive API Documentation:** Provides an automatically generated Swagger UI through FastAPI.
- **RESTful Architecture:** Exposes document extraction functionality through an HTTP endpoint.

## 🏗️ Architecture Flow

1. **Client Request:** The client uploads a document image and a JSON schema through a multipart form-data request.
2. **Image Preprocessing:** OpenCV converts the image to grayscale, applies adaptive thresholding, and prepares it for OCR.
3. **Text Extraction:** EasyOCR detects and extracts text from the processed image.
4. **AI-Based Structuring:** The extracted text and requested schema are passed to Gemini, which generates structured JSON.
5. **API Response:** The API returns the extracted information as a JSON response.

## 💻 Tech Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| API Framework | FastAPI |
| ASGI Server | Uvicorn |
| Image Processing | OpenCV, NumPy |
| Optical Character Recognition | EasyOCR |
| Generative AI | Google Gemini API (`google-genai`) |
| Retry Mechanism | Tenacity |
| API Documentation | Swagger UI (OpenAPI) |

## 📂 Project Structure

```text
dynamic-document-extractor/
├── api.py
├── requirements.txt
├── README.md
└── assets/
    └── demo.gif
```

> The `assets/demo.gif` file is optional. Add a screen recording of the API working in Swagger UI to display the demo on your GitHub repository page.

## ⚙️ Installation and Setup

### Prerequisites

- Python 3.10 or a compatible version supported by your dependencies
- pip
- A Google Gemini API key from [Google AI Studio](https://aistudio.google.com/)

### 1. Clone the Repository

```bash
git clone https://github.com/YourUsername/dynamic-document-extractor.git
cd dynamic-document-extractor
```

Replace `YourUsername` with your GitHub username and update the repository URL if necessary.

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment.

**Windows (Command Prompt):**

```bat
venv\Scripts\activate
```

**Windows (PowerShell):**

```powershell
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

EasyOCR may download its pretrained model files the first time it runs. Initial setup and inference can therefore take longer than subsequent requests.

### 4. Configure the Gemini API Key

Configure your Google Gemini API key using an environment variable rather than hardcoding it in your source code.

**Windows (PowerShell):**

```powershell
$env:GEMINI_API_KEY="your_api_key_here"
```

**Windows (Command Prompt):**

```bat
set GEMINI_API_KEY=your_api_key_here
```

**macOS / Linux:**

```bash
export GEMINI_API_KEY="your_api_key_here"
```

Ensure that `api.py` reads the key from the `GEMINI_API_KEY` environment variable.

> **Security:** Never commit API keys or other secrets to your Git repository.

### 5. Start the API Server

```bash
uvicorn api:app --reload
```

The API should now be available at:

- **API Base URL:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 📡 API Usage

### Extract Document Data

**Endpoint:** `POST /api/v1/extract`

**Content-Type:** `multipart/form-data`

#### Request Parameters

| Parameter | Type | Description |
|---|---|---|
| `file` | File | The document image to process, such as a JPG or PNG |
| `schema_definition` | String | A JSON string describing the fields to extract |

#### Example Schema

```json
{
  "vendor_name": "string",
  "invoice_number": "string",
  "total_amount": "float"
}
```

This schema requests the vendor name, invoice number, and total amount from the uploaded document.

#### Example Request Using cURL

```bash
curl -X POST "http://localhost:8000/api/v1/extract" \
  -F "file=@invoice.jpg" \
  -F 'schema_definition={"vendor_name":"string","invoice_number":"string","total_amount":"float"}'
```

Replace `invoice.jpg` with the path to your document image.

#### Testing with Swagger UI

1. Start the API server.
2. Open http://localhost:8000/docs in your browser.
3. Expand `POST /api/v1/extract`.
4. Click **Try it out**.
5. Upload a document image.
6. Enter the JSON schema in the `schema_definition` field.
7. Click **Execute** to submit the request and inspect the response.

#### Example Response

The following is an illustrative response for a sample invoice. Actual values depend on the uploaded document.

```json
{
  "vendor_name": "ABC Supplies",
  "invoice_number": "INV-2026-001",
  "total_amount": 1250.50
}
```

## 🔒 Error Handling and Reliability

The project uses Tenacity to retry eligible AI API calls when transient failures occur. Retry policies can help handle temporary service errors and rate limits.

The API should also validate uploaded files and schema definitions and return appropriate HTTP error responses for invalid requests or processing failures.

Retries do not guarantee success, and permanent errors or exhausted retry attempts must still be handled appropriately.

## 🚧 Limitations

- Extraction accuracy depends on image quality, document layout, OCR performance, and the AI model's interpretation.
- Complex tables, handwritten text, blurry images, and unusual document formats may reduce accuracy.
- AI-generated values should be validated before being used in financial, legal, or other critical workflows.
- Gemini API usage is subject to the provider's quotas, rate limits, and pricing.
- The initial EasyOCR model download may increase startup or first-request latency.

## 🔮 Future Improvements

- Add Pydantic-based validation for dynamic extraction schemas.
- Support PDF documents and multi-page extraction.
- Add structured error responses and request validation.
- Implement authentication, rate limiting, and request logging.
- Add automated tests for image preprocessing, OCR, and API endpoints.
- Introduce configurable model selection and extraction confidence checks.
- Add Docker support and production deployment configuration.

## 🤝 Contributing

Contributions, suggestions, and bug reports are welcome. Feel free to open an issue or submit a pull request.

## 📄 License

Add a license to this repository if you intend to distribute the project publicly. For example, you can use the MIT License by adding a `LICENSE` file containing its terms.

---

**Built with Python, FastAPI, OpenCV, EasyOCR, and Google Gemini.**