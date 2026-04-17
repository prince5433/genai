# Fine Tuning Notes - Theory Only

> Class focus: Fine tuning of pre-trained LLMs  
> Style: Hinglish, revision-friendly, no code snippets

---

## 1. Fine Tuning Kya Hai?

Fine tuning ka matlab hai ek already trained model ko apne specific data ya task ke liye further train karna.

Pre-trained model general knowledge already seekh chuka hota hai. Fine tuning us model ko kisi particular domain, tone, format, ya behavior ke liye specialize karta hai.

Example:

| General Model | Fine-tuned Model |
| --- | --- |
| General questions answer kar sakta hai | Company-specific customer support answer de sakta hai |
| Normal English/Hindi generate karta hai | Brand tone mein response de sakta hai |
| Generic coding help deta hai | Company code style follow kar sakta hai |

Simple analogy: pre-trained model ek general doctor jaisa hai, fine tuning usse cardiologist, lawyer, support agent, ya coding assistant jaisa specialist bana deti hai.

---

## 2. Fine Tuning Ki Zarurat Kab Padti Hai?

Fine tuning tab useful hoti hai jab model ko sirf information nahi, balki behavior ya pattern sikhana ho.

Use cases:

| Use Case | Fine Tuning Ka Role |
| --- | --- |
| Customer support | Company ke response style aur policies ke according answer dena |
| Legal | Contract language, clause style, legal tone samajhna |
| Medical | Medical report style ya domain terminology follow karna |
| Finance | Financial summaries aur risk language ka pattern seekhna |
| Coding | Internal code conventions, naming style, review style follow karna |
| Education | Teacher-like explanation style, level-based answers |

Fine tuning especially tab helpful hai jab:

- Same type ka task baar-baar karna ho
- Output ka format fixed chahiye
- Model ko specific tone follow karni ho
- Prompt bahut lamba ya complicated ho raha ho
- Few-shot prompting se consistent results nahi aa rahe
- Domain-specific examples ka pattern model ko sikhana ho

---

## 3. Fine Tuning Vs Prompting Vs RAG

Fine tuning, prompting, aur RAG teen alag techniques hain. Inka purpose same nahi hota.

| Technique | Kya Karta Hai | Best For |
| --- | --- | --- |
| Prompting | Model ko instruction deta hai | Quick tasks, formatting, simple behavior |
| Few-shot prompting | Prompt mein examples dekar task samjhata hai | Small pattern learning without training |
| RAG | External documents se relevant info retrieve karta hai | Fresh/private knowledge, document Q&A |
| Fine tuning | Model ke behavior ko training se adapt karta hai | Consistent style, format, domain behavior |

Important point:

- Agar model ko latest ya private facts chahiye, usually RAG better hai.
- Agar model ko bolne ka tareeka, output structure, classification pattern, ya domain behavior sikhana hai, fine tuning better hai.
- Fine tuning model ke andar new facts reliably store karne ka best method nahi hai. Factual knowledge ke liye RAG safer hota hai.

Recommended order:

1. Pehle prompt engineering try karo
2. Phir few-shot examples try karo
3. Agar knowledge documents se answer chahiye, RAG use karo
4. Agar behavior consistent nahi hai, tab fine tuning consider karo

---

## 4. Pre-trained Models

Pre-trained model wo model hota hai jo pehle se large-scale internet, books, code, ya mixed data par train ho chuka hota hai.

Fine tuning usually kisi pre-trained base model ya instruction-tuned model par ki jaati hai.

Common model families:

| Provider / Family | Examples |
| --- | --- |
| OpenAI | GPT series |
| Google | Gemini models |
| Meta | Llama models |
| Mistral | Mistral / Mixtral models |
| Anthropic | Claude models |
| Microsoft | Phi models |
| DeepSeek | DeepSeek models |

Model choose karte waqt ye factors dekho:

- Model size
- Cost
- Latency
- License
- Context window
- Fine tuning support
- Target language support
- Deployment option: cloud ya local

Model size intuition:

| Size | Pros | Cons |
| --- | --- | --- |
| Small models | Fast, cheap, local run possible | Complex reasoning weak ho sakti hai |
| Medium models | Balance of cost and quality | Some tasks mein large model se weak |
| Large models | Better quality and reasoning | Expensive, slow, high GPU requirement |

---

## 5. Fine Tuning Ke Types

### 5.1 Full Fine Tuning

Full fine tuning mein model ke saare ya most parameters update hote hain.

Pros:

- Strong adaptation possible
- Domain behavior deeply learn ho sakta hai
- Best result mil sakta hai jab data aur compute enough ho

Cons:

- Expensive
- High GPU memory required
- Training slow hoti hai
- Overfitting ka risk zyada hota hai
- Large model ke liye practical nahi hota unless strong infra ho

### 5.2 PEFT - Parameter Efficient Fine Tuning

PEFT ka matlab hai model ke saare parameters train nahi karne. Sirf small extra parameters ya selected parts train karna.

Pros:

- Kam compute
- Kam memory
- Faster training
- Multiple tasks ke liye separate adapters bana sakte hain
- Base model mostly unchanged rehta hai

Common PEFT methods:

| Method | Idea |
| --- | --- |
| LoRA | Small trainable adapter matrices add karna |
| QLoRA | Quantized model par LoRA training karna |
| Prefix tuning | Input ke saath trainable prefix add karna |
| Prompt tuning | Soft prompts train karna |

### 5.3 LoRA

LoRA ka full form hai Low-Rank Adaptation.

LoRA mein original model weights freeze rehte hain. Training ke dauran small adapter weights learn hote hain. In adapters ki wajah se model ka behavior task ke according change hota hai.

Why LoRA popular hai:

- Full fine tuning se much cheaper
- GPU memory kam lagti hai
- Training fast hoti hai
- Adapter files small hote hain
- Same base model ke saath multiple adapters use kar sakte hain

LoRA ka main idea: poora model badalne ke bajay uske behavior ko small trainable modules ke through guide karna.

### 5.4 QLoRA

QLoRA LoRA ka efficient version hai jahan base model quantized form mein load hota hai.

Quantization ka matlab weights ko lower precision mein store karna, jisse memory usage kam hota hai.

QLoRA useful hai jab:

- GPU memory limited ho
- Large model fine-tune karna ho
- Cost kam rakhni ho

### 5.5 Instruction Fine Tuning

Instruction fine tuning mein model ko instruction-response examples par train kiya jata hai.

Goal: model user instruction samjhe aur useful response generate kare.

Example type:

| Input | Output |
| --- | --- |
| Explain this topic simply | Simple explanation |
| Summarize this paragraph | Short summary |
| Convert this into bullet points | Structured answer |

Ye technique models ko chatbot-like behavior dene mein important hai.

### 5.6 Supervised Fine Tuning

Supervised fine tuning mein har training example ke saath expected answer diya hota hai.

Model input dekhkar target output imitate karna seekhta hai.

Use cases:

- Classification
- Summarization
- Q&A
- Style transfer
- Structured output generation
- Domain-specific assistant behavior

### 5.7 RLHF

RLHF ka full form hai Reinforcement Learning from Human Feedback.

RLHF mein humans model ke multiple outputs ko compare/rate karte hain. Model learn karta hai ki kaunsa answer more helpful, safe, and preferred hai.

High-level flow:

1. Model multiple responses generate karta hai
2. Humans responses ko rank karte hain
3. Reward model train hota hai
4. Main model reward ke according improve hota hai

RLHF mainly alignment ke liye use hota hai:

- Helpful answers
- Safe behavior
- Better conversational quality
- Human preference ke closer output

---

## 6. Fine Tuning Dataset

Fine tuning ka result mostly dataset quality par depend karta hai.

Good dataset ke qualities:

- Relevant examples
- Clean text
- Correct labels or outputs
- Consistent style
- Balanced distribution
- Duplicate data kam
- Sensitive/private data remove
- Clear task format

Bad dataset ke problems:

- Wrong answers model ko galat behavior sikha denge
- Inconsistent format se model confuse hoga
- Biased data se biased output aayega
- Too little data se overfitting ho sakta hai
- Noisy data se quality degrade ho sakti hai

Common dataset types:

| Dataset Type | Use Case |
| --- | --- |
| Instruction-response | Chatbots, assistants, Q&A |
| Input-output pairs | Translation, summarization, rewriting |
| Labeled examples | Classification, sentiment, intent detection |
| Conversations | Multi-turn assistant behavior |
| Preference data | RLHF / ranking-based training |

Dataset split:

| Split | Purpose |
| --- | --- |
| Training set | Model isse learn karta hai |
| Validation set | Training ke during quality check hoti hai |
| Test set | Final unbiased evaluation hoti hai |

---

## 7. Fine Tuning Training Flow

Typical fine tuning process:

1. Goal define karo
2. Base model choose karo
3. Dataset collect karo
4. Data clean and format karo
5. Training/validation/test split banao
6. Fine tuning method choose karo: full fine tuning, LoRA, QLoRA, etc.
7. Training run karo
8. Evaluation karo
9. Errors analyze karo
10. Dataset improve karo
11. Model deploy karo
12. Monitoring and feedback loop maintain karo

Fine tuning iterative process hai. Usually first run perfect nahi hota.

---

## 8. Important Training Concepts

### Epoch

Ek epoch ka matlab model ne full training dataset ek baar dekh liya.

Too few epochs: model enough learn nahi karega.  
Too many epochs: model overfit kar sakta hai.

### Batch Size

Batch size batata hai ek training step mein kitne examples process honge.

Large batch:

- Training stable ho sakti hai
- More memory chahiye

Small batch:

- Memory kam chahiye
- Training noisy ho sakti hai

### Learning Rate

Learning rate decide karta hai model weights kitni speed se update honge.

High learning rate:

- Fast learning
- Instability ka risk

Low learning rate:

- Stable learning
- Slow training

