"""
Extension of backend/app/core/skills.py. Importing this module registers
extra skills into TECH_SKILLS / SKILL_ALIASES / SKILL_DISPLAY_NAMES and defines
how skills relate to each other. skill_service imports it before compiling
patterns, so skills.py itself stays untouched.

Why this exists (from the evaluation run):
  * The vocabulary only covered ~85 tech skills, so anything else (Kafka, Jest,
    Dataverse, SEO, Excel ...) was invisible -> low resume recall, and a JD with
    no known skill got jd_skill_f1 = 0.
  * Skills were all-or-nothing. A candidate with scikit-learn and Streamlit got
    zero credit toward an LLM/FastAPI role, which pushed borderline candidates
    too low.
"""

from backend.app.core.skills import (
    SKILL_ALIASES,
    SKILL_DISPLAY_NAMES,
    TECH_SKILLS,
)

# key -> (display name, [aliases])
_NEW_SKILLS = {
    # JVM / backend
    "spring boot": ("Spring Boot", ["springboot"]),
    "hibernate": ("Hibernate", []),
    "maven": ("Maven", []),
    "gradle": ("Gradle", []),
    "junit": ("JUnit", []),
    "kafka": ("Kafka", ["apache kafka"]),
    "rabbitmq": ("RabbitMQ", []),
    "graphql": ("GraphQL", []),
    "grpc": ("gRPC", []),
    "express": ("Express", []),            # case-sensitive, see below
    "php": ("PHP", []),
    "kotlin": ("Kotlin", []),
    "scala": ("Scala", []),
    "c#": ("C#", ["csharp"]),
    "golang": ("Go", []),
    "rust": ("Rust", []),                  # case-sensitive
    "ruby": ("Ruby", []),                  # case-sensitive
    # Testing
    "jest": ("Jest", []),                  # case-sensitive
    "selenium": ("Selenium", []),
    "cypress": ("Cypress", []),
    # Data
    "pyspark": ("Spark", ["apache spark"]),
    "airflow": ("Airflow", ["apache airflow"]),
    "snowflake": ("Snowflake", []),        # case-sensitive
    "dbt": ("dbt", []),
    "hadoop": ("Hadoop", []),
    "elasticsearch": ("Elasticsearch", []),
    "tableau": ("Tableau", []),
    "mlflow": ("MLflow", []),
    # DevOps / cloud
    "jenkins": ("Jenkins", []),
    "terraform": ("Terraform", []),
    "ansible": ("Ansible", []),
    "github actions": ("GitHub Actions", []),
    "gitlab": ("GitLab", []),
    "nginx": ("Nginx", []),
    "azure devops": ("Azure DevOps", []),
    "firebase": ("Firebase", []),
    # Frontend / mobile
    "vue.js": ("Vue.js", ["vue", "vuejs"]),
    "angular": ("Angular", ["angularjs"]),
    "redux": ("Redux", []),
    "webpack": ("Webpack", []),
    "figma": ("Figma", []),
    "react native": ("React Native", []),
    "flutter": ("Flutter", []),
    "android": ("Android", []),
    "ios": ("iOS", []),                    # case-sensitive
    # Microsoft
    "dataverse": ("Dataverse", []),
    "sharepoint": ("SharePoint", []),
    "microsoft 365": ("Microsoft 365", ["office 365", "m365"]),
    # Office / finance
    "excel": ("Excel", []),                # case-sensitive
    "tally": ("Tally", []),                # case-sensitive
    "sap fico": ("SAP FICO", []),
    "sap abap": ("SAP ABAP", []),
    "sap hana": ("SAP HANA", []),
    # Marketing
    "seo": ("SEO", []),
    "google analytics": ("Google Analytics", ["ga4"]),
    "google ads": ("Google Ads", ["google adwords"]),
    "meta ads": ("Meta Ads", ["facebook ads"]),
    "canva": ("Canva", []),
    "hubspot": ("HubSpot", []),
    "mailchimp": ("Mailchimp", []),
    "photoshop": ("Photoshop", []),
    "wordpress": ("WordPress", []),
    "semrush": ("SEMrush", []),
}

for _key, (_display, _aliases) in _NEW_SKILLS.items():
    TECH_SKILLS.add(_key)
    SKILL_DISPLAY_NAMES[_key] = _display
    if _aliases:
        SKILL_ALIASES.setdefault(_key, []).extend(_aliases)


# Words that are also ordinary English ("express interest", "excel in",
# "tally the votes", "jest") only count as skills in these exact forms.
# Patterns are self-contained and compiled WITHOUT re.IGNORECASE.
_B = r"(?<![\w+#])"
CASE_SENSITIVE_PATTERNS = {
    "express": _B + r"(?:Express\.?js(?![\w+#])|Express(?=\s*(?:,|/|&|\+|and\b|framework\b)))",
    "excel": _B + r"(?:Microsoft Excel|MS Excel|Excel(?!\s+(?:in|at|as|on|with|your|the)\b))(?![\w+#])",
    # "Tally ERP 9" / "Tally Prime", or a bare "Tally" only when it ends a list
    # item ("Tally, Excel", "Tally.") so that "Tally the votes" is not a skill.
    "tally": _B + r"(?:Tally\s?(?:ERP\s?9|ERP|Prime)(?![\w+#])|Tally(?=\s*(?:[,;/|)]|\.(?:\s|$)|$)))",
    "jest": _B + r"Jest(?![\w+#])",
    "rust": _B + r"Rust(?![\w+#])",
    "ruby": _B + r"Ruby(?![\w+#])",
    "snowflake": _B + r"Snowflake(?![\w+#])",
    "ios": _B + r"iOS(?![\w+#])",
}


