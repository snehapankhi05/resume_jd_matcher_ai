"""
Rule-based skill mining: finds skills that are NOT in the vocabulary by reading
how documents are written, instead of matching against a list.

Trusted places where skills are listed:
  1. a "Skills" / "Technical Skills" / "Tech Stack" / "Tools" section
  2. labelled lines   "Databases: MySQL, MongoDB"   "Frameworks: ..."
  3. cue phrases      "experience with X and Y", "such as X or Y", "using X"
  4. tokens whose spelling alone says "technology": Node.js, C#, PostgreSQL, STM32

Single capitalised words in the middle of ordinary prose ("shipped Looker
dashboards") are NOT guessed by the rules - too many are names or companies. That
case is what the optional LLM layer (skill_llm.py) is for.

Everything is deterministic and offline.
"""

import re

# ----------------------------------------------------------------- vocabulary of non-skills
SOFT_AND_GENERIC = {
    "communication", "teamwork", "team player", "leadership", "collaboration", "problem solving",
    "problem-solving", "time management", "adaptability", "creativity", "critical thinking",
    "interpersonal", "presentation", "multitasking", "work ethic", "attention to detail",
    "fast learner", "self-motivated", "analytical", "organisation", "organization", "negotiation",
    "english", "hindi", "gujarati", "marathi", "tamil", "telugu", "french", "german", "spanish",
    "etc", "more", "others", "other", "and more",
}

GENERIC_WORDS = {
    "data", "analysis", "analytics", "software", "engineering", "development", "design", "management",
    "testing", "system", "systems", "web", "application", "applications", "programming", "computer",
    "science", "technical", "project", "business", "marketing", "financial", "reporting", "customer",
    "service", "support", "research", "planning", "strategy", "operations", "quality", "assurance",
    "documentation", "training", "sales", "structures", "algorithms", "patterns", "concepts",
    "principles", "fundamentals", "methodologies", "practices", "processes", "solutions", "tools",
    "technologies", "skills", "experience", "knowledge", "team", "teams", "work", "environment",
    "tasks", "pipelines", "infrastructure", "cloud", "mobile", "frontend", "backend", "full", "stack",
    "senior", "junior", "lead", "engineer", "developer", "manager", "analyst", "intern", "internship",
    "years", "year", "months", "plus", "required", "preferred", "role", "responsibilities",
}

TITLE_WORDS = {
    "administrator", "admin", "engineer", "developer", "manager", "analyst", "executive", "intern",
    "consultant", "specialist", "architect", "officer", "associate", "scientist", "designer", "director",
    "coordinator", "technician", "programmer", "lead", "head", "assistant", "trainee", "fresher",
}

QUALIFIERS = {
    "strong", "good", "excellent", "solid", "proven", "hands-on", "hands", "on", "working", "basic",
    "advanced", "intermediate", "proficient", "proficiency", "experience", "experienced", "expertise",
    "knowledge", "familiarity", "familiar", "understanding", "deep", "extensive", "practical",
    "demonstrated", "in-depth", "sound", "thorough", "expert", "skilled", "exposure", "good",
    "the", "a", "an", "our", "your", "of", "in", "with", "and", "or", "to", "any", "some", "various",
    "relevant", "similar", "modern", "latest", "popular", "common", "like", "such", "as", "e.g",
    "including", "using", "use", "used", "plus",
}

VERBS = {
    "build", "building", "built", "manage", "managing", "managed", "develop", "developing", "developed",
    "design", "designing", "designed", "lead", "leading", "led", "work", "working", "worked",
    "responsible", "ensure", "ensuring", "maintain", "maintaining", "maintained", "create", "creating",
    "created", "implement", "implementing", "implemented", "write", "writing", "wrote", "support",
    "supporting", "collaborate", "collaborating", "drive", "driving", "own", "owning", "deliver",
    "delivering", "delivered", "participate", "analyze", "analyse", "analyzing", "deploy", "deploying",
    "deployed", "prepare", "prepared", "conduct", "conducted", "run", "ran", "running", "reduced",
    "improved", "migrated", "automated", "configured", "trained", "wrote", "shipped", "published",
    "modelled", "modeled", "debugged", "prototyped", "optimised", "optimized", "set", "ability", "able",
    "must", "should", "will", "can", "have", "has", "need", "needed", "required", "looking",
}

STOP_TOKENS = {  # an item is cut at the first of these (descriptive tail)
    "for", "to", "in", "on", "at", "by", "from", "that", "which", "while", "where", "when", "across",
    "within", "with", "using", "through", "via", "into", "per", "as", "is", "are", "be", "will", "can",
    "preferred", "required", "desired", "plus", "etc", "who", "you", "we", "they", "our", "your",
    "of", "than", "so", "such",
}

