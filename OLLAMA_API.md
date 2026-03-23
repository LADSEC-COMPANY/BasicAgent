# Ollama API Documentation

Ollama exposes an HTTP API to run and interact with models locally. This document covers the main endpoints used by the chatbot and other common operations.

**Base URL (local):** `http://localhost:11434/api`  
**Base URL (cloud):** `https://ollama.com/api`

---

## Table of Contents

1. [Chat](#chat) – conversational completions (used by the chatbot)
2. [Generate](#generate) – single-prompt text generation
3. [List Models](#list-models)
4. [Embeddings](#embeddings)
5. [Pull Model](#pull-model)
6. [Streaming](#streaming)

---

## Chat

**Endpoint:** `POST /api/chat`  
**Purpose:** Generate the next message in a multi-turn conversation (used by this project's chatbot).

### Request

| Field      | Type     | Required | Description                                      |
|------------|----------|----------|--------------------------------------------------|
| `model`    | string   | yes      | Model name (e.g. `llama3.2:latest`, `gemma3:1b`) |
| `messages` | array    | yes      | List of `{ role, content }` messages             |
| `stream`   | boolean  | no       | Stream response (default: `true`)                |
| `format`   | string/object | no  | `"json"` or a JSON schema for structured output |
| `options`  | object   | no       | Generation options (temperature, top_p, etc.)    |
| `keep_alive` | string/number | no | Keep model loaded (e.g. `"5m"`, `0` to unload) |

**Message format:**
```json
{ "role": "user" | "assistant" | "system", "content": "..." }
```

### Example Request (non-streaming)

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "llama3.2:latest",
  "messages": [
    {"role": "user", "content": "What is 2+2?"}
  ],
  "stream": false
}'
```

### Example Request (multi-turn)

```json
{
  "model": "gemma3:1b",
  "messages": [
    {"role": "user", "content": "My name is Alice."},
    {"role": "assistant", "content": "Nice to meet you, Alice!"},
    {"role": "user", "content": "What's my name?"}
  ],
  "stream": false
}
```

### Response (non-streaming)

```json
{
  "model": "llama3.2:latest",
  "created_at": "2025-03-17T12:00:00.000Z",
  "message": {
    "role": "assistant",
    "content": "2 + 2 equals 4."
  },
  "done": true,
  "done_reason": "stop",
  "total_duration": 174560334,
  "load_duration": 101397084,
  "prompt_eval_count": 11,
  "prompt_eval_duration": 13074791,
  "eval_count": 18,
  "eval_duration": 52479709
}
```

| Field                  | Description                                  |
|------------------------|----------------------------------------------|
| `message.content`      | The assistant’s reply text                   |
| `done`                 | Whether generation finished                  |
| `done_reason`          | Why it stopped (`stop`, `length`, etc.)      |
| `eval_count`           | Number of tokens generated                   |
| `prompt_eval_count`    | Number of input tokens                       |
| `*_duration`           | Durations in nanoseconds                     |

---

## Generate

**Endpoint:** `POST /api/generate`  
**Purpose:** Generate text from a single prompt (no conversation history).

### Request

| Field      | Type     | Required | Description                                      |
|------------|----------|----------|--------------------------------------------------|
| `model`    | string   | yes      | Model name                                       |
| `prompt`   | string   | no       | Text to generate from                            |
| `stream`   | boolean  | no       | Stream response (default: `true`)                 |
| `system`   | string   | no       | System prompt                                    |
| `images`   | array    | no       | Base64-encoded images (for vision models)        |
| `format`   | string/object | no  | `"json"` or JSON schema for structured output    |
| `options`  | object   | no       | Generation options                               |
| `keep_alive` | string/number | no | Keep model loaded (e.g. `"5m"`, `0`)        |

### Example Request

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "gemma3:1b",
  "prompt": "Why is the sky blue?",
  "stream": false
}'
```

### Example with Options

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2:latest",
  "prompt": "Tell me a short joke.",
  "stream": false,
  "options": {
    "temperature": 0.8,
    "top_p": 0.9,
    "seed": 42,
    "num_predict": 100
  }
}'
```

### Response (non-streaming)

```json
{
  "model": "gemma3:1b",
  "created_at": "2025-03-17T12:00:00.000Z",
  "response": "The sky appears blue because...",
  "done": true,
  "done_reason": "stop",
  "eval_count": 42,
  "prompt_eval_count": 15
}
```

### Model Options (for both Chat and Generate)

| Option       | Type   | Description                                      |
|--------------|--------|--------------------------------------------------|
| `temperature`| number | Randomness (higher = more random)               |
| `top_p`      | number | Cumulative probability threshold                 |
| `top_k`      | int    | Limit next token to top K candidates            |
| `seed`       | int    | Random seed for reproducibility                 |
| `num_ctx`    | int    | Context window size (tokens)                    |
| `num_predict`| int    | Max tokens to generate                          |
| `stop`       | string/array | Stop sequences                           |

---

## List Models

**Endpoint:** `GET /api/tags`  
**Purpose:** List installed models.

### Request

```bash
curl http://localhost:11434/api/tags
```

### Response

```json
{
  "models": [
    {
      "name": "llama3.2:latest",
      "model": "llama3.2:latest",
      "modified_at": "2025-03-16T10:00:00.000Z",
      "size": 2147483648,
      "digest": "a80c4f17acd5...",
      "details": {
        "format": "gguf",
        "family": "llama",
        "parameter_size": "3B",
        "quantization_level": "Q4_K_M"
      }
    }
  ]
}
```

---

## Embeddings

**Endpoint:** `POST /api/embed`  
**Purpose:** Create vector embeddings for text (e.g. for RAG or semantic search).

### Request

```bash
curl http://localhost:11434/api/embed -d '{
  "model": "nomic-embed-text",
  "input": "Why is the sky blue?"
}'
```

For multiple texts:
```json
{
  "model": "nomic-embed-text",
  "input": ["Text 1", "Text 2", "Text 3"]
}
```

### Response

```json
{
  "model": "nomic-embed-text",
  "embeddings": [
    [0.01, -0.002, 0.05, ...]
  ],
  "total_duration": 14143917
}
```

---

## Pull Model

**Endpoint:** `POST /api/pull`  
**Purpose:** Download a model from the registry.

### Request

```bash
curl http://localhost:11434/api/pull -d '{
  "model": "llama3.2:latest",
  "stream": true
}'
```

---

## Streaming

By default, `/api/chat` and `/api/generate` stream responses as **NDJSON** (newline-delimited JSON). Each line is a JSON object.

### Streamed chunk example

```json
{"model":"gemma3","created_at":"2025-03-17T12:00:00.100Z","response":"That","done":false}
{"model":"gemma3","created_at":"2025-03-17T12:00:00.110Z","response":"'s","done":false}
{"model":"gemma3","created_at":"2025-03-17T12:00:00.120Z","response":" correct","done":false}
{"model":"gemma3","created_at":"2025-03-17T12:00:00.130Z","response":"!","done":true,"done_reason":"stop"}
```

### Disabling streaming

Set `"stream": false` in the request body to receive a single JSON response instead of a stream.

---

## Other Endpoints

| Endpoint       | Method | Description                    |
|----------------|--------|--------------------------------|
| `/api/show`    | POST   | Show model details             |
| `/api/copy`    | POST   | Copy a model                   |
| `/api/delete`  | DELETE | Delete a model                 |
| `/api/ps`      | GET    | List running models            |
| `/api/version` | GET    | Get Ollama version             |

---

## References

- [Ollama Official Docs](https://docs.ollama.com/)
- [Ollama API Introduction](https://docs.ollama.com/api)
- [Ollama Python Library](https://github.com/ollama/ollama-python)
