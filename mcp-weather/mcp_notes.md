# 🔌 MCP Server — Complete Notes (Hinglish)

> Model Context Protocol — Anthropic ne banaya, ab OpenAI, Claude, Google sab support karte hain.

---

## 1. MCP Kya Hai? (The Big Picture)

MCP ek **protocol** hai — matlab ek **set of rules** jo define karta hai ki AI model (like Claude) bahar ki duniya se kaise baat karega.

**Simple analogy:**
> Jaise HTTP ek protocol hai browser aur server ke beech, waise MCP ek protocol hai AI model aur tools/services ke beech.

```
AI Model (Claude/GPT) <---MCP---> External Tools (DB, Gmail, GitHub, APIs)
```

**Pehle kya hota tha?**
Har company apna alag "tool calling" system banati thi. Piyush ne khud ek hacky way nikala tha:
- System prompt mein likho ki ye tools available hain
- Agar tool call karna hai toh type karo: `action: <tool_name>`
- Next response mein output do

MCP ne ye sab **standardize** kar diya. ✅

---

## 2. MCP Architecture — Host, Client, Server

```
┌─────────────────────────────────────┐
│           MCP HOST                  │
│   (AI Based Project / Claude App)   │
│                                     │
│   ┌──────────┐                      │
│   │MCP Client│──────────────────────┼──► MCP Server A ──► DB, Web Search
│   └──────────┘                      │
│               ──────────────────────┼──► MCP Server B ──► File, API Call
└─────────────────────────────────────┘
```

| Component | Kya Hai | Example |
|-----------|---------|---------|
| **MCP Host** | Woh application jahan AI run ho raha hai | Claude Desktop, Cursor, tera custom app |
| **MCP Client** | Host ke andar ka component jo servers se baat karta hai | Built into the host |
| **MCP Server** | Ek alag process jo tools expose karta hai | Gmail MCP Server, GitHub MCP Server |

**Key Point:** Ek host multiple servers se connect ho sakta hai simultaneously.

---

## 3. MCP Server Kya Expose Karta Hai?

MCP Server teen cheezein provide kar sakta hai:

```
MCP Server
├── Tools         ← Functions jo AI call kar sakta hai (e.g., send_email)
├── Prompts       ← Pre-built prompt templates
└── Sample Prompts ← (Mostly nahi use hota practically)
```

**Sabse important: Tools** — ye woh functions hain jo model actually execute karta hai.

---

## 4. Real World Example — Gmail MCP

**Scenario:** "Merko Gmail se email send karna hai"

```
User Prompt
    │
    ▼
MCP Server (Google/Gmail)
    │  exposes: send_email(from, to, subject, body)
    │
    ▼
AI Model decides to call this tool
    │
    ▼
Gmail API ──► gmail.sendEmail() ──► Email sent ✅
```

**Install karna hai?**
```bash
pip install gmail-mcp
```

Bas! Ab Claude/GPT directly Gmail se email bhej sakta hai.

---

## 5. MCP Transports — Client-Server Communication Kaise Hoti Hai?

MCP Client aur MCP Server ke beech data travel karta hai **Transports** ke through.

### 2 Main Transports:

#### Transport 1: STDIO (Standard Input/Output)
```
MCP Client ◄──── stdio ────► MCP Server
                              │
                         Local Machine pe run hota hai
```

- **printf("Hello ji")** → output standard terminal pe jaata hai
- **input("")** → standard terminal se input leta hai
- Local machine pe run hota hai
- Simple, fast, no networking needed

**Use case:** Jab server aur client same machine pe hoon (e.g., Claude Desktop + local MCP server)

#### Transport 2: SSE (Server-Sent Events)
```
MCP Client ◄──────────────────────► MCP Server (hosted)
           GET  /sse               (Server SE Response)
           POST /message  ◄──────── command: list_tools
                                   (POST Request = Command)
```

