# Financial Statement Research Web App

This is a minimal Next.js 14 (App Router) web application for end-to-end financial statement research and export.

## Stack

- Next.js 14 (App Router)
- Node.js route handlers under `app/api`
- Google Gemini (via REST API) as the **only** LLM
- PDF text extraction using `pdf-parse`
- Excel generation using `exceljs`

## Functional flow

1. Upload a PDF on the main page.
2. Click **"Process Financial Statement"**.
3. Backend:
   - `/api/upload` extracts text from the PDF.
   - `/api/gemini` calls Gemini to normalize line items.
   - `/api/export` generates an Excel file and makes it downloadable from `/public/exports`.

No additional manual steps are required beyond uploading a PDF and clicking the button.

## Getting started

1. Install dependencies:

```bash
npm install
```

2. Configure your Gemini API key in `.env.local`:

```bash
GEMINI_API_KEY=YOUR_KEY_HERE
```

3. Run the development server:

```bash
npm run dev
```

4. Open `http://localhost:3000` in your browser.

## Environment variables

- `GEMINI_API_KEY` – your Google Gemini API key (no other API keys are used).

