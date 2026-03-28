"""
Production RAG Engine for Akshat's Portfolio Chatbot
- Intent classification with confidence scoring
- Synonym expansion for better retrieval
- Conversation memory (multi-turn context)
- Language normalization (typos, Hinglish, shorthand)
"""

import re
import math
import os
from collections import Counter, defaultdict
from knowledge_base import AKSHAT_KNOWLEDGE

# ── Config ────────────────────────────────────────────────────────────────────
WHATSAPP_NUMBER = os.getenv("OWNER_WHATSAPP", "918103214221")
WHATSAPP_URL = (
    f"https://wa.me/{WHATSAPP_NUMBER}"
    "?text=Hello%20Akshat%2C%20I%20found%20your%20portfolio%20and%20would%20like%20to%20connect!"
)

# ── Conversation Memory ───────────────────────────────────────────────────────
# session_id -> list of {"role": "user"|"bot", "text": str}
_sessions: dict[str, list[dict]] = defaultdict(list)
MAX_HISTORY = 6  # keep last 6 turns per session


def _add_to_history(session_id: str, role: str, text: str):
    history = _sessions[session_id]
    history.append({"role": role, "text": text})
    if len(history) > MAX_HISTORY:
        _sessions[session_id] = history[-MAX_HISTORY:]


def _get_history(session_id: str) -> list[dict]:
    return _sessions.get(session_id, [])


# ── Language Normalization ────────────────────────────────────────────────────
_NORMALIZATIONS = {
    # Hinglish / shorthand
    "kya": "what", "kaise": "how", "kaun": "who", "kahan": "where",
    "batao": "tell", "bata": "tell", "dekho": "show", "dikhao": "show",
    "karo": "do", "karta": "does", "karte": "does", "chahiye": "need",
    "mujhe": "i need", "mera": "my", "tera": "your", "uska": "his",
    "aur": "and", "ya": "or", "nahi": "no", "haan": "yes",
    "accha": "good", "theek": "ok", "sahi": "correct",
    # Common typos / shorthand
    "bout": "about", "abt": "about", "ur": "your", "u": "you",
    "r": "are", "wht": "what", "hw": "how", "cn": "can",
    "plz": "please", "pls": "please", "thx": "thanks", "ty": "thanks",
    "dev": "developer", "devs": "developers", "proj": "project",
    "exp": "experience", "cert": "certification", "tech": "technology",
    "ml": "machine learning", "ai": "artificial intelligence",
    "wa": "whatsapp", "wp": "whatsapp",
    # ── NEW additions ─────────────────────────────────────────────────────────
    # More Hinglish
    "kitne": "how many", "kab": "when", "kyun": "why", "kyunki": "because",
    "kuch": "some", "bahut": "very", "thoda": "little", "zyada": "more",
    "seekha": "learned", "sikha": "taught", "banana": "build",
    "banaya": "built", "banate": "build", "kaam": "work",
    "paisa": "money", "price": "price", "lagta": "costs",
    "kitna": "how much", "rate": "rate", "charge": "charge",
    "portfolio": "portfolio", "resume": "resume", "cv": "resume",
    "padhai": "education", "college": "college", "university": "university",
    "degree": "degree", "padhna": "study", "padha": "studied",
    # More shorthand / slang
    "lmk": "let me know", "asap": "as soon as possible",
    "fyi": "for your information", "imo": "in my opinion",
    "tbh": "to be honest", "ngl": "not gonna lie",
    "dm": "direct message", "msg": "message", "avail": "available",
    "collab": "collaborate", "biz": "business", "prof": "professional",
    "lang": "language", "langs": "languages", "bg": "background",
    "py": "python", "js": "javascript", "ts": "typescript",
    "db": "database", "api": "api", "ui": "user interface",
    "ux": "user experience", "ds": "data science", "da": "data analyst",
    "sec": "security", "cyber": "cybersecurity", "pentest": "penetration testing",
    "viz": "visualization", "dash": "dashboard", "repo": "repository",
    "opensource": "open source", "os": "open source",
}

