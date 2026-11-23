"""
Offline, deterministic tests for skill extraction (no API key, no network).
Run from the project root:   python -m pytest tests/test_skill_extraction.py -q
"""
import os

os.environ["SKILL_EXTRACTION_MODE"] = "rules"   # never call the LLM in tests

from backend.app.services.skill_llm import _verified
from backend.app.services.skill_mining import mine_skills
from backend.app.services.skill_normalize import is_same_skill, satisfies
from backend.app.services.skill_service import (
    extract_and_match_skills,
    extract_skills_rules,
)


def names(text):
    return {s.lower() for s in extract_skills_rules(text)}


# ---------------------------------------------------------------- unseen skills
def test_skills_section_with_unknown_tools():
    found = names("Technical Skills: Splunk, Prometheus, Grafana, Terraform")
    assert {"splunk", "prometheus", "grafana"} <= found


def test_labelled_lines_and_parentheses():
    found = names("Databases: Snowflake, Redshift\nCloud (GCP, Azure DevOps)")
    assert {"redshift", "snowflake"} <= found


def test_cue_phrases_in_a_job_description():
    found = names("Requirements: experience with Looker and Salesforce; monitoring with Datadog or Splunk.")
    assert {"looker", "salesforce", "datadog", "splunk"} <= found


def test_pdf_line_wrap_inside_a_sentence():
    text = "Requirements: experience with\nFreeRTOS, I2C and SPI interfaces; debugging with JTAG."
    assert {"freertos", "i2c", "spi", "jtag"} <= names(text)


def test_technology_shaped_tokens_in_prose():
    found = names("We run PostgreSQL on EC2 and ship a Vue.js front end with STM32 firmware.")
    assert {"postgresql", "ec2", "vue.js", "stm32"} <= found


# ---------------------------------------------------------------- precision guards
def test_ordinary_english_is_not_a_skill():
    text = "Please express your interest. Strong communication and teamwork. Tally the votes. B.Tech from a University."
    assert names(text) == set()


def test_job_titles_and_soft_skills_are_rejected():
    assert "salesforce administrator" not in names("Skills: Salesforce Administrator, Leadership, English")


def test_no_double_counting_of_vocabulary_skills():
    found = names("Requirements: LLM APIs and Retrieval-Augmented Generation (RAG); REST APIs using FastAPI.")
    assert "llm apis" not in found and "retrieval-augmented generation" not in found
    assert {"llm", "rag", "rest api", "fastapi"} <= found


# ---------------------------------------------------------------- matching
def test_spelling_variants_match_but_different_skills_do_not():
    assert is_same_skill("Node.js", "NodeJS")
    assert is_same_skill("Postgres", "PostgreSQL")
    assert is_same_skill("Microsoft Excel", "Excel")
    assert not is_same_skill("React", "Redux")
    assert not is_same_skill("Java", "JavaScript")
    assert not is_same_skill("SQL", "MySQL")


def test_matching_is_directional():
    assert satisfies("Google Analytics 4", "Google Analytics")      # more specific satisfies
    assert satisfies("Azure Machine Learning", "Machine Learning")
    assert not satisfies("Machine Learning", "Azure Machine Learning")  # less specific does not
    assert not is_same_skill("Machine Learning", "Azure Machine Learning")


def test_unknown_skills_are_matched_between_resume_and_jd():
    result = extract_and_match_skills(
        "Skills: Python, Looker, Datadog",
        "Requirements: experience with Looker and Splunk; Python.",
    )
    assert "Looker" in result["matched_skills"]
    assert "Splunk" in result["missing_skills"]


# ---------------------------------------------------------------- LLM verification
def test_llm_output_must_appear_in_the_document():
    doc = "Skills: Python, Jira. Led a team. Salesforce Administrator."
    out = _verified(["Python", "Jira", "Kubernetes", "communication", "Salesforce Administrator"], doc)
    assert out == ["Python", "Jira"]