- Server remotely hosted ho sakta hai (e.g., `mcp.piyushgarg.dev`)
- `/sse` endpoint pe server **push** karta hai responses
- `/message` endpoint pe client **POST** karta hai commands
- Server pr host kar sakte ho — multiple clients connect ho sakte hain

**Ho Sakta Hai (but rare):**
- HTTP
- WebSocket
- UDP

---

## 6. Tool Discovery & Calling Flow

```
Step 1: list_tools
Claude ──────────────► MCP Server
       ◄──────────────
       list_of_tools and their descriptions

Step 2: Tool Call
Claude ──► add_number(2, 5) ──► MCP Server calculates ──► returns 7

Step 3: Claude responds
"Hey, the result is 7" ──► User
```

**Real example diagram:**
```
claude: add_number(a, b)
   └──► 7 ◄──── command: add_number 2, 5
                     add_number(2, 5) executes on server
```

---

## 7. MCP Server Kis Language Mein Banate Hain?

Officially support hai:
- **TypeScript** ✅ (most popular)
- **Python** ✅

Dono mein SDK available hai Anthropic ka.

---

## 8. MCP.json — Configuration File

Jaise `package.json` node project ka config hota hai, waise **`MCP.json`** mein define karte ho ki kaunse MCP servers use karne hain.

```json
{
  "servers": {
    "github": "...",
    "gmail": "...",
    "microsoft": "..."
  }
}
```

Claude Desktop ya koi bhi MCP host is file ko read karta hai aur servers se connect ho jaata hai.

---

## 9. Side Project Idea — Real Time Stock Market Data

Whiteboard pe ek interesting side project tha:

```
Real Time Stock Market Data
         │
         ▼
      REST API
    /api/server
         │
    ┌────┴────┐
    │         │
Frontend    MCP Server
              │
         def tool(stock: str):
             http.call('/api/server')
             return <data>
              │
              ▼
         AI can now query live stock prices!
```

**Idea:** Ek REST API banao jo stock data de, phir uske upar ek MCP Server wrap karo. Ab Claude directly stock prices query kar sakta hai!

---

## 10. OAuth 2.0 — MCP ke saath Auth

Jab MCP Server ko Google/GitHub/Microsoft se connect karna hota hai, toh **OAuth 2.0** flow use hota hai:

```
User ──► Login with Google/GitHub/Microsoft
              │
              ▼ redirect
         Authorization Server
              │
              ▼ code
         Your App receives code
              │
              ▼ code → token
         Exchange code for access token
              │
              ▼ token → info
         Use token to access user info/APIs
```

**Steps:**
1. Redirect to provider
2. Get `code` back
3. Exchange `code` → `token`
4. Use `token` → get user info

---

## 11. HTTP vs TCP — Quick Revision

```
HTTP  ◄─────────────────► TCP
      (headers, body,
       status code)

HTTP is built ON TOP of TCP
```

MCP STDIO wala local pe TCP jaisa hai, SSE wala HTTP pe.

---

## 12. Key Takeaways 🎯

| Point | Summary |
|-------|---------|
| MCP kya hai | Protocol to connect AI with external tools |
| Banaya kisne | Anthropic (but now OpenAI, Google sab adopt kar rahe hain) |
| 3 components | Host → Client → Server |
| Server expose karta hai | Tools, Prompts, Sample Prompts |
| 2 Transports | STDIO (local) aur SSE (remote/hosted) |
| Config file | MCP.json |
| Languages | TypeScript, Python |
| Auth | OAuth 2.0 |
| Tool flow | list_tools → select tool → call → get result → AI responds |

---

## 13. Analogy Summary 🧠

> **MCP = USB Standard for AI**
>
> Jaise USB ek standard hai — koi bhi device USB port mein laga lo aur kaam karo, waise MCP ek standard hai — koi bhi MCP Server banao aur kisi bhi AI (Claude, GPT, Gemini) se connect karo. No custom integration needed!

---

*Notes based on: Chai aur Code / Piyush Garg MCP Session whiteboard*