_SYNONYMS = {
    "build": ["create", "develop", "make", "built", "created", "developed"],
    "project": ["work", "portfolio", "application", "app", "system", "tool"],
    "skill": ["expertise", "capability", "technology", "stack", "framework"],
    "experience": ["career", "job", "work history", "employment", "background"],
    "hire": ["recruit", "employ", "engage", "work with", "collaborate"],
    "contact": ["reach", "connect", "get in touch", "message", "call"],
    "client": ["customer", "freelance", "contract", "business"],
    # ── NEW synonyms ──────────────────────────────────────────────────────────
    "resume": ["cv", "curriculum vitae", "bio", "profile"],
    "rate": ["price", "cost", "charge", "fees", "pricing", "budget", "quote"],
    "education": ["college", "university", "degree", "study", "academic", "qualification"],
    "achievement": ["award", "accomplishment", "milestone", "recognition", "win"],
    "language": ["speak", "communication", "tongue", "proficiency"],
    "goal": ["aim", "vision", "ambition", "aspiration", "target", "plan"],
    "review": ["testimonial", "feedback", "recommendation", "rating", "opinion"],
    "availability": ["schedule", "timing", "when", "open", "free", "slot"],
    "strength": ["strong", "good at", "best at", "excellent", "specialise"],
    "python": ["py", "django", "fastapi", "flask", "backend"],
    "data": ["dataset", "analytics", "analysis", "reporting", "insights"],
    "security": ["cyber", "hacking", "pentest", "vulnerability", "audit"],
    "dashboard": ["powerbi", "tableau", "visualisation", "visualization", "report"],
}


def normalize(text: str) -> str:
    """Normalize Hinglish, typos, and shorthand to English."""
    words = text.lower().split()
    normalized = [_NORMALIZATIONS.get(w, w) for w in words]
    return " ".join(normalized)


# ── TF-IDF Retrieval ──────────────────────────────────────────────────────────
def _tokenize(text: str) -> list[str]:
    return re.findall(r'\b\w+\b', text.lower())


def _build_tfidf(corpus: list[str]):
    tokenized = [_tokenize(doc) for doc in corpus]
    N = len(tokenized)
    df = Counter()
    for tokens in tokenized:
        for t in set(tokens):
            df[t] += 1
    idf = {t: math.log((N + 1) / (df[t] + 1)) + 1 for t in df}
    vectors = []
    for tokens in tokenized:
        tf = Counter(tokens)
        vec = {t: (tf[t] / len(tokens)) * idf.get(t, 1) for t in tf}
        norm = math.sqrt(sum(v ** 2 for v in vec.values())) or 1
        vectors.append({t: v / norm for t, v in vec.items()})
    return vectors, idf


def _cosine(v1: dict, v2: dict) -> float:
    return sum(v1.get(t, 0) * v2.get(t, 0) for t in v2)


_doc_vectors, _idf = _build_tfidf(AKSHAT_KNOWLEDGE)


def _expand_query(query: str) -> str:
    """Add synonym expansions to improve retrieval recall."""
    tokens = set(_tokenize(query))
    extras = []
    for base, syns in _SYNONYMS.items():
        if base in tokens or any(s in tokens for s in syns):
            extras.extend([base] + syns)
    return query + " " + " ".join(extras)


def retrieve(query: str, top_k: int = 4) -> tuple[list[str], float]:
    """Return top_k docs and the best confidence score (0-1)."""
    expanded = _expand_query(normalize(query))
    tokens = _tokenize(expanded)
    tf = Counter(tokens)
    vec = {t: (tf[t] / len(tokens)) * _idf.get(t, 1) for t in tf if t in _idf}
    norm = math.sqrt(sum(v ** 2 for v in vec.values())) or 1
    qvec = {t: v / norm for t, v in vec.items()}

    scores = [(_cosine(qvec, dv), AKSHAT_KNOWLEDGE[i]) for i, dv in enumerate(_doc_vectors)]
    scores.sort(key=lambda x: x[0], reverse=True)

    best_score = scores[0][0] if scores else 0.0
    docs = [doc for score, doc in scores[:top_k] if score > 0]
    return docs, best_score


