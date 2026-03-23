# Local AI Agent (Ollama)

A helpful AI assistant that runs **entirely on your computer**. Uses Ollama and a local LLM, with tools like `read_file` to read and explain file contents.

---

## Architecture

```
MyFIRSTAgent/
├── main.py              # Entry point - run the agent
├── agent/
│   ├── identity.py     # Agent identity & system prompt (who the agent is)
│   ├── llm.py          # LLM layer - isolated Ollama API calls
│   ├── memory.py       # Memory layer - conversation history
│   ├── run.py          # Agent loop - orchestrates LLM, memory, tools
│   └── tools/
│       ├── __init__.py  # Tool registry - execute_tool, get_tool_definitions
│       └── read_file.py # read_file tool - reads a file from disk
├── chatbot.py          # Legacy chatbot (no tools)
└── OLLAMA_API.md       # Ollama API reference
```

**Design:**
- **Identity**: Defines the agent as a helpful local assistant (no cloud, privacy-first).
- **LLM**: Isolated module—only talks to Ollama. No memory or tool logic.
- **Memory**: Isolated module—stores messages. No LLM or tool logic.
- **Tools**: Extensible. Each tool has a definition (for the LLM) and an executor.

---

## How It Works

1. **User input** → appended to `ConversationMemory`
2. **Agent loop** (`run.py`):
   - Sends messages + system prompt + tool definitions to Ollama (`llm.py`)
   - LLM responds with either:
     - **Text only** → that becomes the agent's reply
     - **Tool calls** → each tool is executed, results are added to memory, and the LLM is called again
3. **Tool execution** → `execute_tool(name, args)` runs the tool (e.g. `read_file`) and returns the result
4. **Tool results** → fed back to the LLM as `role: "tool"` messages
5. **Final response** → LLM produces text after tools run (or directly if no tools); shown to the user

**Data flow:**
```
User → Memory (append) → LLM (chat) → tool_calls? → Tools (execute) → Memory (append results) → LLM (chat) → User
```

---

## Quick Start

1. **Ensure Ollama is running** (it usually runs in the background).

2. **Run the agent:**
   ```powershell
   python main.py
   ```

3. **Try it:**
   ```
   You: Read and explain chatbot.py
   Agent: [Uses read_file tool, then explains the content]
   ```

4. **Exit:** Type `exit` or `quit`.

---

## Agent Identity

The agent is defined in `agent/identity.py`:

- Runs 100% on the user's machine (no cloud, no external APIs)
- Helpful, clear, and concise
- Privacy-first: everything stays on the user's computer
- Uses tools when asked (e.g., read files) and explains what it found

---

## Tools

| Tool        | Description                                      |
|-------------|--------------------------------------------------|
| `read_file` | Reads a file from disk. Use when the user asks to read, open, or explain a file. |

To add a tool: define it in `agent/tools/`, register in `agent/tools/__init__.py`.

---

## Model Selection

Default: `llama3.2:latest`. Use another model:

```powershell
python main.py gemma3:1b
```

**Note:** Tool calling requires models that support it (e.g., Llama 3.1+, Command-R+). If your model doesn't support tools, the agent will still work but won't call tools.

---

## Requirements

- Python 3.10+
- Ollama installed and running
- A local model (e.g., `ollama pull llama3.2:latest`)

---

## Troubleshooting

| Issue                         | Solution                                  |
|-------------------------------|-------------------------------------------|
| Cannot connect to Ollama      | Run `ollama serve`                        |
| Model not found               | `ollama pull llama3.2:latest`             |
| Slow responses                | Try smaller model: `gemma3:1b`            |
| Agent doesn't use tools       | Use a model with tool-calling support     |
