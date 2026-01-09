# MiniGemini Documentation

## Overview

MiniGemini is an AI chatbot with search capabilities using the Gemini free tier search API. It can answer questions about real-time information such as the latest tech news.

## Limitations

- **Rate Limit**: The free tier has a limit of 1 request per minute
- **Cooldown**: If less than 1 minute has passed since the last request, you will see "Error: Cooldown in progress (X seconds remaining)"

## Installation

### Installing with pip

```bash
pip install -r requirements.txt
```

Required packages:
- `google-genai>=1.57.0`
- Other dependencies (see `requirements.txt`)

## How to Get a Free API Key

### 1. Create a Project

1. Access the following URL:
   https://aistudio.google.com/projects

2. Log in with your Google account

3. Click "Create new project"

4. Enter project name "Minigemini" and create it

### 2. Generate API Key

1. Access the following URL:
   https://aistudio.google.com/api-keys

2. Click "Create API key"

3. Enter "minigeminiapi" as the key name

4. Select "Minigemini" for the project

5. Once the API key is generated, copy it

### 3. Configure API Key

1. Run MiniGemini for the first time to automatically generate the configuration file:
   ```bash
   python miniGemini.py
   ```
   This will create `minigemini.json` in the same directory.

2. Open `minigemini.json` and replace the `api_key` value with your copied API key:

```json
{
  "api_key": "Your API key",
  "model_name": "gemini-2.5-flash-lite",
  "prompt_rule": "Include sources within 50 characters"
}
```

**Note**: The configuration file (`minigemini.json`) is automatically generated on first run with default values. You only need to update the `api_key` field with your actual API key.

## Operation Modes

MiniGemini has two operation modes:

### 1. Console Mode (Interactive)

Running without arguments launches interactive console mode.

#### Usage

```bash
python miniGemini.py
```

After launching, enter your question when the prompt appears.

Example:
```
Tell me 3 latest tech news from 2026
```

#### How to Exit

You can exit using any of the following methods:

- Type `exit`
- Type `quit`
- Type `q`
- Press `Ctrl+C`

### 2. Command Line Mode (One-shot)

When you pass a prompt as an argument at startup, it executes once and exits.

#### Usage

```bash
python miniGemini.py "Your question"
```

Example:
```bash
python miniGemini.py "Tell me 3 latest tech news from 2026"
```

If your question contains multiple words, enclose it in quotes.

## Configuration File

The following settings can be configured in `minigemini.json`:

- `api_key`: Gemini API key (required)
- `model_name`: Model name to use (default: `gemini-2.5-flash-lite`)
- `prompt_rule`: Rule to always add to prompts (example: "Include sources within 50 characters")
- `last_used`: Last usage timestamp (automatically updated)

Place the configuration file in the same directory as `miniGemini.py`.

## Error Messages

- `Error: Cooldown in progress (X seconds remaining)`: When attempting to send a request before 1 minute has passed
- `Error: Quota exceeded`: When the daily request limit (20 requests) has been reached
- `Error: API error`: When an error occurs during API call
- `Error: {error details}`: Other errors

## Notes

- The free tier allows up to 20 requests per day
- There is a limit of 1 request per minute
- Place the configuration file (`minigemini.json`) in the same directory as `miniGemini.py`
- **Important**: Response content may not always be accurate. For important information, you should verify it yourself
