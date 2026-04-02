# 📘 Prompt Engineering

**Complete Study Notes**
GIGO  •  Tokens  •  Prompting Techniques  •  Pricing

---

## 1. GIGO — Garbage In, Garbage Out

The quality of AI output is directly determined by the quality of the input prompt. Poor prompts produce poor responses.

Garbage Input — Vague, unclear, or poorly structured prompt

Garbage Output — Irrelevant, inaccurate, or useless response from the model

Key principle: If you give the model bad instructions, it will produce bad results — no matter how powerful the model is.

---

## 2. Tokens — How AI Processes Text

LLMs do not read words — they process tokens. A token is roughly a word or a piece of a word.

### 2.1 What are tokens?

• Text is split into tokens before being sent to the model
• A token is approximately 3/4 of a word in English
• Numbers, punctuation, and rare words may be split into multiple tokens

Tokens [ 1, 2, 3, 4, 5, 6 ]
After encoding:  [ a, b, c, 4, 5, 6 ]

---

### 2.2 Initial context tokens

Every conversation starts with initial context — tokens that are always present before the user types anything:

• System prompt tokens
• Any initial context or instructions
• Tool descriptions (if applicable)

---

### 2.3 How pricing works

You are charged for every token processed — both what you send and what the model generates:

Charge = Input Tokens + Output Tokens — Every token going in and coming out is billed

| Token Type    | Counts As                    | Notes                          |
| ------------- | ---------------------------- | ------------------------------ |
| Input tokens  | System prompt + user message | Charged per token              |
| Output tokens | Model response               | Charged per token              |
| Total charge  | Input + Output               | Charge = Input + Output Tokens |

---

## 3. Prompt Formats / Styles

Different models are fine-tuned with different prompt formats. Using the correct format for a given model significantly improves output quality.

| Format          | Structure                              | Example                                                                                             |
| --------------- | -------------------------------------- | --------------------------------------------------------------------------------------------------- |
| Alpaca          | Instructions / Input / Response format | Instructions: For the given number by user perform Input: what is 2 + 2 Response:                   |
| INST (LLaMA-2)  | Wrap user message with [INST] tags     | [INST] What is an LRU Cache? [/INST]                                                                |
| ChatML (OpenAI) | JSON role/content message format       | { role: "system", content: "You are an assistant" } { role: "user", content: "what is LRU Cache?" } |

---

### 3.1 Alpaca Prompt

Structured format with clear sections for instruction, input, and expected response:

Instructions:
For the given number by user perform

Input: what is 2 + 2

Response:

---

### 3.2 INST Format (LLaMA-2)

Wraps the user's message in special tokens to distinguish it from the model's response:

[INST] What is an LRU Cache? [/INST]

---

### 3.3 ChatML Format (OpenAI)

Uses a JSON-style role/content structure — the format used by GPT models and the OpenAI API:

{ role: "system", content: "You are an assistant" }
{ role: "user",   content: "what is LRU Cache?" }

---

## 4. Prompting Techniques

Prompting techniques are structured approaches to writing prompts that reliably produce better outputs. These can be combined for complex tasks.

---

### 1. Zero-shot Prompting

The model is given a direct question or task without any prior examples. Relies entirely on the model's pre-trained knowledge.

Example: Translate 'Hello' to French.

---

### 2. Few-shot Prompting

A few examples are provided before asking the model to complete a similar task. The model learns the pattern from the examples.

Example:
Q: 2+2? A: 4 | Q: 3+3? A: 6 | Q: 5+5? A:

---

### 3. Chain-of-Thought (CoT) Prompting

The model is asked to reason step-by-step before arriving at an answer. Dramatically improves accuracy on complex tasks.

Example:
Q: Is 9.11 > 9.8? Think step by step.
A: 9.11 = 9 + 0.11; 9.8 = 9 + 0.80; 0.11 < 0.80 so 9.8 is greater.

---

### 4. Self-Consistency Prompting

The model generates multiple independent responses to the same query, then selects the most consistent or common answer. Reduces hallucination.

Example:
Query: What is greater? 9.8 or 9.11 (ask 3 times, pick most common answer)

---

### 5. Instruction Prompting

The model is explicitly instructed to follow a particular format, guideline, or process. Often uses structured templates.

Example: Always respond in JSON. Always start with a greeting. Never mention competitors.

---

### 6. Direct Answer Prompting

The model is asked to give a concise, direct response without explanation or reasoning steps. Good for quick factual lookups.

Example: What is the capital of France? Answer in one word.

---

### 7. Persona-based Prompting

The model is instructed to respond as if it were a particular character, expert, or professional, including their tone and style.

Example: You are Hitesh sir. Tone: Hinglish. Respond as he would — Hanji!

---

### 8. Role-Playing Prompting

The model assumes a specific functional role and interacts accordingly throughout the conversation.

Example: You are an AI coding assistant who is expert in teaching how to code.

---

### 9. Contextual Prompting

The prompt includes relevant background information, prior context, or domain knowledge to improve the quality of the response.

Example: Given: user is a beginner in Python. They asked: 'what is a list?' Explain simply.

---

### 10. Multimodal Prompting

The model is given a combination of modalities — text, images, audio, or other data — to generate a response.

Example: [Image of a dog] + 'What breed is this dog?'

---

## 5. Combining Techniques

Techniques can and should be combined for best results on complex, real-world tasks:

* CoT + Persona + Role — Reason step by step, as a senior engineer who teaches beginners, acting as a coding tutor.

* Few-shot + CoT — Provide examples that each show the step-by-step reasoning, not just the final answer.

* Instruction + Persona — Set the output format (JSON, markdown) while also setting a persona for tone and expertise.

---

## 6. System Prompt

The system prompt is the initial, hidden instruction given to the model before any user interaction. It sets the model's behavior for the entire conversation.

system prompt
user input
↓
Output

System prompt components typically include:

• Role / persona definition
• Tone and language instructions
• Output format requirements
• Topics to avoid or focus on
• Example interactions (few-shot)

---

## 📌 Quick Reference Summary

| Technique        | When to use                  | Key benefit                   |
| ---------------- | ---------------------------- | ----------------------------- |
| Zero-shot        | Simple, direct tasks         | Fast, no examples needed      |
| Few-shot         | Pattern-based tasks          | Teaches by example            |
| Chain-of-Thought | Math, logic, reasoning       | Accurate step-by-step answers |
| Self-Consistency | Critical / uncertain queries | Reduces hallucination         |
| Instruction      | Formatted outputs            | Enforces structure            |
| Direct Answer    | Quick factual lookups        | Concise responses             |
| Persona-based    | Tone / style matching        | Consistent character          |
| Role-Playing     | Domain expertise tasks       | Contextual expertise          |
| Contextual       | Background-heavy queries     | Better relevance              |
| Multimodal       | Image + text tasks           | Cross-modal understanding     |

---

## End of Notes


## extra notes by me
## agr hm kisi model ko usi ke dwara generate koya huwa prompt denge to kya hoga? to result hame bekar milega because hamne jo input dalke output nikala model kabhi wpas us output ko input ke roop m train nahi kiya hoga. isliye jab bhi ham prompt banate hai to hame dhyan rakhna chahiye ki hamara prompt clear, specific, aur well-structured ho taki model uska sahi se samajh sake aur hame accha output de sake.



