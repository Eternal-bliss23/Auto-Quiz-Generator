import os
import re
import json
import random
import uuid
import logging
from typing import List, Optional, Dict, Any
import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger("quizcrafter")

class QuizQuestion(BaseModel):
    id: int
    question: str
    options: List[str]
    correct_answer: str  # e.g., "A", "B", "C", or "D"
    explanation: str
    topic: Optional[str] = None

class QuizResult(BaseModel):
    quiz_id: str
    title: str
    topic: str
    difficulty: str
    num_questions: int
    questions: List[QuizQuestion]
    provider_used: str
    warning: Optional[str] = None

class QuizGenerationRequest(BaseModel):
    topic: Optional[str] = "General Knowledge"
    content: Optional[str] = None
    num_questions: int = Field(default=5, ge=1, le=20)
    difficulty: str = Field(default="Medium")  # Easy, Medium, Hard
    provider: str = Field(default="auto")      # auto, offline, ollama, gemini, openai
    api_key: Optional[str] = None
    ollama_url: Optional[str] = None
    ollama_model: Optional[str] = None

SYSTEM_PROMPT_TEMPLATE = """You are an expert educator and assessment specialist.
Generate exactly {num_questions} multiple-choice questions on the topic "{topic}" based on the provided content.
Target Difficulty: {difficulty}.

Rules:
1. Every question must have exactly 4 options labeled: "A) ...", "B) ...", "C) ...", "D)".
2. Only ONE option must be correct.
3. Provide the letter (A, B, C, or D) in "correct_answer".
4. Provide a clear, educational 1-2 sentence explanation for why the answer is correct in "explanation".
5. Return ONLY a valid JSON array matching the schema below without any extra markdown or conversational text.

JSON Schema:
[
  {{
    "id": 1,
    "question": "Question text here?",
    "options": [
      "A) First option",
      "B) Second option",
      "C) Third option",
      "D) Fourth option"
    ],
    "correct_answer": "A",
    "explanation": "Why option A is correct."
  }}
]
"""

# Fallback smart question templates for various academic & tech subjects
TOPIC_KNOWLEDGE_BASE = {
    "machine learning": [
        {
            "question": "What is the primary difference between supervised and unsupervised learning?",
            "options": ["A) Supervised learning uses labeled training data, whereas unsupervised learning does not", "B) Supervised learning only works on numerical data", "C) Unsupervised learning always achieves higher accuracy", "D) Supervised learning requires quantum computing"],
            "correct_answer": "A",
            "explanation": "Supervised learning relies on labeled input-output pairs to learn a mapping function, whereas unsupervised algorithms discover hidden patterns in unlabeled data."
        },
        {
            "question": "Which of the following techniques is commonly used to prevent overfitting in deep neural networks?",
            "options": ["A) Dropout and L2 regularization", "B) Increasing learning rate indefinitely", "C) Removing all validation data", "D) Disabling gradient descent"],
            "correct_answer": "A",
            "explanation": "Dropout randomly deactivates neurons during training, and L2 regularization penalizes large weights, both preventing the model from fitting noise in training data."
        },
        {
            "question": "In classification problems, what metric calculates the proportion of true positives among all instances predicted as positive?",
            "options": ["A) Precision", "B) Recall", "C) Specificity", "D) Mean Squared Error"],
            "correct_answer": "A",
            "explanation": "Precision measures exactness (True Positives / (True Positives + False Positives)), while Recall measures completeness."
        }
    ],
    "web development": [
        {
            "question": "What is the purpose of CORS (Cross-Origin Resource Sharing)?",
            "options": ["A) A security mechanism that controls how web applications running at one origin can interact with resources at another origin", "B) A compiler for converting JavaScript into WebAssembly", "C) A CSS framework for responsive layout design", "D) A protocol replacing HTTP/2"],
            "correct_answer": "A",
            "explanation": "CORS is a browser-enforced HTTP-header-based mechanism that allows a server to indicate any origins other than its own from which a browser should permit loading resources."
        },
        {
            "question": "Which HTTP method should be used for operations that are idempotent and update a complete existing resource?",
            "options": ["A) PUT", "B) POST", "C) PATCH", "D) DELETE"],
            "correct_answer": "A",
            "explanation": "PUT is standard for replacing an entire resource idempotently, whereas POST creates new resources and PATCH performs partial updates."
        }
    ]
}