TRAILING_NOUNS = {
    "skills", "skill", "experience", "knowledge", "expertise", "proficiency", "framework", "frameworks",
    "library", "libraries", "interface", "interfaces", "protocol", "protocols", "tool", "tools",
    "tooling", "technologies", "technology", "software", "stack",
}

NOT_SKILL_TOKENS = {
    "the", "a", "an", "we", "our", "you", "your", "this", "these", "that", "it", "i", "he", "she",
    "they", "if", "but", "not", "no", "yes", "all", "any", "each", "every", "both", "also", "only",
    "linkedin", "youtube", "whatsapp", "iphone", "ebay", "paypal", "b2b", "b2c", "q1", "q2", "q3",
    "q4", "h1", "h2", "covid", "covid19", "mr", "mrs", "ms", "dr", "ltd", "inc", "llc", "pvt", "gpa",
    "cgpa", "ceo", "cto", "cfo", "hr", "usa", "uk", "india", "pdf", "id", "ok", "etc", "ph", "pm", "am",
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "january", "february",
    "march", "april", "may", "june", "july", "august", "september", "october", "november", "december",
}

_EDU_OR_ORG = re.compile(
    r"\b(university|college|institute|school|academy|inc|ltd|llc|pvt|corp|company|bank|"
    r"b\.?\s?tech|m\.?\s?tech|b\.?\s?sc|m\.?\s?sc|b\.?\s?e|m\.?\s?e|bca|mca|mba|ph\.?d|b\.?\s?com|"
    r"diploma|bachelor|master|degree|certified|certification)\b",
    re.IGNORECASE,
)

_BAD_SHAPES = re.compile(
    r"(@|https?:|www\.|\.com\b|\.in\b|\.org\b|\d{4,}|^\d+$|^[\W\d_]+$)",
    re.IGNORECASE,
)

# ----------------------------------------------------------------- section / label detection
_SKILL_HEADING = re.compile(
    r"^\W*(?:(?:technical|key|core|primary|relevant|it|professional|programming)\s+)?"
    r"(?:skills?(?:\s*set)?|technologies|tech(?:nology)?\s*stack|tools?(?:\s*(?:&|and)\s*technologies)?|"
    r"competenc(?:y|ies)|expertise|technical\s+proficienc(?:y|ies)|technical\s+expertise|"
    r"areas\s+of\s+expertise|skills\s*(?:&|and)\s*tools|tools\s*(?:&|and)\s*skills)\W*$",
    re.IGNORECASE,
)

_STOP_HEADING = re.compile(
    r"^\W*(?:education|(?:work |professional |relevant )?experience|employment(?: history)?|"
    r"(?:academic |personal |key )?projects?|summary|(?:professional )?profile|(?:career )?objective|"
    r"certifications?|achievements?|awards|internships?|publications|interests|hobbies|references|"
    r"declaration|personal\s+(?:details|information)|contact|responsibilities|requirements|"
    r"qualifications|about us|about the role|what you.ll do|benefits)\W*$",
    re.IGNORECASE,
)

_LABEL_LINE = re.compile(
    r"^\W*(?P<label>(?:technical |key |core |programming |primary |primary |tools? (?:and|&) )?"
    r"(?:skills?|technologies|tech stack|tools?|languages|frameworks?|libraries|databases?|"
    r"cloud(?: platforms?)?|platforms?|devops|back[- ]?end|front[- ]?end|testing|"
    r"methodologies|operating systems?|ides?|version control|monitoring|ml|ai|"
    r"cloud\s*(?:&|and)\s*devops|web|mobile|big data|analytics|bi tools?|crm|erp))"
    r"\s*[:\-–]\s*(?P<rest>\S.*)$",
    re.IGNORECASE,
)

_SPLIT = re.compile(
    r"\s*(?:,|;|\||•|●|▪|■|◦|·|\t|\s/\s|\s&\s|\band\b|\bor\b|\bplus\b|\bas well as\b)\s*",
    re.IGNORECASE,
)