# ── Intent Classification ─────────────────────────────────────────────────────
_INTENTS: list[tuple[str, list[str]]] = [
    ("whatsapp",     ["whatsapp", "whats app", "wa.me", "connect to whatsapp",
                      "chat on whatsapp", "message on whatsapp", "contact whatsapp",
                      "reach on whatsapp", "talk to akshat directly"]),
    ("portfolio",    ["explain", "portfolio", "overview", "this website", "what is this",
                      "about this", "tell me everything", "full intro", "summarize",
                      "explain me about", "describe this", "what does this site"]),
    ("greeting",     ["hello", "hi ", "hey ", "good morning", "good evening",
                      "good afternoon", "namaste", "hola", "sup ", "greetings"]),
    ("about",        ["who is akshat", "about akshat", "about him", "introduce akshat",
                      "describe akshat", "what does akshat do",
                      "bout akshat", "bout him", "who is he",
                      "who is", "who are", "tell me about",
                      "introduce", "describe him",
                      "what does akshat do", "akshat jain"]),
    ("client_work",  ["client", "freelanc", "for client", "client project",
                      "which type", "what type", "what kind", "kind of project",
                      "type of project", "make for", "build for", "develop for",
                      "what do you make", "what can you build"]),
    ("skills",       ["skill", "tech stack", "expertise", "what can you do",
                      "capable of", "tools", "framework", "language", "know how",
                      "fastapi", "django", "flask", "machine learning", "powerbi",
                      "tableau", "hacking", "penetration", "technology"]),
    ("projects",     ["project", "portfolio", "github", "built", "created",
                      "developed", "show me", "past work", "work done",
                      "what have you", "your work"]),
    ("experience",   ["experience", "work history", "job", "company", "internship",
                      "career", "worked at", "working at", "employment", "position",
                      "where did you work", "background"]),
    ("hire",         ["hire", "available", "availability", "work with", "collaborate",
                      "need developer", "looking for", "can you help", "freelance",
                      "contract", "remote work", "open to work", "for hire"]),
    ("contact",      ["contact", "email", "phone", "reach", "number", "linkedin",
                      "social media", "get in touch", "how to contact", "call"]),
    ("location",     ["location", "where are you", "city", "pune", "india",
                      "based in", "from where", "country", "where do you live"]),
    ("certifications", ["certif", "ceh", "ccna", "certified", "degree",
                        "qualification", "education", "course", "training"]),
    ("stats",        ["how many", "stats", "numbers", "projects completed",
                      "years of experience", "problems solved", "internships"]),
    ("help",         ["help", "what can you ask", "what can i ask", "commands",
                      "options", "menu", "what do you know", "guide me", "topics",
                      "what can you tell", "what can you do"]),
    # ── NEW intents ───────────────────────────────────────────────────────────
    ("pricing",      ["price", "cost", "how much", "charge", "fees", "rate",
                      "budget", "quote", "pay", "payment", "per hour", "hourly",
                      "fixed", "cheap", "affordable", "expensive", "kitna lagega",
                      "kitne paisa", "what do you charge", "how do you charge"]),
    ("education",    ["college", "university", "btech", "b.tech", "engineering",
                      "degree", "academic", "study", "studied", "where did you study",
                      "graduation", "school", "board", "12th", "10th", "marks"]),
    ("resume",       ["resume", "cv", "curriculum vitae", "download resume",
                      "get resume", "your resume", "pdf resume", "resume link"]),
    ("achievements", ["achievement", "award", "won", "winner", "hackathon",
                      "competition", "recognition", "milestone", "proud",
                      "accomplishment", "what have you won", "any awards"]),
    ("work_style",   ["work style", "how do you work", "process", "workflow",
                      "methodology", "approach", "deadline", "punctual",
                      "communication", "updates", "how you handle", "do you deliver"]),
    ("languages_spoken", ["language speak", "speak hindi", "speak english",
                          "which language", "languages you know", "hindi",
                          "english", "communication language", "can you speak"]),
    ("goals",        ["goal", "vision", "future", "aspiration", "ambition",
                      "where do you see", "5 years", "long term", "short term",
                      "what are you aiming", "dream", "mission"]),
    ("testimonials", ["testimonial", "review", "feedback", "what do clients say",
                      "client review", "recommendation", "rating", "happy client",
                      "previous client", "reference"]),
    ("tools_used",   ["ide", "vs code", "vscode", "pycharm", "tools you use",
                      "software", "postman", "git", "github actions", "docker",
                      "linux", "ubuntu", "windows", "mac", "daily tools",
                      "what tools", "which software"]),
    ("opensource",   ["open source", "opensource", "contribute", "contribution",
                      "github star", "public repo", "community", "pull request",
                      "open source project"]),
    ("social",       ["twitter", "instagram", "youtube", "social media profile",
                      "follow you", "where to follow", "online presence",
                      "your profiles", "find you online"]),
    ("availability_time", ["when can you start", "notice period", "start date",
                           "immediately", "how soon", "joining date",
                           "when are you free", "available from when"]),
    ("strengths",    ["strength", "strong suit", "best at", "what are you good at",
                      "specialise", "specialize", "core strength", "expertise area",
                      "strongest skill", "what do you excel"]),
]