# Having the key on the left is enough to satisfy a JD requirement on the right.
# (Used for matching only; resume_skills still lists what was literally written.)
SKILL_IMPLIES = {
    "github": ["git"],
    "gitlab": ["git"],
    "chromadb": ["vector database"],
    "pinecone": ["vector database"],
    "faiss": ["vector database"],
    "mysql": ["sql"],
    "postgresql": ["sql"],
    "sqlite": ["sql"],
    "react": ["javascript"],
    "next.js": ["react", "javascript"],
    "node.js": ["javascript"],
    "express": ["node.js", "javascript"],
    "typescript": ["javascript"],
    "vue.js": ["javascript"],
    "react native": ["react", "javascript"],
    "tailwind css": ["css"],
    "power apps": ["power platform"],
    "power automate": ["power platform"],
    "power bi": ["power platform"],
    "copilot studio": ["power platform"],
    "ai builder": ["power platform"],
    "azure machine learning": ["azure", "machine learning"],
    "azure devops": ["azure"],
    "langchain": ["llm"],
    "langgraph": ["llm"],
    "llamaindex": ["llm"],
    "spring boot": ["java"],
    "pyspark": ["python"],
    "fastapi": ["python"],
    "flask": ["python"],
    "django": ["python"],
    "streamlit": ["python"],
}


# Related skills earn partial credit when a JD skill is missing.
# Same tight group -> TIGHT_CREDIT, same broad group -> BROAD_CREDIT.
TIGHT_GROUPS = [
    {"llm", "generative ai", "rag", "langchain", "langgraph", "llamaindex", "crewai", "autogen",
     "prompt engineering", "openai", "groq", "gemini", "ollama", "agentic ai", "huggingface"},
    {"vector database", "chromadb", "pinecone", "faiss", "elasticsearch"},
    {"machine learning", "deep learning", "nlp", "tensorflow", "pytorch", "scikit-learn", "opencv",
     "nltk", "spacy", "azure machine learning", "huggingface", "mlflow"},
    {"fastapi", "flask", "django", "streamlit"},
    {"javascript", "typescript", "react", "next.js", "node.js", "express", "vue.js", "angular", "redux"},
    {"html", "css", "tailwind css", "javascript", "typescript"},
    {"sql", "mysql", "postgresql", "sqlite", "mongodb", "redis", "sqlalchemy", "snowflake"},
    {"rest api", "graphql", "grpc", "jwt"},
    {"docker", "kubernetes", "jenkins", "ci/cd", "github actions", "gitlab", "terraform", "ansible"},
    {"aws", "azure", "gcp", "firebase"},
    {"java", "spring boot", "hibernate", "maven", "gradle", "junit", "kotlin", "scala"},
    {"pytest", "jest", "junit", "selenium", "cypress"},
    {"power platform", "power apps", "power automate", "power bi", "copilot studio", "ai builder",
     "dataverse", "dynamics 365", "business central", "sharepoint", "microsoft 365"},
    {"seo", "google analytics", "google ads", "meta ads", "hubspot", "mailchimp", "semrush"},
    {"excel", "tally", "sap fico", "sap abap", "sap hana", "tableau"},
    {"kafka", "rabbitmq"},
    {"pyspark", "airflow", "hadoop", "dbt", "snowflake"},
]

BROAD_GROUPS = [
    {"llm", "generative ai", "rag", "langchain", "langgraph", "llamaindex", "crewai", "autogen",
     "prompt engineering", "openai", "groq", "gemini", "ollama", "agentic ai", "huggingface",
     "vector database", "chromadb", "pinecone", "faiss", "machine learning", "deep learning", "nlp",
     "tensorflow", "pytorch", "scikit-learn", "opencv", "nltk", "spacy", "azure machine learning",
     "numpy", "pandas", "mlflow"},
    {"fastapi", "flask", "django", "streamlit", "spring boot", "node.js", "express", "rest api",
     "graphql", "grpc", "jwt", "sql", "mysql", "postgresql", "mongodb", "redis", "sqlalchemy",
     "kafka", "rabbitmq", "hibernate"},
    {"python", "java", "c", "c++", "c#", "javascript", "typescript", "golang", "rust", "ruby", "php",
     "kotlin", "scala"},
    {"docker", "kubernetes", "jenkins", "ci/cd", "github actions", "gitlab", "terraform", "ansible",
     "aws", "azure", "gcp", "linux", "nginx", "azure devops"},
    {"html", "css", "tailwind css", "javascript", "typescript", "react", "next.js", "vue.js",
     "angular", "redux", "webpack", "figma"},
]

TIGHT_CREDIT = 0.5
BROAD_CREDIT = 0.25
