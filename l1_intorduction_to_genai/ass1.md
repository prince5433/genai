# Complete AI/LLM Concepts — Deep Notes (Hinglish) 🧠

> **GenAI Cohort** | Piyush Garg & Hitesh Sir  
> Yeh notes un sab topics ko cover karte hain jo ek LLM (jaise GPT) ke andar hote hain.

---

## 📑 Table of Contents

1. [Transformers](#1-transformers)
2. [Encoder](#2-encoder)
3. [Decoder](#3-decoder)
4. [Vectors](#4-vectors)
5. [Embeddings](#5-embeddings)
6. [Positional Encoding](#6-positional-encoding)
7. [Semantic Meaning](#7-semantic-meaning)
8. [Self Attention](#8-self-attention)
9. [Softmax](#9-softmax)
10. [Multi-Head Attention](#10-multi-head-attention)
11. [Temperature](#11-temperature)
12. [Knowledge Cutoff](#12-knowledge-cutoff)
13. [Tokenization](#13-tokenization)
14. [Vocab Size](#14-vocab-size)

---

## 1. Transformers

### Kya Hai? 🤔
**Transformer ek neural network architecture hai** jo 2017 mein Google ne introduce ki thi ek paper mein:

> **"Attention is All You Need"** — Google Brain, 2017

Yeh paper **Google Translate** ko better karne ke liye banaya gaya tha — lekin iss architecture ne poori AI ki duniya badal di.

### Kyun Important Hai?
Transformer se pehle **RNN (Recurrent Neural Networks)** aur **LSTM** use hote the.

**Problem thi:**
- RNN ek word ek baar process karta tha — slow!
- Lambi sentences mein pehle wale words "bhool" jaata tha
- Parallel processing nahi ho sakti thi

**Transformer ne solve kiya:**
- Saare words **ek saath (parallel)** process karo
- Koi bhi word kisi bhi doosre word pe **directly attention** de sakta hai
- Bahut fast, bahut powerful

### Architecture Overview

```
Input Text
    ↓
Tokenization
    ↓
Embeddings + Positional Encoding
    ↓
┌─────────────────────────────┐
│     ENCODER STACK           │  ← N layers (N=6 original paper mein)
│  Multi-Head Attention       │
│  Feed Forward Network       │
│  Layer Normalization        │
└─────────────────────────────┘
             ↓
┌─────────────────────────────┐
│     DECODER STACK           │  ← N layers
│  Masked Multi-Head Attention│
│  Cross-Attention            │
│  Feed Forward Network       │
└─────────────────────────────┘
    ↓
Linear Layer + Softmax
    ↓
Output Token
```

### Kaun Kaun Use Karta Hai Transformer?

| Model | Company | Type |
|-------|---------|------|
| GPT-4 | OpenAI | Decoder only |
| Claude | Anthropic | Decoder only |
| BERT | Google | Encoder only |
| T5 | Google | Encoder + Decoder |
| LLaMA | Meta | Decoder only |
| Gemini | Google | Decoder only |

> 💡 **Aaj ki date mein sabse popular LLMs Decoder-only Transformers hain.**

---

## 2. Encoder

### Kya Kaam Karta Hai? 📥
**Encoder ka kaam hai: Input ko samajhna aur uska ek rich representation banana.**

Simple words mein: Encoder **"reader"** hai — padho aur samjho.

### Kaise Kaam Karta Hai?

```
Input: "The cat sat on the mat"
           ↓
    [Token IDs: 1, 10, 76, 4, 1, 8]
           ↓
    [Embeddings + Positional Encoding]
           ↓
    [Self Attention — har word dusre se baat karta hai]
           ↓
    [Feed Forward Network]
           ↓
    Context-rich vectors output  ← yeh "understanding" hai
```

Output mein har token ka vector ab sirf apna matlab nahi, balki **poore sentence ke context mein apna matlab** represent karta hai.

### Example — "Bank" word:

```
Sentence 1: "I went to the river bank"
Sentence 2: "I went to the ICICI bank"

Encoder ke baad:
- "bank" in S1 → vector [0.2, 0.9, 0.1, ...]  ← river/nature context
- "bank" in S2 → vector [0.8, 0.1, 0.9, ...]  ← finance context

Same word, alag vectors!  ✅
```

Yahi Encoder ki power hai — **context-aware representation**.

### Encoder-only Models
- **BERT** (Bidirectional Encoder Representations from Transformers)
- Best for: Classification, NER, Sentiment Analysis, Search
- Dono directions se (left-to-right AND right-to-left) padhta hai

### Encoder Code Analogy
```python
class Encoder:
    def encode(self, text: str) -> list[float]:
        """
        Text → context-aware vector representation
        "The cat sat" → [0.23, 0.87, 0.12, 0.56, ...]
        """
        tokens = tokenize(text)
        embeddings = embed(tokens)
        return self_attention(embeddings)
```

---

## 3. Decoder

### Kya Kaam Karta Hai? 📤
**Decoder ka kaam hai: Output generate karna — ek ek token karke.**

Simple words mein: Decoder **"writer"** hai — jo samajha usse likhna shuru karo.

### Kaise Kaam Karta Hai?

```
Input (prompt): "My name is"
                    ↓
           [Decoder process karta hai]
                    ↓
          Next token predict: "Piyush" (probability: 0.87)
                    ↓
Input becomes: "My name is Piyush"
                    ↓
          Next token predict: "." (probability: 0.72)
                    ↓
Input becomes: "My name is Piyush."
                    ↓
          Next token: "<end>" → STOP
```

Yeh process **Autoregressive Generation** kehlaata hai.

### Masked Attention — Decoder Ka Special Feature

Decoder mein **Masked Self-Attention** hoti hai:

```
"My name is Piyush"

Jab "is" process ho raha hai:
✅ "My" dekh sakta hai
✅ "name" dekh sakta hai
✅ "is" khud ko dekh sakta hai
❌ "Piyush" NAHI dekh sakta (future token hai!)
```

**Kyun masking?** — Kyunki real generation mein future tokens exist nahi karte. Training ko realistic banana ke liye masking use hoti hai.

### Decoder-only vs Encoder-Decoder

```
GPT (Decoder only):
Prompt → [Decoder] → Response
Best for: Text generation, chatbots, coding

Google Translate (Encoder + Decoder):
Hindi → [Encoder] → [middle representation] → [Decoder] → English
Best for: Translation, summarization
```

### Decoder ka Flow (GPT style):
```
<start> token
    ↓
Token 1 generate
    ↓
Token 1 + <start> → Token 2 generate
    ↓
Token 1 + Token 2 + <start> → Token 3 generate
    ↓
...jab tak <end> na aaye
```

---

## 4. Vectors

### Kya Hota Hai Vector? 📐
**Vector = numbers ki ek ordered list**

Mathematics mein: `[1.2, -0.5, 3.4, 0.8]` — yeh ek 4-dimensional vector hai.

AI mein: **Har cheez ko vector mein represent karte hain** — words, sentences, images, sab kuch!

### Kyun Vectors?
Machine numbers samajhti hai, words nahi.

```
"cat"   → Machine samajh nahi sakti ❌
[0.2, 0.8, -0.3, 0.5]  → Machine samajh sakti hai ✅
```

### 2D Vector Example (Simplified)

```
       Royalty
         |
King ●   |   ● Queen
         |
─────────┼─────────  Gender
         |          (Male ← → Female)
Man  ●   |   ● Woman
         |
```

Agar hum plot karein:
- King: (Male=0.9, Royalty=0.9)
- Queen: (Female=0.9, Royalty=0.9)
- Man: (Male=0.9, Royalty=0.1)
- Woman: (Female=0.9, Royalty=0.1)

**King - Man + Woman:**
```
[0.9, 0.9] - [0.9, 0.1] + [0.1, 0.9]
= [0.9-0.9+0.1, 0.9-0.1+0.9]
= [0.1, 1.7]
≈ Queen! ✅
```

### Real Model Mein Vectors

| Model | Vector Dimensions |
|-------|------------------|
| GPT-2 small | 768 |
| GPT-3 | 12,288 |
| GPT-4 (estimated) | ~25,000+ |
| BERT base | 768 |

Yeh dimensions mein relationships store hoti hain: gender, royalty, tense, sentiment, aur hazaaron aur cheezein.

### Vector Operations Jo Useful Hain

```python
# Cosine Similarity — do vectors kitne similar hain?
# 1 = same direction, 0 = perpendicular, -1 = opposite

similarity("cat", "dog")    → 0.85  (similar — dono animals)
similarity("cat", "car")    → 0.12  (different)
similarity("king", "queen") → 0.92  (similar)
```

---

## 5. Embeddings

### Kya Hain Embeddings? 🧩
**Embeddings = tokens ko meaningful vectors mein convert karna — jisme semantic relationships bhi captured hon.**

Simple vector sirf ek number assign karta hai (cat=10, dog=11).  
**Embedding ek rich multi-dimensional representation** hai jisme meaning bhi hoti hai.

### Token → Embedding Process

```
Token ID: 10 ("cat")
    ↓
Embedding Matrix lookup
[Row 10 nikalo]
    ↓
[0.23, -0.45, 0.87, 0.12, -0.33, ...]  ← 768 numbers
```

**Embedding Matrix** ek badi table hoti hai:
- Rows = vocab size (jitne tokens hain)
- Columns = embedding dimensions

```
Embedding Matrix (simplified):
         dim1   dim2   dim3   dim4
"the"  [ 0.1,  -0.2,   0.5,  0.3]
"cat"  [ 0.8,   0.3,  -0.1,  0.9]
"sat"  [-0.2,   0.7,   0.4, -0.5]
"on"   [ 0.0,  -0.1,   0.2,  0.1]
"mat"  [ 0.7,   0.4,  -0.2,  0.8]
```

### Static vs Contextual Embeddings

```
Static (Word2Vec, old method):
"bank" hamesha ek hi vector
[0.5, 0.3, 0.8, ...]  — chahe context koi bhi ho

Contextual (BERT, GPT — modern):
"river bank"  → [0.2, 0.9, 0.1, ...]
"ICICI bank"  → [0.8, 0.1, 0.9, ...]
Same word, different context, DIFFERENT vector ✅
```

### Training Mein Embeddings Kaise Seekhi Jaati Hain?

```
Initially: Random vectors
    ↓
Model training shuru
    ↓
Loss calculate hota hai
    ↓
Backpropagation: Embedding values bhi update hoti hain
    ↓
Billions of examples ke baad...
    ↓
Meaningful embeddings! "cat" aur "dog" close hain,
"cat" aur "rocket" door hain.
```

### Embedding Ka Use

```python
import numpy as np

# Yeh real embeddings nahi hain — conceptual example
king   = np.array([0.9, 0.9, 0.1])   # [royalty, male, young]
queen  = np.array([0.9, 0.1, 0.1])   # [royalty, female, young]
man    = np.array([0.1, 0.9, 0.5])   # [normal, male, middle]
woman  = np.array([0.1, 0.1, 0.5])   # [normal, female, middle]

# King - Man + Woman ≈ Queen
result = king - man + woman
# result ≈ queen vector!
```

---

## 6. Positional Encoding

### Problem Kya Thi? 🤷
Transformer mein saare tokens **parallel** process hote hain — iska matlab position ki koi information nahi!

```
"Dog bites man"   → tokens: [dog, bites, man]
"Man bites dog"   → tokens: [dog, bites, man]  ← same tokens!
```

Agar position na pata ho toh model dono ko same samjhega — yeh toh galat hai!

### Solution: Positional Encoding 📍
Har token ke embedding mein **position information add karo**.

```
Final Input = Token Embedding + Positional Encoding

"cat" at position 2:
Token Embedding:     [0.8,  0.3, -0.1,  0.9]
Positional Encoding: [0.0,  1.0,  0.0,  1.0]  ← position 2 ke liye
                   + ────────────────────────
Final Vector:        [0.8,  1.3, -0.1,  1.9]
```

### Original Paper Mein Formula (Sine/Cosine)

```
PE(pos, 2i)   = sin(pos / 10000^(2i/d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))

Jahan:
- pos = word ki position (0, 1, 2, ...)
- i = dimension index
- d_model = embedding size
```

**Kyun Sine/Cosine?**
- Values hamesha -1 to 1 ke beech rahti hain
- Har position ka unique pattern hota hai
- Model relative positions (2 positions apart) bhi samajh sakta hai

### Learnable Positional Encoding (Modern Approach)

Aajkal kai models **learnable** positional encodings use karte hain:

```
Initially: Random positional vectors
    ↓
Training ke dauran seekhte hain
    ↓
Best positions automatically discover ho jaati hain
```

GPT-2, GPT-3 yahi approach use karte hain.

### Positional Encoding Ka Effect

```
Sentence: "The cat sat on the mat"

"The" (pos=0): embedding + PE(0) → [...]
"cat" (pos=1): embedding + PE(1) → [...]
"sat" (pos=2): embedding + PE(2) → [...]
"on"  (pos=3): embedding + PE(3) → [...]
"the" (pos=4): embedding + PE(4) → [...]  ← same word "the" but different position!
"mat" (pos=5): embedding + PE(5) → [...]
```

Ab model jaanta hai:
- "The" position 0 pe hai aur "the" position 4 pe hai
- Dono alag roles play kar rahe hain sentence mein

---

## 7. Semantic Meaning

### Kya Hai Semantic Meaning? 💬
**Semantic Meaning = Kisi word ya sentence ka actual, contextual meaning — sirf literal nahi.**

**Syntactic (literal):** Word ka dictionary meaning  
**Semantic (contextual):** Word ka context mein actual meaning

### Examples:

**Example 1 — Same word, alag meaning:**
```
"I went to the bank"
→ Kaun sa bank? River bank ya SBI bank?
→ Context dekhe bina answer possible nahi!

"I went to the bank to fish"    → river bank  🎣
"I went to the bank to withdraw"  → financial bank  💰
```

**Example 2 — Same meaning, alag words:**
```
"He is happy"
"He is joyful"
"He is elated"
→ Teeno ka semantic meaning similar hai!
→ Vector space mein teeno close honge
```

**Example 3 — Sarcasm:**
```
"Oh great, another Monday!"
→ Literal: "Great" = positive
→ Semantic: Actually frustrated hai!
→ Context se samjho
```

### AI Mein Semantic Meaning Kaise Capture Hoti Hai?

```
Steps:
1. Tokenization → words ko IDs
2. Embeddings → IDs ko vectors
3. Self Attention → context dekho
4. Ab vector mein semantic meaning bhi hai!

"bank" in "river bank":
Before attention: [0.5, 0.3, 0.8]  ← generic bank vector
After attention:  [0.2, 0.9, 0.1]  ← river context add hua

"bank" in "ICICI bank":
Before attention: [0.5, 0.3, 0.8]  ← generic bank vector
After attention:  [0.8, 0.1, 0.9]  ← finance context add hua
```

### Semantic Search (Real-world use)

```
Query: "cheap flights to Mumbai"
↓
Semantic Search finds:
✅ "affordable air travel to Bombay"  ← same meaning, different words
✅ "budget airlines Mumbai route"
❌ "Mumbai local train pass"  ← different meaning

Traditional keyword search would miss the first two!
```

---

## 8. Self Attention

### Concept Kya Hai? 🎯
**Self Attention = Har token decide karta hai ki sentence ke doosre konse tokens uske liye important hain.**

Yeh mechanism model ko **relationships** samajhne mein help karta hai.

### Simple Example

```
Sentence: "The animal didn't cross the street because it was too tired"

"it" refers to kya? → "animal" ya "street"?

Self Attention mechanism:
- "it" → "animal" pe high attention (yahi correct hai!)
- "it" → "street" pe low attention
- "it" → "tired" pe medium attention (kyunki tired = animal)
```

Human bhi yahi karta hai — "it" padte waqt peeche jaake dekhte hain ki kis ke baare mein baat ho rahi hai!

### Q, K, V — Query, Key, Value 🔑

Self Attention teen vectors use karta hai har token ke liye:

```
Har token se teen vectors banate hain:
Q (Query)  = "Main kya dhoondh raha hoon?"
K (Key)    = "Main kyaa offer kar sakta hoon?"
V (Value)  = "Agar match hua toh kya information doon?"
```

**Real-world analogy — YouTube Search:**
```
Q (Query)  = "python tutorial" (jo tum search kar rahe ho)
K (Key)    = Video titles, tags (jo har video offer karta hai)
V (Value)  = Actual video content (jo tum dekhoge agar match hua)

Attention Score = Q · K (dot product)
Output = sum of (attention_score × V)
```

### Step-by-Step Process

**Step 1: Q, K, V matrices banao**
```
Input: "The cat sat"
       [X_the, X_cat, X_sat]  ← input vectors

Q = X × W_Q  (Query weight matrix se multiply)
K = X × W_K  (Key weight matrix se multiply)
V = X × W_V  (Value weight matrix se multiply)
```

**Step 2: Attention Scores Calculate Karo**
```
Score(Q, K) = Q × K^T

Example (3 tokens):
        The    cat    sat
The  [ 0.8,   0.2,   0.1 ]  ← "The" ka attention distribution
cat  [ 0.1,   0.9,   0.3 ]  ← "cat" ka attention distribution
sat  [ 0.2,   0.7,   0.8 ]  ← "sat" ka attention distribution
```

**Step 3: Scale karo**
```
Scores = Scores / √(d_k)
d_k = key vector ki dimension

Kyun scale? — Agar dimensions bahut zyada hain toh
dot product bahut bada ho jaata hai → gradients vanish ho jaate hain
```

**Step 4: Softmax lagao**
```
Attention Weights = Softmax(Scores)

Ab har row sum to 1 hogi:
        The    cat    sat
The  [ 0.70,  0.20,  0.10 ]  ← sum = 1.0
cat  [ 0.08,  0.75,  0.17 ]  ← sum = 1.0
sat  [ 0.15,  0.45,  0.40 ]  ← sum = 1.0
```

**Step 5: Values se multiply karo**
```
Output = Attention_Weights × V

"sat" ki final representation:
= 0.15 × V_the + 0.45 × V_cat + 0.40 × V_sat
= mostly "cat" ki information + thodi "sat" ki = "sat" context mein "cat" ke saath hai
```

### Formula Summary

```
Attention(Q, K, V) = Softmax(QK^T / √d_k) × V
```

Yeh ek line hai lekin bahut powerful hai!

---

## 9. Softmax

### Kya Hai Softmax? 📊
**Softmax ek mathematical function hai jo raw numbers (logits) ko probability distribution mein convert karta hai.**

Properties:
- Saare outputs 0 aur 1 ke beech hote hain
- Saare outputs ka sum = **exactly 1.0 (100%)**

### Simple Example

```
Raw scores (logits): [2.0, 1.0, 0.1]
                       ↓
           Softmax apply karo
                       ↓
Probabilities: [0.659, 0.242, 0.099]
               ↑ sabse zyada → yeh token choose hoga (likely)
```

Verify: 0.659 + 0.242 + 0.099 = **1.000** ✅

### Formula

```
Softmax(x_i) = e^(x_i) / Σ e^(x_j)

Jahan:
- e = Euler's number (~2.718)
- x_i = current score
- Σ e^(x_j) = sab scores ka e^x ka sum
```

**Manual Calculation:**
```
Scores: [2.0, 1.0, 0.1]

Step 1: e^ of each
e^2.0 = 7.389
e^1.0 = 2.718
e^0.1 = 1.105
Sum   = 11.212

Step 2: Divide each by sum
7.389 / 11.212 = 0.659
2.718 / 11.212 = 0.242
1.105 / 11.212 = 0.099

Result: [0.659, 0.242, 0.099] ✅
```

### Softmax Kahan Kahan Use Hota Hai?

```
1. Self Attention mein:
   Attention scores → Softmax → Attention weights (0 to 1)

2. Final output layer mein:
   Vocab pe raw scores → Softmax → Next token ki probability

3. Classification tasks mein:
   [0.1, 3.2, 1.5] → [0.05, 0.86, 0.09]
   Classes: [cat, dog, bird] → model ko 86% lagta hai "dog" hai
```

### Temperature Ka Softmax Pe Effect (Preview)

```python
def softmax_with_temp(scores, temperature=1.0):
    scaled = [s / temperature for s in scores]
    exp_scores = [e^s for s in scaled]
    total = sum(exp_scores)
    return [e/total for e in exp_scores]

scores = [2.0, 1.0, 0.1]

temp=0.5 (cold):  [0.88, 0.11, 0.01]  ← confident, deterministic
temp=1.0 (normal):[0.66, 0.24, 0.10]
temp=2.0 (hot):   [0.46, 0.34, 0.20]  ← less confident, more random
```

---

## 10. Multi-Head Attention

### Problem With Single Attention 🤔
Ek attention mechanism ek type ki relationship seekhta hai.

**Lekin ek sentence mein kai tarah ke relationships hote hain:**
```
"The animal didn't cross the street because it was too tired"

Relationship 1: "it" → "animal" (pronoun resolution)
Relationship 2: "cross" → "street" (verb-object)
Relationship 3: "tired" → "didn't cross" (reason-consequence)
```

Ek attention head yeh sab ek saath efficiently nahi seekh sakta!

### Solution: Multiple Heads Parallel Mein! 🎭

```
Input Embeddings
        ↓
   Split into h heads
   ↙    ↓    ↓    ↘
Head1  Head2  Head3  Head4  ...Head_h
(Q1,K1,V1) (Q2,K2,V2) ...
   ↓       ↓      ↓      ↓
Attn1   Attn2   Attn3  Attn4
   ↘       ↓      ↓    ↙
       Concatenate
            ↓
     Linear Projection
            ↓
     Final Output
```

### Har Head Kya Seekhta Hai?

```
Head 1: Syntax relationships (subject-verb agreement)
Head 2: Coreference resolution ("it" = "animal")
Head 3: Long-range dependencies
Head 4: Local context (neighboring words)
...and so on
```

(Yeh exact nahi hai — model khud decide karta hai kya seekhna hai)

### Formula

```
MultiHead(Q, K, V) = Concat(head_1, ..., head_h) × W_O

jahan head_i = Attention(Q×W_Q_i, K×W_K_i, V×W_V_i)

Aur:
- h = number of heads (GPT-3 mein 96 heads!)
- d_k = d_model / h (dimension per head)
```

### Dimensions Ka Math

```
GPT-3 example:
d_model = 12,288  (total embedding size)
h = 96            (number of heads)
d_k = 12288/96 = 128  (each head ki dimension)

Toh 96 heads parallel mein 128-dim attention compute karte hain!
```

### Real World Analogy 🎬

Socho ek crime scene investigate karna hai:
```
Detective 1: Suspects ke beech relationships dekho
Detective 2: Timeline track karo
Detective 3: Physical evidence analyze karo
Detective 4: Motive dhundho

Alag alag aspects → sab combine karo → Complete picture!
```

Multi-head attention bhi yahi karta hai — **alag alag "detectives" (heads) parallel mein alag aspects analyze karte hain.**

---

## 11. Temperature

### Kya Hai Temperature? 🌡️
**Temperature ek hyperparameter hai jo model ke output ki randomness / creativity control karta hai.**

Low temperature = boring, predictable  
High temperature = creative, random (kabhi kabhi galat bhi!)

### Intuition

Socho ek parrot ko train kiya hai:
```
Low Temp:  Hamesha vahi bolta hai jo sabse zyada suna ho
High Temp: Kabhi kabhi nayi, unexpected cheezein bolta hai
```

### Technical Working

```python
# Simplified Softmax with Temperature
def sample_with_temperature(logits, temperature):
    # Temperature se divide karo
    scaled_logits = logits / temperature
    
    # Softmax apply karo
    probabilities = softmax(scaled_logits)
    
    # Sample karo (probability ke hisaab se)
    return random_sample(probabilities)
```

### Temperature Values Ka Effect

**Example: Next word predict karna after "The weather today is..."**

```
Vocab probabilities (normal):
"sunny"   → 0.40
"cloudy"  → 0.30
"rainy"   → 0.20
"amazing" → 0.07
"purple"  → 0.03

Temperature = 0.1 (Very Cold/Low):
"sunny"   → 0.98  ← almost always choose karega
"cloudy"  → 0.02
"rainy"   → 0.00
(Always predictable, boring)

Temperature = 1.0 (Normal):
"sunny"   → 0.40
"cloudy"  → 0.30
"rainy"   → 0.20
(Balanced)

Temperature = 2.0 (Hot/High):
"sunny"   → 0.26
"cloudy"  → 0.25
"rainy"   → 0.22
"amazing" → 0.16
"purple"  → 0.11
(Weird, creative, unpredictable)
```

### Kab Kaun Sa Temperature Use Karein?

| Task | Temperature | Reason |
|------|-------------|--------|
| Code generation | 0.1 - 0.3 | Correct syntax zaroori, no creativity |
| Factual Q&A | 0.1 - 0.5 | Accurate answers chahiye |
| Creative writing | 0.8 - 1.2 | Creativity chahiye |
| Brainstorming | 1.0 - 1.5 | Wild ideas welcome! |
| Poetry/Art | 1.2 - 2.0 | Maximum creativity |

### Top-p (Nucleus Sampling) — Temperature Ka Cousin

```
Top-p = 0.9 ka matlab:
Cumulative probability 90% tak wale tokens consider karo

"sunny"  0.40  cumsum=0.40 ✅
"cloudy" 0.30  cumsum=0.70 ✅
"rainy"  0.20  cumsum=0.90 ✅  ← 90% ho gayi, stop!
"amazing" 0.07 cumsum=0.97 ❌  ← ignore karo
"purple"  0.03 cumsum=1.00 ❌  ← ignore karo

In teeno mein se random sample karo.
```

---

## 12. Knowledge Cutoff

### Kya Hai Knowledge Cutoff? 📅
**Knowledge Cutoff = woh date jiske baad ka koi bhi data model ke training mein use nahi hua.**

Simple: Model ko us date ke baad ki duniya ka kuch pata nahi!

```
Training data: 
Jan 2024 tak ki sab cheezein ✅
Feb 2024 ke baad: ❌ Model ko pata nahi

User: "2025 mein kya hua?"
Model: "Mujhe nahi pata — yeh meri knowledge cutoff ke baad hai"
```

### Why Does It Happen?

```
Training Pipeline:
Data collect karo (web crawl, books, code, etc.)
         ↓
Data clean karo
         ↓
Model train karo  ← yeh bahut time leta hai (months!)
         ↓
Evaluate karo
         ↓
Deploy karo  ← yahan aur time lagta hai
         ↓
Users use karte hain  ← deployment ke 6-12 months baad bhi!
```

Training complete hone tak data already purana ho chuka hota hai. Isliye cutoff aur deployment mein gap hota hai.

### Famous Models Ki Knowledge Cutoffs

| Model | Knowledge Cutoff |
|-------|-----------------|
| GPT-4 | April 2023 |
| GPT-4 Turbo | December 2023 |
| Claude 3 | Early 2024 |
| Gemini Pro | Early 2024 |

### Problems With Knowledge Cutoff

```
1. Current Events: 
   "Kaun banega India ka PM 2025 mein?" → Model nahi jaanta

2. New Technologies:
   "GPT-5 ke features kya hain?" → Cutoff ke baad release hua → nahi pata

3. Price Changes:
   "Petrol ka price aaj kya hai?" → Real-time data nahi hai

4. Stale Information:
   "Company X ka CEO kaun hai?" → Badal gaya hoga shayad
```

### Solutions

**1. RAG (Retrieval Augmented Generation):**
```
User Query → Search current data (Google, DB, etc.)
           → Relevant documents retrieve karo
           → Context mein do to model
           → Model fresh information se answer kare
```

**2. Web Search Tool:**
```
ChatGPT + Browsing = Knowledge cutoff bypass!
Model real-time web search karta hai
```

**3. Fine-tuning:**
```
Regular intervals pe model ko naye data pe fine-tune karo
```

### Model Ko Khud Pata Hona Chahiye!

Ek well-trained model apni limitation jaanta hai:
```
✅ Good response:
"Meri knowledge cutoff April 2024 hai.
Iske baad ke events ke baare mein mujhe 
accurate information nahi hai. Please 
current sources check karein."

❌ Bad response (Hallucination):
"2025 mein X hua, Y hua..." ← confidently galat!
```

---

## 13. Tokenization

### Kya Hai Tokenization? ✂️
**Tokenization = Raw text ko chhote meaningful pieces (tokens) mein todna, phir har token ko ek unique number (ID) assign karna.**

```
"Hello, world!" → ["Hello", ",", " world", "!"] → [15496, 11, 995, 0]
```

### Kyun Tokenization?

```
Neural networks numbers samajhte hain, text nahi.
Text → Tokens → Token IDs (numbers) → Model input
```

### Types of Tokenization

**Type 1: Character-level Tokenization**
```
"cat" → ['c', 'a', 't'] → [3, 1, 20]

✅ Pros:
- Vocab bahut chhoti (26 letters + special chars)
- Koi bhi word handle kar sakta hai
- Spelling mistakes handle kar sakta hai

❌ Cons:
- Sequences bahut lambi ho jaati hain
- Meaning capture karna mushkil
- Slow training
```

**Type 2: Word-level Tokenization**
```
"The cat sat" → ["The", "cat", "sat"] → [1, 10, 76]

✅ Pros:
- Har token meaningful hai
- Short sequences

❌ Cons:
- Vocab bahut badi (lakhs of words!)
- New words handle nahi kar sakta ("Piyush" → unknown!)
- Languages ke liye problem
```

**Type 3: Subword Tokenization (Modern Approach) ⭐**
```
"unhappiness" → ["un", "happi", "ness"] → [451, 8091, 1108]
"GPT" → ["G", "PT"] → [38, 11571]

✅ Pros:
- Common words → single token
- Rare words → subwords mein toot jaata hai
- Balance between vocab size aur sequence length
- Naye words bhi handle kar sakta hai
```

### BPE — Byte Pair Encoding (GPT Use Karta Hai)

**Algorithm:**
```
Step 1: Characters se shuru karo
"low", "lower", "newest", "widest"
l-o-w, l-o-w-e-r, n-e-w-e-s-t, w-i-d-e-s-t

Step 2: Sabse frequent pair dhundho
"e-s" → highest frequency

Step 3: Merge karo
l-o-w, l-o-w-e-r, n-e-w-es-t, w-i-d-es-t

Step 4: Repeat
"es-t" most frequent → merge
l-o-w, l-o-w-e-r, n-e-w-est, w-i-d-est

Step 5: Vocab size reach hone tak repeat karo
```

GPT-4 ki vocab size: **~100,000 tokens**

### Tokenization Examples (GPT Tokenizer)

```
"Hello world"        → ["Hello", " world"]          → 2 tokens
"Unbelievable"       → ["Un", "bel", "ievable"]      → 3 tokens
"ChatGPT"            → ["Chat", "G", "PT"]           → 3 tokens
"मेरा नाम पियुष है"   → ["मे", "रा", " न", "ाम", ...] → more tokens
"2024"               → ["2024"]                      → 1 token
"https://github.com" → ["https", "://", "git", ...]  → many tokens
```

**Important:** Non-English languages mein same content ke liye **zyada tokens** lagte hain → zyada cost!

### Special Tokens

```
<|start|>     → Sequence start
<|end|>       → Sequence end
<|pad|>       → Padding (same length ke liye)
<|unk|>       → Unknown token
<|sep|>       → Separator (BERT mein)
<|cls|>       → Classification token (BERT mein)
<|mask|>      → Masked token (BERT training mein)
```

### Assignment 2 — Apna Tokenizer Banao

```python
class SimpleTokenizer:
    def __init__(self):
        # Character-level tokenizer
        self.chars = list("abcdefghijklmnopqrstuvwxyz "
                         "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                         "0123456789.,!?<>")
        self.char_to_id = {ch: i for i, ch in enumerate(self.chars)}
        self.id_to_char = {i: ch for i, ch in enumerate(self.chars)}
        
        # Special tokens
        self.START_TOKEN = len(self.chars)
        self.END_TOKEN = len(self.chars) + 1
    
    def encode(self, text: str) -> list[int]:
        """Text → Token IDs"""
        tokens = [self.START_TOKEN]
        for char in text:
            if char in self.char_to_id:
                tokens.append(self.char_to_id[char])
        tokens.append(self.END_TOKEN)
        return tokens
    
    def decode(self, token_ids: list[int]) -> str:
        """Token IDs → Text"""
        text = ""
        for token_id in token_ids:
            if token_id == self.START_TOKEN:
                continue
            elif token_id == self.END_TOKEN:
                break
            elif token_id in self.id_to_char:
                text += self.id_to_char[token_id]
        return text

# Test karo
tokenizer = SimpleTokenizer()
encoded = tokenizer.encode("Hello World")
print(encoded)   # [66, 7, 4, 11, 11, 14, 53, 22, 14, 17, 11, 3, 67]

decoded = tokenizer.decode(encoded)
print(decoded)   # "Hello World"
```

---

## 14. Vocab Size

### Kya Hai Vocab Size? 📏
**Vocab Size = Model ke tokenizer mein total unique tokens ki count.**

Yeh basically model ki "dictionary" ka size hai.

```
Simple character tokenizer:
a-z (26) + A-Z (26) + space (1) = 53 tokens

Real GPT-4 tokenizer:
~100,000 tokens
```

### Vocab Size Ka Impact

**Too Small Vocab:**
```
Word "unbelievable" → ["u","n","b","e","l","i","e","v","a","b","l","e"] → 12 tokens
Problem: Sequences bahut lambi ho jaati hain
         Model ko "u" aur "n" ko "un" (prefix) se connect karna mushkil
         Context window jaldi bhar jaata hai
```

**Too Large Vocab:**
```
Har unique word ek token
"cat", "cats", "catting", "cated" → 4 alag tokens

Problem: Rare words ke liye bahut kam training data
         Model "catting" acche se nahi seekh paata
         Embedding matrix bahut badi ho jaati hai
```

**Balanced Vocab (Subword):**
```
"cat" → [cat]  ← common word, ek token
"unbelievable" → ["un", "believ", "able"]  ← 3 tokens
"Piyushgarg"   → ["Pi", "yu", "shg", "arg"]  ← 4 tokens
```

### Vocab Size Aur Model Size Ka Relation

```
Embedding Matrix size = Vocab Size × Embedding Dimensions

GPT-3 example:
Vocab Size = 50,257
Embedding Dim = 12,288
Embedding Matrix = 50,257 × 12,288 = 617,635,000 parameters!
(617 million parameters sirf embeddings mein!)
```

### Different Models Ki Vocab Size

| Model | Vocab Size | Tokenizer |
|-------|-----------|-----------|
| GPT-2 | 50,257 | BPE |
| GPT-3/4 | ~100,000 | BPE (tiktoken) |
| BERT | 30,522 | WordPiece |
| LLaMA 2 | 32,000 | SentencePiece |
| Claude | ~100,000+ | BPE variant |
| Gemini | ~256,000 | SentencePiece |

### Hindi/Multilingual Token Efficiency Problem

```
English: "My name is Piyush" → 4 tokens ✅ (efficient)

Hindi: "मेरा नाम पियुष है" → ~12 tokens ❌ (less efficient)

Kyun? Kyunki training data mein English zyada tha
Hindi ke frequent patterns kam identify hue
Isliye Hindi ke liye zyada tokens lagte hain
→ Context window jaldi bhar jaata hai
→ API calls zyada expensive hote hain!
```

### Vocab Size Aur Softmax

```
Final layer ka output size = Vocab Size

GPT-4 ka final layer:
Input: [1, d_model]
Output: [1, 100,000]  ← har token ki probability!

Phir Softmax lagao → sab probabilities sum to 1
Phir sample karo temperature ke hisaab se
```

---

## 🔁 Sab Kuch Ek Saath — Complete Flow

```
USER INPUT: "What is the capital of India?"

STEP 1 — TOKENIZATION:
"What is the capital of India?" 
→ ["What", " is", " the", " capital", " of", " India", "?"]
→ [2061, 318, 262, 3139, 286, 4India, 30]

STEP 2 — EMBEDDINGS:
[2061] → [0.2, -0.5, 0.8, ...]  (768 dimensional vector)
[318]  → [0.1, 0.3, -0.2, ...]
...

STEP 3 — POSITIONAL ENCODING:
Position 0 ka PE add to "What" embedding
Position 1 ka PE add to "is" embedding
...

STEP 4 — SELF ATTENTION:
"capital" pays high attention to "India" ← relationship!
"What" pays attention to "?" ← question context

STEP 5 — MULTI-HEAD ATTENTION:
Head 1: Grammar relationships
Head 2: Question-answer patterns
Head 3: Geographic knowledge activation
...8-96 heads parallel

STEP 6 — FEED FORWARD NETWORK:
Complex transformations apply

STEP 7 — SOFTMAX ON VOCAB:
[0.001, 0.002, ..., 0.87 ("New"), ..., 0.001, ...]
→ "New" highest probability!

OUTPUT TOKEN: "New"

REPEAT with "What is the capital of India? New"
→ Next token: " Delhi"

FINAL OUTPUT: "New Delhi"
```

---

## 📊 Quick Reference Summary Table

| Concept | Ek Line Mein | Key Formula |
|---------|-------------|-------------|
| **Transformer** | Sab LLMs ka base architecture | Encoder + Decoder stack |
| **Encoder** | Input samjho | Context-aware vectors |
| **Decoder** | Output generate karo | Autoregressive generation |
| **Vectors** | Numbers ki list = word | [0.2, -0.5, 0.8, ...] |
| **Embeddings** | Meaningful vectors jisme relations hain | King - Man + Woman ≈ Queen |
| **Positional Encoding** | Token ko position ka pata | PE(pos, i) = sin/cos |
| **Semantic Meaning** | Context mein actual meaning | "bank" changes with context |
| **Self Attention** | Har token dusron se baat kare | Attention(Q,K,V) = Softmax(QK^T/√dk)V |
| **Softmax** | Scores → Probabilities (sum=1) | e^xi / Σe^xj |
| **Multi-Head Attention** | Kai parallel attentions | Concat(head_1...head_h) × W_O |
| **Temperature** | Randomness control | scores / temp → softmax |
| **Knowledge Cutoff** | Iss date ke baad pata nahi | Training data end date |
| **Tokenization** | Text → Token IDs | "cat" → [1234] |
| **Vocab Size** | Total unique tokens | GPT-4: ~100K |

---

## 💡 Key Takeaways

1. **Transformer** ne RNN/LSTM ko replace kiya — parallel processing ki wajah se
2. **Encoder** understands, **Decoder** generates
3. **Vectors** aur **Embeddings** = math ki language mein meaning
4. **Positional Encoding** isliye hai kyunki Transformer ko position nahi pata otherwise
5. **Self Attention** = har word ka doosre words se intelligent conversation
6. **Softmax** convert karta hai scores ko probabilities mein — hamesha sum=1
7. **Multi-Head Attention** = kai alag perspectives ek saath
8. **Temperature** = creativity dial — low for facts, high for creativity
9. **Knowledge Cutoff** = model ki expiry date for world events
10. **Tokenization** = text to numbers — AI ki "reading" ability
11. **Vocab Size** = model ki dictionary ka size — balance important hai

---

> **"Be comfortable with uncomfortable"** — Hitesh Sir  
> 
> Yeh sab concepts ek baar mein samajh nahi aate — aur that's okay! 
> Baar baar padho, implement karo, experiments karo. 🚀

---

*GitHub: github.com/piyushgarg-dev/genai-cohort*