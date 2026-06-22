# 🧠 LLM (Large Language Model) — Complete Notes
> **Language:** Hinglish | **Format:** Study Notes

---

## 1. LLM Kya Hota Hai?

**LLM = Large Language Model**

- Ye ek AI model hota hai jo **text samajhta aur generate karta hai**
- Bahut badi dataset pe train hota hai — billions of words/tokens
- Examples: **GPT (OpenAI), Gemini (Google), Claude (Anthropic), DeepSeek, LLaMA**

### Popular LLMs:
| Provider | Model |
|----------|-------|
| OpenAI | GPT-4, GPT-4o |
| Google | Gemini |
| Meta | LLaMA |
| DeepSeek | DeepSeek-R1 |
| Anthropic | Claude |

---

## 2. Prompting

**Prompting = LLM ko sahi instruction dena**

- Jo hum LLM ko likhke dete hain → **Prompt** kehte hain
- Prompt jitna achha → Output utna better
- Types of prompting:
  - **Zero-shot** → Bina example diye seedha question
  - **Few-shot** → Kuch examples dekar question
  - **Chain-of-thought** → Step-by-step sochne ko kehna

> **Example:** "Tum ek helpful teacher ho. Mujhe Python loops samjhao simple Hindi mein."

---

## 3. Tooling — LLM ke Saath Tools

**Tooling = LLM ko extra capabilities dena**

- Sirf text generate karna kaafi nahi hota
- Tools attach karke LLM ko zyada powerful banate hain
- Examples of tools:
  - 🌐 Web Search
  - 🧮 Calculator
  - 📁 File Reader
  - 🌦️ Weather API

---

## 4. LLM → Agent

**Agent = LLM (Brain) + Planning + Memory + Tools**

- Jab LLM sirf response generate nahi karta, balki **apne aap decision lekar complex tasks complete karta hai**, toh use **Agent** kehte hain.
- Agent ek goal ke saath kaam karta hai aur zarurat padhne par alag-alag tools ko use karta hai.

### Core Components of an Agent:
1. **Brain (LLM):** Sochne aur decision lene ke liye.
2. **Planning:**
   - **Sub-goal decomposition:** Bade task ko chhote-chhote steps mein todna.
   - **ReAct (Reason + Act):** Pehle reason karna (sochna) fir act karna (tool chalana) aur output dekhkar agla step decide karna.
3. **Memory:**
   - **Short-term Memory:** Chat history ko yaad rakhna.
   - **Long-term Memory:** Vector Database ya RAG ke through purani information recall karna.
4. **Tools:** External APIs, Web Search, Python Calculator, Database Reader jo LLM ko direct computational power dete hain.

### Agent Flow:
```
User Request ──> LLM (Planning & Reasoning) ──> Tool Call (e.g., Search/API)
                                                    │
User ko Final Answer <── LLM (Analyze Results) <────┘
```

---

## 5. Inferencing vs Training

### Inferencing (Use karna):
- **Inferencing = Trained model se output lena**
- Jab hum ChatGPT se kuch poochte hain → Inferencing ho raha hai.
- Fast hota hai, inference pipelines optimized hoti hain.

### Training (Sikhana):
- **Training = Model ko data se seekhna sikhana**
- Bahut zyada compute (GPUs) aur massive raw text datasets chahiye.

| Feature | Training | Inferencing |
|---|---|---|
| **Purpose** | Naya model ya brain banana | Banaye hue model se kaam lena |
| **Cost** | Millions of dollars (Bahut zyada) | Kam (Pay per token/API cost) |
| **Time** | Weeks/Months lagte hain | Milliseconds/Seconds mein answer |

---

## 5.5 Fine-Tuning (Model Customization)

**Fine-Tuning = Kisi pre-trained model ko specific data par customize karna**

- **Kyoon karte hain?** Pre-trained models (jaise GPT-4, LLaMA) generic hote hain. Agar humein model ko specific legal documents, medical files, ya kisi proprietary programming language ke codes par expert banana hai, toh hum Fine-Tuning karte hain.
- **Pre-Training vs Fine-Tuning:**
  - *Pre-Training:* Model zero se seekhta hai (massive compute, high cost).
  - *Fine-Tuning:* Model pehle se English/Hindi/Maths seekha hua hai, bas hum use apne specific business data par train karke style, tone ya specific knowledge sikha rahe hain (kam data aur kam compute lagta hai).
- **Popular Techniques:**
  - **LoRA (Low-Rank Adaptation):** Isme poore model ke parameters ko train nahi kiya jata, balki model ke andar kuch extra chhote weight matrices add karke sirf unhe train kiya jata hai. Isse memory aur resource cost 90% tak kam ho jati hai.
  - **QLoRA:** LoRA ko quantized version (4-bit representation) ke sath run karna, jisse local ordinary GPUs par bhi bade models train ho sakein.

---

## 6. OpenAI — Inferencing (API ke through)