_CUE = re.compile(
    r"(?:\b(?:experience|experienced|proficien(?:t|cy)|expertise|expert|knowledge|knowledgeable|"
    r"familiar(?:ity)?|skilled|hands[- ]on|working knowledge|understanding|exposure|competen(?:t|cy)|"
    r"background)\s+(?:with|in|of|on|using)\b"
    r"|\b(?:monitoring|logging|log analysis|scripting|programming|coding|debugg(?:ing|ed)|modell?(?:ing|ed)|"
    r"design(?:ed)?|development|automation|automated|testing|deployment|orchestrat(?:ion|ed)|"
    r"visuali[sz]ation|dashboards?|pipelines?|analysis|analytics|queries|notebooks?|tracing|"
    r"observability|provisioning|infrastructure(?: as code)?|written|implemented|hosted|running|"
    r"reports?|workflows?|integrations?|prototyp(?:ing|ed)|simulation|firmware|jobs?|models?)"
    r"\s+(?:with|in|on|using|via|through)\b"
    r"|\b(?:such as|including|includes?|e\.g|for example|like|using|built (?:with|using|on)|"
    r"developed (?:with|using|in)|deployed (?:with|using|on)|tech stack(?: is)?|technologies)\b)"
    r"\s*:?\s*",
    re.IGNORECASE,
)

# strong spellings that identify a technology anywhere in running text
_SHAPE_PATTERNS = [
    re.compile(r"(?<![\w.])[A-Za-z][A-Za-z0-9]*\.(?:js|py|net|io|ts|jsx)\b", re.IGNORECASE),
    re.compile(r"(?<![\w])\.NET\b"),
    re.compile(r"(?<![\w+#])[A-Za-z]+(?:\+\+|#)(?![\w+#])"),
    re.compile(r"\b[A-Z][a-z]{2,}[A-Z][A-Za-z]+\b"),            # PostgreSQL, TensorFlow, GitOps
    re.compile(r"\b[A-Z][A-Za-z]{0,5}\d+[A-Za-z]{0,3}\b"),      # STM32, EC2, S3, I2C, Web3
]


# ----------------------------------------------------------------- helpers
def _is_shapey(token: str) -> bool:
    return bool(token) and (
        token[0].isupper()
        or any(ch.isdigit() for ch in token)
        or any(ch in "+#." for ch in token[1:])
    )


def clean_item(raw: str, trusted: bool) -> str:
    """Turn one raw list item into a skill name, or '' if it is not one."""

    item = raw.strip().strip("•●▪■◦·-–—*>:").strip()

    item = re.sub(r"\(.*?\)", " ", item)          # drop "(canvas and model-driven)"
    item = re.sub(r"\b\d+\+?\s*(?:years?|yrs?)\b.*", "", item, flags=re.IGNORECASE)
    item = re.sub(r"\s+", " ", item).strip(" .,:;-")

    if not item:
        return ""

    tokens = item.split(" ")

    # cut the descriptive tail ("Looker for finance" -> "Looker")
    for i, token in enumerate(tokens):
        if i > 0 and token.lower() in STOP_TOKENS:
            tokens = tokens[:i]
            break

    # drop leading qualifiers / verbs ("Strong", "Managed", "hands-on")
    while tokens and (tokens[0].lower() in QUALIFIERS or tokens[0].lower() in VERBS):
        tokens = tokens[1:]

    if not tokens:
        return ""

    # keep the first run of "technology-looking" tokens; descriptive lowercase
    # tails ("Arduino prototyping", "Spring Boot microservices") are dropped.
    start = next((i for i, t in enumerate(tokens) if _is_shapey(t)), None)

    if start is None:

        # Lowercase single words are only trusted inside an explicit Skills list.
        if trusted and len(tokens) == 1 and re.fullmatch(r"[a-z][a-z0-9+#.\-]{1,19}", tokens[0]):
            word = tokens[0]
            if word in GENERIC_WORDS or word in SOFT_AND_GENERIC or word in NOT_SKILL_TOKENS:
                return ""
            return word

        return ""

    if start > 2:
        return ""

    end = start

    while end < len(tokens) and _is_shapey(tokens[end]):
        end += 1

    run = tokens[start:end]

    # drop trailing generic nouns that survived ("SPI interfaces" -> "SPI")
    while len(run) > 1 and run[-1].lower() in TRAILING_NOUNS:
        run = run[:-1]

    if len(run) == 1 and run[0].lower() in TRAILING_NOUNS:
        return ""

    name = " ".join(run)

    return name if _looks_like_skill(name) else ""


def _looks_like_skill(name: str) -> bool:

    if not (2 <= len(name) <= 40):
        return False

    low = name.lower()

    tokens = name.split()

    if len(tokens) > 4:
        return False

    if low in SOFT_AND_GENERIC or low in NOT_SKILL_TOKENS:
        return False

    if all(t.lower() in GENERIC_WORDS or t.lower() in NOT_SKILL_TOKENS for t in tokens):
        return False

    if tokens[0].lower() in NOT_SKILL_TOKENS or tokens[0].lower() in VERBS:
        return False

    # "Salesforce Administrator", "Data Scientist": a job title, not a skill
    if tokens[-1].lower() in TITLE_WORDS:
        return False

    if _EDU_OR_ORG.search(name) or _BAD_SHAPES.search(name):
        return False

    return True


