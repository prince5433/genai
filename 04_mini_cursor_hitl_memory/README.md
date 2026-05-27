# 04 Mini Cursor HITL Memory

This is a new project based on the idea of `03_mini_cursor`, but the original
project is not changed.

Features:
- LangGraph state machine
- LangGraph checkpointing with `MemorySaver`
- Restart persistence through `data/langgraph_state.json`
- Tools for reading files, writing files, and running commands
- Human-in-the-loop yes/no approval before complex actions
- `ask_human` tool for missing information or decisions
- Mem0 memory, with automatic in-memory fallback if local Qdrant storage fails
- Local knowledge graph saved in `data/knowledge_graph.json`

## Run

From `C:\Users\Prince\OneDrive\Desktop\GENAI`:

```powershell
python .\04_mini_cursor_hitl_memory\app.py
```

Or with your root venv:

```powershell
.\venv\Scripts\python.exe .\04_mini_cursor_hitl_memory\app.py
```

Make sure `OPENAI_API_KEY` is available in your environment or in a `.env` file.

## Commands Inside The App

```text
exit
clear memory
```

Memory is stored here:

```text
04_mini_cursor_hitl_memory\data\
```

Important files created at runtime:

```text
data\langgraph_state.json
data\knowledge_graph.json
data\mem0_history.db
data\qdrant\
```

The app first tries to persist Mem0 data under `data\`. If local Qdrant/SQLite
storage fails on Windows or OneDrive, it falls back to in-memory Mem0 for the
current run while still saving LangGraph state and the knowledge graph to disk.