class SmartOfflineGenerator:
    """
    Intelligent NLP-based question generator that requires no external LLM or API keys.
    Extracts key concepts, definitions, metrics, and relationships from any PDF or text.
    """

    @staticmethod
    def extract_sentences(text: str) -> List[str]:
        # Clean text
        text = re.sub(r'\s+', ' ', text).strip()
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        clean = [s.strip() for s in sentences if len(s.strip()) > 30 and len(s.strip()) < 300]
        return clean

    @classmethod
    def generate_from_text(cls, text: str, topic: str, num_questions: int, difficulty: str) -> List[QuizQuestion]:
        sentences = cls.extract_sentences(text)
        questions: List[QuizQuestion] = []

        # Find informative sentences (definitions, causations, classifications)
        candidate_patterns = [
            (r'\b(is defined as|refers to|is known as|is a type of|is called)\b', "definition"),
            (r'\b(because|results in|leads to|causes|enables|allows)\b', "causation"),
            (r'\b(primary|crucial|essential|key|main|fundamental)\b', "significance"),
            (r'\b(consists of|contains|includes|comprises)\b', "composition"),
            (r'\b(used for|designed to|serves as|functions as)\b', "function"),
        ]

        scored_sentences = []
        for s in sentences:
            score = 0
            category = "general"
            for pattern, cat in candidate_patterns:
                if re.search(pattern, s, re.IGNORECASE):
                    score += 2
                    category = cat
            if any(char.isdigit() for char in s):
                score += 1
            if len(s.split()) >= 8 and len(s.split()) <= 40:
                score += 1
            scored_sentences.append((score, category, s))

        scored_sentences.sort(key=lambda x: x[0], reverse=True)

        # Extract vocabulary/terms for plausible distractors
        all_words = re.findall(r'\b[A-Z][a-z]{3,}\b|\b[a-z]{5,}\b', text)
        common_words = set(all_words)

        used_sentences = set()

        for idx, (score, category, sentence) in enumerate(scored_sentences):
            if len(questions) >= num_questions:
                break
            if sentence in used_sentences:
                continue
            used_sentences.add(sentence)

            # Formulate question based on category
            q_data = cls._create_question_from_sentence(sentence, category, difficulty, common_words, topic)
            if q_data:
                q_data.id = len(questions) + 1
                questions.append(q_data)

        # If not enough questions from text, supplement with knowledge base or topic expansions
        if len(questions) < num_questions:
            cls._supplement_questions(questions, topic, num_questions, difficulty)

        return questions[:num_questions]

    @classmethod
    def _create_question_from_sentence(cls, sentence: str, category: str, difficulty: str, word_bank: set, topic: str) -> Optional[QuizQuestion]:
        # Look for subject / predicate patterns
        # e.g., "X is defined as Y", "X refers to Y"
        match = re.search(r'^(.*?)\s+(is defined as|refers to|is known as|is called|consists of|is designed to|is primarily used for)\s+(.*?)[\.]$', sentence, re.IGNORECASE)
        
        if match:
            subject, verb, predicate = match.groups()
            subject = subject.strip()
            predicate = predicate.strip()

            if len(subject) > 3 and len(predicate) > 10:
                question_text = f"According to the text, what {verb} {predicate}?"
                correct_text = subject
                
                # Synthesize distractors
                distractors = cls._generate_distractors(subject, word_bank, count=3)
                options_raw = [correct_text] + distractors
                random.shuffle(options_raw)

                letters = ["A", "B", "C", "D"]
                correct_idx = options_raw.index(correct_text)
                options = [f"{letters[i]}) {opt}" for i, opt in enumerate(options_raw)]

                return QuizQuestion(
                    id=0,
                    question=question_text,
                    options=options,
                    correct_answer=letters[correct_idx],
                    explanation=f"The text explicitly states that '{subject}' {verb} {predicate}.",
                    topic=topic
                )

        # Fallback clozed/factual extraction
        words = sentence.split()
        if len(words) < 8:
            return None

        # Choose a key target word or phrase to blank out
        candidates = [w.strip(".,;:()") for w in words if len(w) > 5 and w.isalpha()]
        if not candidates:
            return None

        target = candidates[len(candidates) // 2]
        blanked = re.sub(r'\b' + re.escape(target) + r'\b', '_______', sentence, count=1)

        question_text = f"Fill in the blank: \"{blanked}\""
        correct_text = target
        distractors = cls._generate_distractors(target, word_bank, count=3)
        options_raw = [correct_text] + distractors
        random.shuffle(options_raw)

        letters = ["A", "B", "C", "D"]
        correct_idx = options_raw.index(correct_text)
        options = [f"{letters[i]}) {opt}" for i, opt in enumerate(options_raw)]

        return QuizQuestion(
            id=0,
            question=question_text,
            options=options,
            correct_answer=letters[correct_idx],
            explanation=f"In the context: \"{sentence}\", the term '{target}' correctly completes the statement.",
            topic=topic
        )

    @classmethod
    def _generate_distractors(cls, correct: str, word_bank: set, count: int = 3) -> List[str]:
        pool = [w for w in word_bank if w.lower() != correct.lower() and abs(len(w) - len(correct)) < 6]
        if len(pool) < count:
            defaults = ["Optimization", "Standardization", "Abstraction", "Encapsulation", "Decomposition", "Integration"]
            pool.extend([d for d in defaults if d.lower() != correct.lower()])
        selected = random.sample(pool, min(count, len(pool)))
        while len(selected) < count:
            selected.append(f"Alternative {len(selected) + 1}")
        return selected

    @classmethod
    def _supplement_questions(cls, current_questions: List[QuizQuestion], topic: str, needed: int, difficulty: str):
        topic_lower = topic.lower()
        pool = []
        for key, items in TOPIC_KNOWLEDGE_BASE.items():
            if key in topic_lower or topic_lower in key:
                pool.extend(items)

        if not pool:
            # General tech & science fallback
            pool = [
                {
                    "question": f"Which principle is most essential when analyzing core concepts of {topic}?",
                    "options": [f"A) Systematic empirical validation and structured analysis", f"B) Disregarding all baseline measurements", f"C) Exclusively relying on anecdotal evidence", f"D) Ignoring reproducible test protocols"],
                    "correct_answer": "A",
                    "explanation": f"Systematic analysis and rigorous verification form the foundation of understanding {topic}."
                },
                {
                    "question": f"In the study of {topic}, what is the primary benefit of modular decomposition?",
                    "options": [f"A) Isolating complexity to make systems easier to test, maintain, and scale", f"B) Making components tightly coupled and rigid", f"C) Preventing documentation from being written", f"D) Increasing execution latency uniformly"],
                    "correct_answer": "A",
                    "explanation": "Modularity reduces cognitive load and allows isolated testing, troubleshooting, and parallel evolution."
                },
                {
                    "question": f"When evaluating performance in {topic}, which factor represents standard best practice?",
                    "options": [f"A) Establishing quantifiable benchmark metrics under controlled conditions", f"B) Guessing outcomes without measuring results", f"C) Running tests only once without validation", f"D) Discarding edge cases completely"],
                    "correct_answer": "A",
                    "explanation": "Accurate assessment requires objective benchmarks tested systematically across variable constraints."
                },
                {
                    "question": f"What is the risk of overfitting or narrow specialization when applying methods in {topic}?",
                    "options": [f"A) The system performs well on known samples but fails to generalize to novel situations", f"B) The system becomes completely immune to input errors", f"C) Data requirements decrease to zero", f"D) All future computations run instantaneously"],
                    "correct_answer": "A",
                    "explanation": "Overfitting restricts adaptability, causing high degradation when introduced to out-of-distribution scenarios."
                },
                {
                    "question": f"Why is iterative refinement preferred when developing solutions in {topic}?",
                    "options": [f"A) It permits early feedback, incremental validation, and rapid risk mitigation", f"B) It guarantees the elimination of all planning steps", f"C) It forces implementations to restart from scratch repeatedly", f"D) It ensures that requirements never change"],
                    "correct_answer": "A",
                    "explanation": "Iterative methodologies uncover unexpected bottlenecks early while keeping delivery aligned with goals."
                }
            ]

        for item in pool:
            if len(current_questions) >= needed:
                break
            current_questions.append(QuizQuestion(
                id=len(current_questions) + 1,
                question=item["question"],
                options=item["options"],
                correct_answer=item["correct_answer"],
                explanation=item["explanation"],
                topic=topic
            ))


class MultiProviderQuizGenerator:
    """
    Central router that can generate quizzes using:
    - Built-in Offline NLP Generator
    - Local Ollama
    - Google Gemini
    - OpenAI / Compatible endpoints
    """

    @staticmethod
    def _clean_json_output(content: str) -> str:
        content = content.strip()
        # Remove markdown code blocks ```json ... ```
        if "```" in content:
            match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', content, re.DOTALL)
            if match:
                return match.group(1).strip()
            # Try removing backticks
            content = re.sub(r'^```(?:json)?\n?', '', content)
            content = re.sub(r'\n?```$', '', content)
        # Find JSON array bracket
        start = content.find('[')
        end = content.rfind(']')
        if start != -1 and end != -1 and end > start:
            return content[start:end+1].strip()
        return content

    @classmethod
    async def generate_with_ollama(
        cls, 
        content: str, 
        topic: str, 
        num_questions: int, 
        difficulty: str, 
        base_url: str = "http://localhost:11434",
        model: Optional[str] = None
    ) -> List[QuizQuestion]:
        base_url = base_url.rstrip("/")
        
        async with httpx.AsyncClient(timeout=45.0) as client:
            # Check available models if none provided
            if not model:
                try:
                    tags_res = await client.get(f"{base_url}/api/tags")
                    if tags_res.status_code == 200:
                        models_data = tags_res.json().get("models", [])
                        model_names = [m.get("name", "") for m in models_data]
                        for candidate in ["llama3.2:latest", "llama3.2", "llama3:latest", "llama3", "mistral", "gemma2", "phi3"]:
                            for name in model_names:
                                if candidate in name:
                                    model = name
                                    break
                            if model:
                                break
                        if not model and model_names:
                            model = model_names[0]
                except Exception as e:
                    logger.warning(f"Failed to query Ollama tags: {e}")
            
            model = model or "llama3.2"

            prompt = SYSTEM_PROMPT_TEMPLATE.format(
                num_questions=num_questions,
                topic=topic,
                difficulty=difficulty
            )
            user_msg = f"CONTENT TO BASE QUIZ ON:\n\n{content[:4000]}"

            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_msg}
                ],
                "format": "json",
                "stream": False,
                "options": {
                    "temperature": 0.5
                }
            }

            response = await client.post(f"{base_url}/api/chat", json=payload)
            response.raise_for_status()
            res_data = response.json()
            raw_text = res_data.get("message", {}).get("content", "")
            
            cleaned = cls._clean_json_output(raw_text)
            parsed = json.loads(cleaned)

            questions = []
            for i, q in enumerate(parsed):
                questions.append(QuizQuestion(
                    id=i + 1,
                    question=q["question"],
                    options=q["options"],
                    correct_answer=q["correct_answer"].strip().upper(),
                    explanation=q.get("explanation", f"Option {q['correct_answer']} is the correct answer."),
                    topic=topic
                ))
            return questions

    @classmethod
    async def generate_with_gemini(
        cls,
        content: str,
        topic: str,
        num_questions: int,
        difficulty: str,
        api_key: str
    ) -> List[QuizQuestion]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        prompt = SYSTEM_PROMPT_TEMPLATE.format(
            num_questions=num_questions,
            topic=topic,
            difficulty=difficulty
        )
        full_prompt = f"{prompt}\n\nCONTENT TO BASE QUIZ ON:\n{content[:5000]}"

        payload = {
            "contents": [
                {
                    "parts": [{"text": full_prompt}]
                }
            ],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.4
            }
        }

        async with httpx.AsyncClient(timeout=40.0) as client:
            res = await client.post(url, json=payload)
            res.raise_for_status()
            data = res.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            cleaned = cls._clean_json_output(raw_text)
            parsed = json.loads(cleaned)

            questions = []
            for i, q in enumerate(parsed):
                questions.append(QuizQuestion(
                    id=i + 1,
                    question=q["question"],
                    options=q["options"],
                    correct_answer=q["correct_answer"].strip().upper(),
                    explanation=q.get("explanation", f"Option {q['correct_answer']} is correct according to the context."),
                    topic=topic
                ))
            return questions

    @classmethod
    async def generate_with_openai(
        cls,
        content: str,
        topic: str,
        num_questions: int,
        difficulty: str,
        api_key: str,
        base_url: str = "https://api.openai.com/v1"
    ) -> List[QuizQuestion]:
        url = f"{base_url.rstrip('/')}/chat/completions"
        prompt = SYSTEM_PROMPT_TEMPLATE.format(
            num_questions=num_questions,
            topic=topic,
            difficulty=difficulty
        )

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"CONTENT:\n{content[:4000]}"}
            ],
            "response_format": {"type": "json_object"} if "openai.com" in url else None,
            "temperature": 0.4
        }

        async with httpx.AsyncClient(timeout=40.0) as client:
            res = await client.post(url, json=payload, headers=headers)
            res.raise_for_status()
            data = res.json()
            raw_text = data["choices"][0]["message"]["content"]
            cleaned = cls._clean_json_output(raw_text)
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict) and "questions" in parsed:
                parsed = parsed["questions"]

            questions = []
            for i, q in enumerate(parsed):
                questions.append(QuizQuestion(
                    id=i + 1,
                    question=q["question"],
                    options=q["options"],
                    correct_answer=q["correct_answer"].strip().upper(),
                    explanation=q.get("explanation", f"Option {q['correct_answer']} is correct."),
                    topic=topic
                ))
            return questions

    @classmethod
    async def generate_quiz(cls, req: QuizGenerationRequest) -> QuizResult:
        quiz_id = str(uuid.uuid4())[:8]
        topic = req.topic.strip() if req.topic else "General Study"
        content = req.content.strip() if req.content else ""
        
        # If content is minimal, create a descriptive baseline
        if len(content) < 50:
            content = f"Educational overview of {topic}. {topic} encompasses foundational principles, methodologies, practical applications, standard best practices, and systematic evaluation metrics."

        provider = req.provider.lower()
        warning = None

        # 1. Gemini explicit or auto if key present
        gemini_key = req.api_key or os.getenv("GEMINI_API_KEY")
        openai_key = req.api_key or os.getenv("OPENAI_API_KEY")

        if provider == "gemini" or (provider == "auto" and gemini_key):
            if gemini_key:
                try:
                    logger.info("Attempting quiz generation with Google Gemini...")
                    questions = await cls.generate_with_gemini(
                        content=content,
                        topic=topic,
                        num_questions=req.num_questions,
                        difficulty=req.difficulty,
                        api_key=gemini_key
                    )
                    return QuizResult(
                        quiz_id=quiz_id,
                        title=f"{topic} Quiz ({req.difficulty})",
                        topic=topic,
                        difficulty=req.difficulty,
                        num_questions=len(questions),
                        questions=questions,
                        provider_used="Google Gemini (gemini-1.5-flash)"
                    )
                except Exception as e:
                    logger.warning(f"Gemini generation failed: {e}. Falling back...")
                    warning = f"Gemini API error: {str(e)}. Fell back to Offline NLP Engine."

        # 2. OpenAI explicit
        if provider == "openai" or (provider == "auto" and openai_key and not gemini_key):
            if openai_key:
                try:
                    logger.info("Attempting quiz generation with OpenAI...")
                    questions = await cls.generate_with_openai(
                        content=content,
                        topic=topic,
                        num_questions=req.num_questions,
                        difficulty=req.difficulty,
                        api_key=openai_key
                    )
                    return QuizResult(
                        quiz_id=quiz_id,
                        title=f"{topic} Quiz ({req.difficulty})",
                        topic=topic,
                        difficulty=req.difficulty,
                        num_questions=len(questions),
                        questions=questions,
                        provider_used="OpenAI (gpt-4o-mini)"
                    )
                except Exception as e:
                    logger.warning(f"OpenAI generation failed: {e}. Falling back...")
                    warning = f"OpenAI API error: {str(e)}. Fell back to Offline NLP Engine."

        # 3. Ollama explicit or auto test
        ollama_url = req.ollama_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        if provider == "ollama" or provider == "auto":
            try:
                # Fast ping
                async with httpx.AsyncClient(timeout=2.0) as client:
                    ping = await client.get(f"{ollama_url.rstrip('/')}/api/version")
                    if ping.status_code == 200:
                        logger.info("Ollama is reachable, invoking Ollama...")
                        questions = await cls.generate_with_ollama(
                            content=content,
                            topic=topic,
                            num_questions=req.num_questions,
                            difficulty=req.difficulty,
                            base_url=ollama_url,
                            model=req.ollama_model
                        )
                        return QuizResult(
                            quiz_id=quiz_id,
                            title=f"{topic} Quiz ({req.difficulty})",
                            topic=topic,
                            difficulty=req.difficulty,
                            num_questions=len(questions),
                            questions=questions,
                            provider_used="Local Ollama"
                        )
            except Exception as e:
                if provider == "ollama":
                    warning = f"Ollama connection error: {str(e)}. Switched to built-in Offline NLP Generator."
                logger.info(f"Ollama not available or failed: {e}")

        # 4. Built-in Offline NLP Generator
        logger.info("Generating quiz using Smart Offline NLP Engine...")
        questions = SmartOfflineGenerator.generate_from_text(
            text=content,
            topic=topic,
            num_questions=req.num_questions,
            difficulty=req.difficulty
        )

        return QuizResult(
            quiz_id=quiz_id,
            title=f"{topic} Quiz ({req.difficulty})",
            topic=topic,
            difficulty=req.difficulty,
            num_questions=len(questions),
            questions=questions,
            provider_used="Smart Offline NLP Engine (Zero Setup)",
            warning=warning
        )