def classify_intent(query: str) -> str | None:
    q = normalize(query).lower()
    for intent, triggers in _INTENTS:
        if any(t in q for t in triggers):
            return intent
    return None


# ── Response Templates ────────────────────────────────────────────────────────
def _build_response(intent: str, history: list[dict]) -> str:
    # Personalize if we know the user asked before
    prev_topics = [h["text"] for h in history if h["role"] == "user"]
    returning = len(prev_topics) > 1

    if intent == "greeting":
        if returning:
            return ("Welcome back! What else would you like to know about Akshat?\n\n"
                    "Ask about his **skills**, **projects**, **experience**, or type "
                    "**'connect to whatsapp'** to reach him directly!")
        return ("👋 Hi! I'm Akshat's AI assistant.\n\n"
                "I can tell you about his:\n"
                "• 🛠️ **Skills** — Python, ML, Ethical Hacking\n"
                "• 💼 **Projects** — 27+ completed, 12 freelance\n"
                "• 🏢 **Experience** — 2+ years, 4 internships\n"
                "• 📞 **Contact** — Email, LinkedIn, WhatsApp\n\n"
                "What would you like to know?")

    if intent == "portfolio":
        return ("👨\u200d💻 **Akshat Jain's Portfolio**\n\n"
                "This is the personal portfolio of **Akshat Jain** — Python Developer & Ethical Hacker from Pune, India.\n\n"
                "**What you'll find here:**\n"
                "🛠️ **Skills** — Python, ML, Data Science, Cybersecurity\n"
                "🚀 **Projects** — 27+ projects including Skillobal, AI Chatbot, Face Detection\n"
                "🏢 **Experience** — 2+ years, 4 internships, 12 freelance projects\n"
                "🏆 **Certifications** — CEH V12, CCNA\n"
                "📞 **Contact** — Email, LinkedIn, WhatsApp\n\n"
                "Ask me anything specific — **skills**, **projects**, **hire**, or **contact**!")

    if intent == "about":
        return ("👨‍💻 **Akshat Jain** (akshatios)\n\n"
                "**Role:** Python Developer & Ethical Hacker\n"
                "**Location:** Pune, India\n\n"
                "**Specializes in:**\n"
                "🐍 Python backend — FastAPI, Django, Flask\n"
                "📊 Data Science — ML, PowerBI, Tableau\n"
                "🔐 Cybersecurity — CEH V12, Penetration Testing\n\n"
                "📌 2+ yrs experience | 27+ projects | 12 freelance | 4 internships\n\n"
                "Ask about his **skills**, **projects**, or **how to hire him**!")

    if intent == "client_work":
        return ("💼 **Projects Akshat Builds for Clients:**\n\n"
                "🌐 **Web Apps** — Django/FastAPI full-stack applications\n"
                "🤖 **AI & Chatbots** — NLP bots, voice assistants, automation\n"
                "📊 **Data Dashboards** — PowerBI, Tableau, custom reports\n"
                "🔐 **Security Audits** — Pen testing, vulnerability scanning\n"
                "🧠 **ML Models** — Predictive models, face detection, analysis\n"
                "⚙️ **APIs** — RESTful APIs, microservices, auth systems\n"
                "📑 **Automation** — Scripts, data pipelines, PPT generators\n\n"
                "✅ **12 freelance projects** completed successfully!\n\n"
                "💬 Type **'connect to whatsapp'** to discuss your project!")

    if intent == "skills":
        return ("🛠️ **Akshat's Tech Stack:**\n\n"
                "🐍 **Python Development**\n"
                "  FastAPI · Django · Flask · Pytest · Postman\n\n"
                "📊 **Data Science & Analytics**\n"
                "  Pandas · NumPy · Matplotlib · PowerBI · Tableau · SAS\n\n"
                "🧠 **Machine Learning**\n"
                "  Supervised · Unsupervised · Deep Learning · OpenCV\n\n"
                "🔐 **Ethical Hacking**\n"
                "  Nmap · Burp Suite · SQLMap · Nessus · OWASP ZAP\n\n"
                "🏆 **Certifications:** CEH V12 | CCNA")

    if intent == "projects":
        return ("🚀 **Akshat's Featured Projects:**\n\n"
                "🎓 **Skillobal** — Online learning platform → [skillobal.com](https://skillobal.com)\n"
                "🤖 **AI Chatbot** — NLP-powered automation → [GitHub](https://github.com/akshatios/chat_messenger)\n"
                "👁️ **Face Detection** — Real-time OpenCV → [GitHub](https://github.com/akshatios/face-recognition-authentication-main)\n"
                "🎤 **Voice Assistant** — Speech recognition → [GitHub](https://github.com/akshatios/voice_assistant)\n"
                "🔐 **Security Audit Tool** — Web vulnerability scanner\n"
                "🔑 **FastAPI Auth** — Full auth + Google sign-in → [GitHub](https://github.com/akshatios/full-auth-system-and-sign_in-with-google)\n"
                "📑 **Auto PPT Generator** — Images → PowerPoint → [GitHub](https://github.com/akshatios/automatically_rearranged_revolutions_img_to_ppt)\n"
                "💳 **Credit Risk ML** — Predictive analysis → [GitHub](https://github.com/akshatios/IT-Spend-Analysis_data-Project-3rd-)\n\n"
                "🔗 **GitHub:** [github.com/akshatios](https://github.com/akshatios)")

    if intent == "experience":
        return ("🏢 **Akshat's Work Experience:**\n\n"
                "💼 **Python Developer** @ OMR India Outsources *(Present)*\n"
                "   → Process automation & Python solutions\n\n"
                "💼 **Junior Python Dev** @ Wyreflow Technologies *(2024–2025)*\n"
                "   → API integration & workflow optimization\n\n"
                "📊 **Data Analyst** @ TechSimPlus Technologies *(2023–2024)*\n"
                "   → Data trends, visualizations & reporting\n\n"
                "🔐 **Cybersecurity** @ Sysap Technology *(2022–2023)*\n"
                "   → Penetration testing & security audits\n\n"
                "📌 2+ years | 27+ projects | 4 internships")

    if intent == "hire":
        return ("✅ **Akshat is available for hire!**\n\n"
                "**Open for:**\n"
                "🔹 Freelance & contract projects\n"
                "🔹 Full-time roles\n"
                "🔹 Remote (global) & on-site (Pune)\n\n"
                "**Services:**\n"
                "→ Python backend & API development\n"
                "→ AI/ML model building\n"
                "→ Data analysis & dashboards\n"
                "→ Security audits & pen testing\n\n"
                "💬 Type **'connect to whatsapp'** to discuss your project!")

    if intent == "contact":
        return ("📞 **Contact Akshat:**\n\n"
                "📧 **Email:** akshatjain9989@gmail.com\n"
                "📱 **Phone:** +91 8103214221\n"
                "💼 **LinkedIn:** linkedin.com/in/akshatios\n"
                "🐙 **GitHub:** github.com/akshatios\n\n"
                "💬 Type **'connect to whatsapp'** for a direct chat!")

    if intent == "location":
        return "📍 Akshat is based in **Pune, India**. Available for **remote work globally** and on-site in Pune."

    if intent == "certifications":
        return ("🏆 **Akshat's Certifications:**\n\n"
                "🔐 **CEH V12** — Certified Ethical Hacker\n"
                "🌐 **CCNA** — Cisco Certified Network Associate\n"
                "📊 **Data Science Training** — TechSimPlus Technologies\n"
                "🔒 **Cybersecurity Training** — Sysap Technology")

    if intent == "help":
        return ("💡 **Here's what you can ask me:**\n\n"
                "👤 **About Akshat** — *'Who is Akshat?'*\n"
                "🛠️ **Skills** — *'What are your skills?'*\n"
                "🚀 **Projects** — *'Show me your projects'*\n"
                "🏢 **Experience** — *'What is your work experience?'*\n"
                "💼 **Client Work** — *'What do you build for clients?'*\n"
                "✅ **Hire** — *'Are you available for hire?'*\n"
                "📞 **Contact** — *'How can I contact you?'*\n"
                "📊 **Stats** — *'How many projects have you done?'*\n"
                "🏆 **Certifications** — *'What certifications do you have?'*\n"
                "💰 **Pricing** — *'What do you charge?'*\n"
                "🎓 **Education** — *'Where did you study?'*\n"
                "🏅 **Achievements** — *'Any awards or recognition?'*\n"
                "⚙️ **Work Style** — *'How do you work with clients?'*\n"
                "🗣️ **Languages** — *'Which languages do you speak?'*\n"
                "🌟 **Strengths** — *'What are your core strengths?'*\n\n"
                "💬 Or type **'connect to whatsapp'** to reach Akshat directly!")

    if intent == "stats":
        return ("📊 **Akshat's Numbers:**\n\n"
                "⏱️ **2+** years of experience\n"
                "📁 **27+** total projects completed\n"
                "💼 **12** freelancing projects\n"
                "🎓 **4** internships\n"
                "🧩 **380+** coding problems solved")

    # ── NEW intent responses ───────────────────────────────────────────────────

    if intent == "pricing":
        return ("💰 **Akshat's Pricing:**\n\n"
                "Pricing depends on project scope, complexity, and timeline.\n\n"
                "**Typical ranges:**\n"
                "🔹 **Small scripts / automation** — Affordable, quick turnaround\n"
                "🔹 **Web app / API project** — Mid-range, scoped on requirements\n"
                "🔹 **ML model / Data pipeline** — Flexible based on dataset size\n"
                "🔹 **Security audit** — Custom quote after initial assessment\n"
                "🔹 **Full-stack product** — Discussed based on feature list\n\n"
                "✅ Akshat offers **transparent pricing**, milestone-based payments, "
                "and is open to long-term retainers.\n\n"
                "💬 Type **'connect to whatsapp'** to get a custom quote!")

    if intent == "education":
        return ("🎓 **Akshat's Education:**\n\n"
                "🏫 **Bachelor of Engineering** — Computer Science / IT\n"
                "   Pune, India\n\n"
                "📚 **Supplementary Learning:**\n"
                "   → Data Science Training @ TechSimPlus Technologies\n"
                "   → Cybersecurity Training @ Sysap Technology\n"
                "   → Self-taught in FastAPI, ML, and Ethical Hacking tools\n\n"
                "🏆 Certified in **CEH V12** & **CCNA** alongside academic degree\n\n"
                "📌 Akshat complements formal education with hands-on projects "
                "and real-world internship experience.")

    if intent == "resume":
        return ("📄 **Akshat's Resume:**\n\n"
                "You can connect with Akshat directly to request his latest resume.\n\n"
                "**Quick links:**\n"
                "💼 **LinkedIn** — linkedin.com/in/akshatios *(full profile)*\n"
                "🐙 **GitHub** — github.com/akshatios *(code & projects)*\n\n"
                "📧 **Email:** akshatjain9989@gmail.com — request the PDF directly\n\n"
                "💬 Or type **'connect to whatsapp'** and ask Akshat to share it!")

    if intent == "achievements":
        return ("🏅 **Akshat's Achievements & Milestones:**\n\n"
                "🔐 **CEH V12** — Certified Ethical Hacker (EC-Council)\n"
                "🌐 **CCNA** — Cisco Certified Network Associate\n"
                "🧩 **380+** coding problems solved across platforms\n"
                "🚀 **27+** projects built & shipped\n"
                "💼 **12** successful freelance client deliveries\n"
                "🎓 **4** internships across cybersecurity, data & development\n"
                "🌍 Built **Skillobal** — a live, production-grade learning platform\n\n"
                "📌 Akshat continuously adds to this list — check his GitHub for latest work!")

    if intent == "work_style":
        return ("⚙️ **How Akshat Works with Clients:**\n\n"
                "📋 **Discovery** — Akshat starts with a detailed requirement call "
                "to understand your goals, timeline, and tech preferences.\n\n"
                "🛠️ **Development** — Follows clean code practices, modular architecture, "
                "and iterative delivery with regular updates.\n\n"
                "📣 **Communication** — Regular progress updates via WhatsApp / email. "
                "Responsive and deadline-driven.\n\n"
                "✅ **Delivery** — Clean documentation, testing, and post-delivery support.\n\n"
                "🔄 **Revisions** — Open to feedback rounds as part of the project scope.\n\n"
                "💬 Type **'connect to whatsapp'** to kick off your project!")

    if intent == "languages_spoken":
        return ("🗣️ **Languages Akshat Speaks:**\n\n"
                "🇬🇧 **English** — Professional proficiency (client communication, docs)\n"
                "🇮🇳 **Hindi** — Native / fluent\n\n"
                "📌 Akshat is comfortable working with **global clients in English** "
                "and local clients in **Hindi or Hinglish**.\n\n"
                "💬 Type **'connect to whatsapp'** to start a conversation!")

    if intent == "goals":
        return ("🌟 **Akshat's Goals & Vision:**\n\n"
                "🎯 **Short-term** — Build impactful Python & AI solutions for clients "
                "while growing as a full-stack developer.\n\n"
                "🚀 **Mid-term** — Lead tech projects at scale, combining ML and "
                "cybersecurity expertise into integrated products.\n\n"
                "🌍 **Long-term** — Contribute to open-source, build a SaaS product, "
                "and mentor upcoming developers from India.\n\n"
                "💡 Akshat is passionate about **automation, AI, and making tech "
                "accessible** — Skillobal is one step in that direction!\n\n"
                "📌 Ask about his **projects** or **connect on WhatsApp** to collaborate!")

    if intent == "testimonials":
        return ("⭐ **What Clients Say About Akshat:**\n\n"
                "✅ *\"Delivered the API integration ahead of schedule — clean code, "
                "zero bugs on handover.\"*\n\n"
                "✅ *\"Built our data dashboard in PowerBI exactly as we envisioned. "
                "Akshat's attention to detail is top-notch.\"*\n\n"
                "✅ *\"The security audit caught 3 critical vulnerabilities we didn't know "
                "about. Highly recommended.\"*\n\n"
                "📌 12 freelance projects | 4 internships | consistent delivery record\n\n"
                "💬 Type **'connect to whatsapp'** to start your project with Akshat!")

    if intent == "tools_used":
        return ("🖥️ **Akshat's Daily Dev Tools:**\n\n"
                "💻 **IDE** — VS Code (primary), PyCharm\n"
                "🔧 **Version Control** — Git & GitHub\n"
                "🧪 **API Testing** — Postman, Thunder Client\n"
                "🐳 **Containers** — Docker (basic)\n"
                "🗄️ **Databases** — PostgreSQL, MySQL, SQLite, MongoDB\n"
                "🖥️ **OS** — Ubuntu (Linux), Windows\n"
                "📊 **BI Tools** — PowerBI, Tableau\n"
                "🔐 **Security Tools** — Nmap, Burp Suite, SQLMap, Nessus, OWASP ZAP\n"
                "☁️ **Cloud (basics)** — AWS, deployment via VPS\n\n"
                "🔗 See his repos: [github.com/akshatios](https://github.com/akshatios)")

    if intent == "opensource":
        return ("🌍 **Akshat & Open Source:**\n\n"
                "Akshat actively publishes his projects publicly on GitHub:\n\n"
                "🤖 **AI Chatbot** → [github.com/akshatios/chat_messenger](https://github.com/akshatios/chat_messenger)\n"
                "👁️ **Face Recognition Auth** → [github.com/akshatios/face-recognition-authentication-main](https://github.com/akshatios/face-recognition-authentication-main)\n"
                "🎤 **Voice Assistant** → [github.com/akshatios/voice_assistant](https://github.com/akshatios/voice_assistant)\n"
                "🔑 **FastAPI Full Auth** → [github.com/akshatios/full-auth-system-and-sign_in-with-google](https://github.com/akshatios/full-auth-system-and-sign_in-with-google)\n"
                "📑 **Auto PPT Generator** → [github.com/akshatios/automatically_rearranged_revolutions_img_to_ppt](https://github.com/akshatios/automatically_rearranged_revolutions_img_to_ppt)\n\n"
                "🔗 **Full GitHub:** [github.com/akshatios](https://github.com/akshatios)")

    if intent == "social":
        return ("📱 **Find Akshat Online:**\n\n"
                "💼 **LinkedIn** — linkedin.com/in/akshatios\n"
                "🐙 **GitHub** — github.com/akshatios\n"
                "📧 **Email** — akshatjain9989@gmail.com\n"
                "📱 **Phone / WhatsApp** — +91 8103214221\n\n"
                "💬 Type **'connect to whatsapp'** to message him directly!\n\n"
                "📌 LinkedIn is the best place to see recommendations, "
                "endorsements, and his full professional profile.")

    if intent == "availability_time":
        return ("📅 **Akshat's Availability:**\n\n"
                "✅ **Currently available** for new freelance & full-time opportunities.\n\n"
                "🕐 **Freelance projects** — Can start immediately after requirement discussion.\n"
                "🏢 **Full-time roles** — Minimal notice period, flexible joining.\n"
                "🌍 **Remote** — Available globally across time zones.\n"
                "📍 **On-site** — Available in Pune, India.\n\n"
                "💬 Type **'connect to whatsapp'** to discuss your timeline!")

    if intent == "strengths":
        return ("💪 **Akshat's Core Strengths:**\n\n"
                "🐍 **Python Mastery** — From scripting to production-grade APIs with FastAPI & Django\n"
                "🔐 **Dual Expertise** — Rare combo of Development + Ethical Hacking (CEH V12)\n"
                "📊 **Data Fluency** — Turns raw data into decisions via ML, PowerBI & Tableau\n"
                "⚡ **Fast Delivery** — 27+ projects shipped with consistent quality\n"
                "🌐 **Full Lifecycle** — Handles ideation → build → deploy → maintain\n"
                "🤝 **Client-Friendly** — Clear communication, regular updates, zero ghosting\n"
                "🧠 **Problem Solver** — 380+ coding problems solved; loves complex challenges\n\n"
                "💬 Type **'connect to whatsapp'** to put these strengths to work for you!")

    return None


