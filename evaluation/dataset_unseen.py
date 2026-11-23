"""
Held-out examples whose skills are deliberately NOT in the vocabulary
(skills.py / skills_extended.py): Prometheus, Grafana, Splunk, Databricks, BigQuery,
Looker, Salesforce, Zendesk, FreeRTOS, STM32, Unity ... The point is to measure how
well skill extraction generalises to skills nobody listed in advance.

Gold = named tools, technologies, languages, frameworks, platforms, protocols and
well-known practices (e.g. GitOps). Not gold: soft skills, job titles, generic
activities ("log analysis", "financial reporting").
Do NOT add these skills to the vocabulary: that would turn this set into a
memory test. Write new unseen cases instead.
"""
from evaluation.dataset import _ex

SRE_JD = """Site Reliability Engineer. Requirements: hands-on experience with Kubernetes and Helm;
monitoring with Prometheus and Grafana; log analysis in Splunk or Datadog; infrastructure as code using
Terraform; scripting in Python or Bash; GitOps tooling such as ArgoCD. On-call rotation required. Strong communication."""

SRE_RESUME = """Rohan Desai. Site reliability engineer, 4 years.
Technical Skills: Kubernetes, Helm, Prometheus, Grafana, Datadog, Terraform, Python, Bash, Jenkins, AWS.
Experience: Ran production Kubernetes clusters for a fintech platform; built Grafana dashboards and alerting on
Prometheus; automated deployments with Helm charts and Jenkins pipelines; reduced incident response time by 35 percent.
Education: B.E. Computer Engineering."""

DE_JD = """Data Engineer. You will build batch and streaming pipelines on Databricks and BigQuery.
Requirements: SQL and Python; Apache Airflow for orchestration; experience with Snowflake or Redshift;
dashboards in Looker; data modelling with dbt. Nice to have: Kafka, Terraform."""

DE_RESUME = """Meera Iyer. Data engineer, 3 years.
Skills: Python, SQL, Databricks, BigQuery, Airflow, dbt, Tableau, Docker.
Built ELT pipelines on BigQuery orchestrated by Airflow, modelled marts with dbt and published Tableau dashboards.
Migrated nightly Spark jobs to Databricks. Education: B.Tech."""

ANALYTICS_PROSE_RESUME = """Sanjay Rao. I spent five years as an analytics engineer. I modelled warehouse tables in dbt,
wrote Python and SQL for the transformations, orchestrated everything with Airflow, and shipped Looker dashboards for
finance. Earlier I migrated reports from Redshift to BigQuery."""

CRM_JD = """Salesforce Administrator. Manage Salesforce CRM, build flows and reports, support the sales team through
Jira tickets and document processes in Confluence. Experience with Zendesk integrations preferred. Minimum 2 years."""

CRM_RESUME = """Anita Verma. CRM administrator, 3 years.
Skills: Salesforce, Jira, Confluence, HubSpot, Excel.
Configured Salesforce objects, validation rules and approval flows; trained 40 sales reps; managed the support
backlog in Jira and wrote Confluence documentation."""

EMBEDDED_JD = """Embedded Systems Engineer. Develop firmware in C for ARM Cortex-M microcontrollers; experience with
FreeRTOS, I2C and SPI interfaces; debugging with JTAG; model-based design in MATLAB and Simulink.
Familiarity with Arduino prototyping is a plus."""

EMBEDDED_RESUME = """Kabir Singh. Embedded engineer.
Skills: C, C++, FreeRTOS, MATLAB, Simulink, Arduino, STM32, I2C, SPI, UART.
Wrote bare-metal firmware in C for STM32 microcontrollers, debugged with JTAG and an oscilloscope, and prototyped
sensor boards on Arduino."""

GAME_RESUME = """Dev Patel. Game developer.
Skills: Unity, Unreal Engine, C#, Blender, Perforce, Photon.
Built a multiplayer racing game in Unity with C#, optimised shaders and set up Perforce workflows."""

SRE_JD_SK = ["Kubernetes", "Helm", "Prometheus", "Grafana", "Splunk", "Datadog", "Terraform", "Python",
             "Bash", "ArgoCD", "GitOps"]
DE_JD_SK = ["Databricks", "BigQuery", "SQL", "Python", "Airflow", "Snowflake", "Redshift", "Looker", "dbt",
            "Kafka", "Terraform"]

UNSEEN_EXAMPLES = [
    _ex("unseen_sre_strong", SRE_RESUME, SRE_JD, "strong", [55, 100], True,
        ["Kubernetes", "Helm", "Prometheus", "Grafana", "Datadog", "Terraform", "Python", "Bash", "Jenkins", "AWS"],
        SRE_JD_SK,
        ["Kubernetes", "Helm", "Prometheus", "Grafana", "Datadog", "Terraform", "Python", "Bash"],
        ["Splunk", "ArgoCD", "GitOps"], unseen=True),

    _ex("unseen_data_engineer_strong", DE_RESUME, DE_JD, "strong", [50, 100], True,
        ["Python", "SQL", "Databricks", "BigQuery", "Airflow", "dbt", "Tableau", "Docker", "Spark"],
        DE_JD_SK,
        ["Databricks", "BigQuery", "SQL", "Python", "Airflow", "dbt"],
        ["Snowflake", "Redshift", "Looker", "Kafka", "Terraform"], unseen=True),

    _ex("unseen_prose_resume_vs_data_engineer", ANALYTICS_PROSE_RESUME, DE_JD, "strong", [50, 100], True,
        ["dbt", "Python", "SQL", "Airflow", "Looker", "Redshift", "BigQuery"],
        DE_JD_SK,
        ["BigQuery", "SQL", "Python", "Airflow", "Redshift", "Looker", "dbt"],
        ["Databricks", "Snowflake", "Kafka", "Terraform"], unseen=True),

    _ex("unseen_crm_strong", CRM_RESUME, CRM_JD, "strong", [55, 100], True,
        ["Salesforce", "Jira", "Confluence", "HubSpot", "Excel"],
        ["Salesforce", "Jira", "Confluence", "Zendesk"],
        ["Salesforce", "Jira", "Confluence"], ["Zendesk"], unseen=True),

    _ex("unseen_embedded_strong", EMBEDDED_RESUME, EMBEDDED_JD, "strong", [55, 100], True,
        ["C", "C++", "FreeRTOS", "MATLAB", "Simulink", "Arduino", "STM32", "I2C", "SPI", "UART", "JTAG"],
        ["C", "ARM Cortex-M", "FreeRTOS", "I2C", "SPI", "JTAG", "MATLAB", "Simulink", "Arduino"],
        ["C", "FreeRTOS", "I2C", "SPI", "JTAG", "MATLAB", "Simulink", "Arduino"],
        ["ARM Cortex-M"], unseen=True),

    _ex("unseen_game_dev_vs_sre", GAME_RESUME, SRE_JD, "mismatch", [0, 30], False,
        ["Unity", "Unreal Engine", "C#", "Blender", "Perforce", "Photon"],
        SRE_JD_SK, [], SRE_JD_SK, unseen=True),
]
