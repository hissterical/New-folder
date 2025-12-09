# LLM Query API

A simple Python web app that accepts questions via URL query parameters and responds using an LLM via curl.

## Usage

Once deployed, use it like this:

```
https://your-app.vercel.app/?q=What is the capital of France?
```

## Local Testing

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your Gemini API key:
```bash
$env:GEMINI_API_KEY="your-api-key-here"
```

3. Run locally:
```bash
python api/index.py
```

4. Test it:
```
http://localhost:5000/?q=Hello, how are you?
```

## Deploying to Vercel

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Set your Gemini API key as a secret:
```bash
vercel secrets add gemini_api_key "your-api-key-here"
```

3. Deploy:
```bash
vercel
```

## Environment Variables

- `GEMINI_API_KEY`: Your Google Gemini API key (required)

## Endpoints

- `GET /?q=your-question` - Ask a question to the LLM
- `GET /health` - Health check endpoint

## Response Format

```json
{
  "question": "What is the capital of France?",
  "answer": "The capital of France is Paris.",
  "model": "gemini-pro"
}
```