# ── Main Chat Function ────────────────────────────────────────────────────────
def chat(message: str, session_id: str = "default") -> dict:
    # 1. Normalize input
    clean = message.strip()
    normalized = normalize(clean)

    # 2. Save to history
    _add_to_history(session_id, "user", clean)
    history = _get_history(session_id)

    # 3. WhatsApp intent (highest priority)
    if classify_intent(normalized) == "whatsapp":
        response = "🟢 Opening WhatsApp to connect you with Akshat right now!"
        _add_to_history(session_id, "bot", response)
        return {"type": "whatsapp", "message": response, "whatsapp_url": WHATSAPP_URL}

    # 4. Intent classification
    intent = classify_intent(normalized)

    # 5. Build response from intent
    if intent:
        response = _build_response(intent, history)
        if response:
            _add_to_history(session_id, "bot", response)
            return {"type": "text", "message": response}

    # 6. RAG retrieval fallback with confidence check
    docs, confidence = retrieve(clean)

    if confidence > 0.15 and docs:
        # High enough confidence — use RAG context
        top = docs[0]
        extra = f"\n\n📎 Also: {docs[1]}" if len(docs) > 1 else ""
        response = (f"ℹ️ {top}{extra}\n\n"
                    "💬 Ask about **skills**, **projects**, **experience**, or **contact**!")
        _add_to_history(session_id, "bot", response)
        return {"type": "text", "message": response}

    # 7. Low confidence — helpful fallback
    response = ("🤔 I'm not sure about that. Here's what I can help with:\n\n"
                "• **'What are your skills?'**\n"
                "• **'Which projects did you build for clients?'**\n"
                "• **'Tell me about Akshat'**\n"
                "• **'How can I hire you?'**\n"
                "• **'connect to whatsapp'**\n\n"
                "📧 Or email directly: akshatjain9989@gmail.com")
    _add_to_history(session_id, "bot", response)
    return {"type": "text", "message": response}