### Overfitting

Overfitting tab hota hai jab model training data ko memorize kar leta hai but new examples par weak perform karta hai.

Signs:

- Training loss low
- Validation performance weak
- Model same type ke answers repeat karta hai
- New cases par generalize nahi karta

Avoid karne ke ways:

- More diverse data
- Validation monitoring
- Fewer epochs
- Regularization
- Early stopping
- Better dataset cleaning

### Catastrophic Forgetting

Catastrophic forgetting tab hota hai jab fine tuning ke baad model apni general ability lose karne lagta hai.

Example: model legal data par fine-tune hua, but normal conversation mein weak ho gaya.

Avoid karne ke ways:

- PEFT/LoRA use karo
- Learning rate low rakho
- Mixed/general data include karo
- Evaluation broad rakho

---

## 9. Evaluation

Fine-tuned model ko sirf training loss se judge nahi karna chahiye. Real task performance evaluate karna important hai.

Evaluation dimensions:

| Dimension | Meaning |
| --- | --- |
| Accuracy | Correct answer de raha hai ya nahi |
| Format consistency | Required structure follow kar raha hai ya nahi |
| Tone | Desired communication style match kar raha hai ya nahi |
| Factuality | Hallucination kam hai ya nahi |
| Safety | Harmful ya private info leak nahi kar raha |
| Generalization | New examples par bhi perform kar raha hai |

Evaluation methods:

- Holdout test set
- Human review
- Side-by-side comparison with base model
- Task-specific metrics
- LLM-as-a-judge, with human spot-checking
- Production feedback

Important: LLM-as-a-judge useful hai, but blindly trust nahi karna chahiye. Human evaluation bhi important hai, especially high-stakes tasks mein.

---

## 10. Deployment Considerations

Fine-tuned model ko deploy karte waqt sirf accuracy nahi, cost and safety bhi dekhni hoti hai.

Things to consider:

- Inference cost
- Latency
- Model hosting
- Data privacy
- Versioning
- Rollback plan
- Monitoring
- User feedback
- Guardrails
- Bias and safety checks

Production mein monitor karo:

- Wrong outputs
- Hallucinations
- User complaints
- Drift in input data
- Cost spikes
- Latency issues

---

## 11. Common Mistakes

| Mistake | Problem |
| --- | --- |
| Fine tuning when prompting was enough | Extra cost and complexity |
| Fine tuning for latest facts | Facts outdated ho sakte hain; RAG better |
| Poor dataset quality | Model poor behavior learn karega |
| Too much training | Overfitting |
| No validation set | Real performance pata nahi chalegi |
| No baseline comparison | Improvement measure nahi hoga |
| Ignoring safety/privacy | Sensitive data leak risk |
| Only training loss dekhna | User-facing quality miss ho sakti hai |

---

## 12. Quick Revision

| Concept | One-line Meaning |
| --- | --- |
| Fine tuning | Pre-trained model ko specific task/domain/style ke liye train karna |
| Pre-trained model | Already large data par trained base model |
| Prompting | Training ke bina instruction dena |
| Few-shot | Prompt mein examples dekar guide karna |
| RAG | External knowledge retrieve karke answer generate karna |
| Full fine tuning | Model ke many/all weights update karna |
| PEFT | Few parameters train karke efficient adaptation |
| LoRA | Small adapters train karna instead of full model |
| QLoRA | Quantized model ke saath LoRA training |
| SFT | Labeled input-output examples par supervised training |
| RLHF | Human feedback se model align karna |
| Epoch | Dataset ka ek full pass |
| Learning rate | Model update speed |
| Overfitting | Training data memorize, new data par weak |
| Catastrophic forgetting | Fine tuning ke baad general ability lose hona |
| Evaluation | Model quality ko test examples/human review se check karna |

---

## 13. Exam / Interview Points

- Fine tuning model ko new behavior sikhata hai; RAG model ko external knowledge deta hai.
- Fine tuning tab karo jab output style, task format, ya domain behavior consistent banana ho.
- LoRA and QLoRA practical fine tuning ke most common efficient methods hain.
- Dataset quality fine tuning result ka sabse important factor hai.
- Fine tuning ke baad evaluation zaruri hai because low training loss does not guarantee good real-world answers.
- Overfitting aur catastrophic forgetting major risks hain.
- Sensitive data ko training dataset mein include karna dangerous ho sakta hai.
- Production model ke liye monitoring, feedback, versioning, and rollback plan important hain.

---

## Extra Notes

LLM as a judge: LLM ko evaluator ki tarah use karna, jahan wo model outputs ko compare karta hai aur decide karta hai kaunsa output better hai. Fine-tuning evaluation mein useful ho sakta hai, but human spot-checking ke saath use karna better hai.

SDK: Software Development Kit, yani tools/libraries ka set jo developers ko kisi model provider ya framework ke saath application integrate karne mein help karta hai. Fine tuning ke context mein SDK training jobs, dataset upload, model management, and deployment ko easier bana sakta hai.