def _split_items(text: str) -> list:
    """Split one list line into items; also yields the contents of parentheses
    ("Cloud (AWS, GCP)") as separate items."""

    items = []

    for inner in re.findall(r"\(([^()]*)\)", text):
        if "," in inner or " and " in inner.lower() or " or " in inner.lower():
            items.extend(_SPLIT.split(inner))

    outer = re.sub(r"\([^()]*\)", " ", text)

    items.extend(_SPLIT.split(outer))

    return [i for i in items if i and i.strip()]


# ----------------------------------------------------------------- mining
def _section_lines(lines):
    """Yield lines that belong to a Skills section (until the next heading)."""

    inside, taken = False, 0

    for line in lines:

        stripped = line.strip()

        if not stripped:
            continue

        if _SKILL_HEADING.match(stripped) and len(stripped.split()) <= 5:
            inside, taken = True, 0
            continue

        if inside:

            if _STOP_HEADING.match(stripped) or taken >= 30:
                inside = False
                continue

            taken += 1
            yield stripped


_CONTINUATION_WORDS = STOP_TOKENS | {
    "and", "or", "including", "experience", "knowledge", "familiarity", "understanding",
    "proficiency", "expertise", "exposure", "skills", "tools", "technologies", "like",
}

_BULLET_START = re.compile(r"^\s*(?:[•●▪■◦·\-–—*>]|\d+[.)])\s*")


def _paragraphs(lines) -> list:
    """
    Join lines that are only visually wrapped (typical for text extracted from
    PDFs) so a sentence such as "experience with<newline>FreeRTOS and SPI" stays
    in one piece. A new paragraph starts after sentence punctuation, after a
    short line (a heading / list item), or at a bullet.
    """

    paragraphs, current = [], ""

    for line in lines:

        stripped = line.strip()

        if not stripped:
            if current:
                paragraphs.append(current)
                current = ""
            continue

        if not current:
            current = stripped
            continue

        previous_ends = current[-1] in ".;:!?"
        short_previous = len(current) < 30

        last_word = current.split()[-1].lower().strip(",:")

        # a line that stops on a comma or a function word is mid-sentence
        continues = current.endswith(",") or last_word in _CONTINUATION_WORDS

        if previous_ends or _BULLET_START.match(stripped):
            paragraphs.append(current)
            current = stripped
        elif continues or not short_previous:
            current = current + " " + stripped
        else:
            paragraphs.append(current)
            current = stripped

    if current:
        paragraphs.append(current)

    return paragraphs


def mine_skills(text: str) -> list:
    """Candidate skills found by structure alone, in order of first appearance."""

    if not text or not text.strip():
        return []

    # keep sentence-ending dots, but not the dots of "e.g." / "i.e."
    text = re.sub(r"\b(e)\.(g)\.", r"\1.\2", text, flags=re.IGNORECASE)

    lines = text.replace("\r", "\n").split("\n")

    found = []

    def add(raw, trusted):
        name = clean_item(raw, trusted)
        if name:
            found.append(name)

    # 1. Skills sections, and 2. labelled lines
    for line in _section_lines(lines):

        label = _LABEL_LINE.match(line)

        for part in _split_items(label.group("rest") if label else line):
            add(part, trusted=True)

    for line in lines:

        label = _LABEL_LINE.match(line.strip())

        if label:
            for part in _split_items(label.group("rest")):
                add(part, trusted=True)

    # 3. cue phrases, clause by clause (on text with PDF line-wraps joined)
    flat = "\n".join(_paragraphs(lines))

    clauses = re.split(r"\n|;|•|\.\s+(?=[A-Z])", flat)

    for clause in clauses:

        cues = list(_CUE.finditer(clause))

        for i, cue in enumerate(cues):

            end = cues[i + 1].start() if i + 1 < len(cues) else len(clause)

            for part in _split_items(clause[cue.end():end]):
                add(part, trusted=False)

    # 4. strong spellings anywhere
    for pattern in _SHAPE_PATTERNS:
        for match in pattern.finditer(flat):
            add(match.group(0), trusted=False)

    # de-duplicate, keep first spelling
    seen, ordered = set(), []

    for name in found:

        key = re.sub(r"[^a-z0-9+#]", "", name.lower())

        if key and key not in seen:
            seen.add(key)
            ordered.append(name)

    return ordered