- OpenAI apna model **API ke through** provide karta hai
- Hum directly call karte hain:

```python
import openai

response = openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

- API key chahiye hoti hai
- Pay-per-use model hota hai (tokens pe charge)

---

## 7. Open Source LLM — Ollama se Local Run Karo

**Ollama = Apne computer pe LLM chalane ka tool**

- OpenAI ko paise dene ki zaroorat nahi
- Locally run hota hai — data bahar nahi jaata
- Privacy-friendly

### Install & Use:
```bash
# Model download karo
ollama pull deepseek

# Ya koi bhi model
ollama pull llama3
ollama pull mistral
```

### Architecture:
```
APP → Ollama → Models (DeepSeek, LLaMA, Mistral...)
```

- **APP** tumhara code/application hai
- **Ollama** ek local server ki tarah kaam karta hai
- **Models** alag-alag LLMs hain jo tum use kar sakte ho

---

## 8. APP → Ollama → Models (Detail)

Ollama ek loop mein kaam karta hai:

```
          ┌─────────────────────────────┐
          │   APP → Ollama → Models     │
          └──────────┬──────────────────┘
                     │
          ┌──────────▼──────────┐
          │  Request aata hai   │
          └──────────┬──────────┘
                     │
          ┌──────────▼──────────┐
          │  Model process karta│
          └──────────┬──────────┘
                     │
          ┌──────────▼──────────┐
          │  Response wapas     │
          └─────────────────────┘
```

**Ollama API** OpenAI jaisi hi hoti hai — same format, easy switch!

```python
import openai

# Sirf base_url change karo
client = openai.OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # Kuch bhi daal sakte ho
)

response = client.chat.completions.create(
    model="deepseek",
    messages=[{"role": "user", "content": "Namaste!"}]
)
```

---

## 9. Tokenizer — Text ko Numbers mein Todna

**Tokenizer = Text → Tokens (Numbers)**

- LLM directly text nahi samajhta — pehle **tokens** mein convert karta hai
- Token = word ka ek piece

### Example:
```
"Hello World"  →  [15496, 995]
"Namaste"      →  [7402, 5874, 83]
```

- Ek token ≈ 0.75 words
- OpenAI **tokens pe charge** karta hai isliye samajhna zaroori hai

### Tokenization Steps:
```
Raw Text
   ↓
Tokenizer (split into tokens)
   ↓
Token IDs (numbers)
   ↓
Transformer (LLM model)
   ↓
Output Token IDs
   ↓
DeTokenizer
   ↓
Human-readable Text
```

---

## 10. Transformer — LLM ka Dimaag

**Transformer = LLM ka core architecture**

- 2017 mein Google ne banaya — paper: *"Attention Is All You Need"*
- Aaj ke sabhi bade LLMs Transformer pe based hain
- Key concept: **Attention Mechanism** — har word dusre words ke saath connect hota hai

### Inside Transformer:
- **Encoder** → Input samajhta hai
- **Decoder** → Output generate karta hai
- **Attention** → Context samajhta hai

---

## 11. DeTokenizer — Numbers wapas Text mein

**DeTokenizer = Tokens → Text (wapas human language)**

- Transformer numbers output karta hai
- DeTokenizer unhe wapas readable text mein convert karta hai

```
Model Output: [7402, 995, 11, 1234]
      ↓
DeTokenizer
      ↓
"Hello World, response..."
```

---

## 12. Full Flow — Ek Saath Samjho

```
User Input (Text)
       ↓
   Tokenizer
       ↓
  Token IDs
       ↓
Transformer (LLM Model)
  — DeepSeek, GPT, LLaMA —
       ↓
Output Token IDs
       ↓
  DeTokenizer
       ↓
User ko Response (Text)
```

---

## 13. Quick Revision — Key Points

| Concept | Ek Line Mein |
|---|---|
| LLM | Bada AI model jo text samjhe aur likhe |
| Prompting | LLM ko sahi instruction dena |
| Tooling | LLM ko extra powers dena |
| Agent | LLM + Tools + Automatic actions |
| Inferencing | Trained model use karna |
| Training | Model ko data se sikhana |
| OpenAI API | Cloud pe LLM use karo (paid) |
| Ollama | Local pe LLM use karo (free) |
| Tokenizer | Text → Numbers |
| Transformer | LLM ka brain |
| DeTokenizer | Numbers → Text |

---

## 14. Practice Commands

```bash
# Ollama setup
ollama pull deepseek
ollama pull llama3
ollama list          # installed models dekho
ollama run llama3    # directly chat karo

# OpenAI API test (Python)
pip install openai
python -c "import openai; print('Ready!')"
```

---

> 📝 **Ye notes Excalidraw diagram se banaye gaye hain**
> Topics: LLM → Prompting → Tooling → Agents → Inferencing → Ollama → Tokenizer → Transformer → DeTokenizer