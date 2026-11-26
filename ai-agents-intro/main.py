#!/usr/bin/env python3
"""Entry point for the AI Study Guide Generator.

Usage:
    ./main.py "Python decorators"
    ./main.py                      (asks for a topic)

Sequential workflow:
    Topic input
    -> Explainer Agent
    -> Practice Designer Agent
    -> Draft Study Guide
    -> Reviewer Agent
    -> Final Markdown Assembly
    -> Validation Tool
    -> Save Markdown Tool

Exit status: 0 on success, 1 if the guide could not be generated,
saved, or did not pass validation.
"""
import asyncio
import os
import sys

from google.adk.runners import InMemoryRunner
from google.genai import types

from agents.explainer_agent import explainer_agent
from agents.model_config import ConfigError
from agents.model_config import MODEL_NAME
from agents.model_config import check_configuration
from agents.practice_designer_agent import practice_designer_agent
from agents.reviewer_agent import reviewer_agent
from tools.file_writer import save_markdown_file
from tools.validation import fix_section_headings
from tools.validation import validate_required_sections

APP_NAME = "study_guide_generator"
USER_ID = "student"
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "output", "study_guide.md")
TOTAL_STEPS = 6


class AgentError(Exception):
    """Raised when an agent returns no usable output."""


# ---------------------------------------------------------------------
# Agent execution
# ---------------------------------------------------------------------
async def run_agent_async(agent, text):
    """Send a text message to an agent and return its final response."""
    runner = InMemoryRunner(agent=agent, app_name=APP_NAME)
    session = await runner.session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID
    )
    message = types.Content(role="user", parts=[types.Part(text=text)])

    final_text = ""
    async for event in runner.run_async(
        user_id=USER_ID, session_id=session.id, new_message=message
    ):
        if event.is_final_response() and event.content:
            final_text = "".join(
                part.text for part in event.content.parts if part.text
            )
    return final_text.strip()


def run_agent(agent, text):
    """Run an agent and return its response. Raise AgentError if empty."""
    response = asyncio.run(run_agent_async(agent, text))
    if not response:
        raise AgentError(
            "{} returned an empty response. Try running again or use a "
            "different model.".format(agent.name))
    return response


def run_explainer_agent(topic):
    """Return the explanation, key concepts and example for a topic."""
    return run_agent(explainer_agent, topic)


def run_practice_designer_agent(topic, explanation):
    """Return a practice exercise based on the topic and explanation."""
    request = "Topic: {}\n\nExplanation:\n{}".format(topic, explanation)
    return run_agent(practice_designer_agent, request)


def run_reviewer_agent(draft):
    """Return review sections for a draft study guide."""
    request = "Draft study guide to review:\n\n{}".format(draft)
    return run_agent(reviewer_agent, request)


# ---------------------------------------------------------------------
# Markdown assembly
# ---------------------------------------------------------------------
def assemble_markdown(topic, explanation, practice):
    """Build the draft guide from the topic and the first two agents."""
    return "# Topic\n\n{}\n\n{}\n\n{}".format(topic, explanation, practice)


def assemble_final_markdown(draft, review):
    """Add the review to the draft and fix the section heading levels."""
    final_markdown = "{}\n\n{}".format(draft, review)
    return fix_section_headings(final_markdown)


# ---------------------------------------------------------------------
# Input and output helpers
# ---------------------------------------------------------------------
def get_topic_from_user():
    """Return the topic from the command line, or ask for it."""
    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:])
    try:
        return input("Enter a programming topic: ")
    except EOFError:
        return ""


def validate_topic(topic):
    """Return the cleaned topic. Raise ValueError if it is empty."""
    if not topic.strip():
        raise ValueError(
            "Topic cannot be empty.\n"
            "  Example: ./main.py \"Python decorators\"")
    return topic.strip()


def print_error(message):
    """Print an error message to standard error."""
    print("Error: {}".format(message), file=sys.stderr)


def progress(step, message):
    """Print a numbered progress message."""
    print("[{}/{}] {}".format(step, TOTAL_STEPS, message))


def report_validation(result):
    """Print the validation result, listing missing sections if any."""
    if result["valid"]:
        print("      Validation passed: all required sections found.")
    else:
        print("      Validation failed. Missing sections:")
        for section in result["missing_sections"]:
            print("        - {}".format(section))


# ---------------------------------------------------------------------
# Main workflow
# ---------------------------------------------------------------------
def main():
    """Run the full study guide workflow. Return the exit status."""
    try:
        check_configuration()
        topic = validate_topic(get_topic_from_user())
    except (ConfigError, ValueError) as error:
        print_error(error)
        return 1

    print("Model: {}".format(MODEL_NAME))
    print("Generating a study guide for: {}\n".format(topic))

    try:
        progress(1, "Explainer Agent: writing the explanation...")
        explanation = run_explainer_agent(topic)

        progress(2, "Practice Designer Agent: designing the exercise...")
        practice = run_practice_designer_agent(topic, explanation)
        draft = assemble_markdown(topic, explanation, practice)

        progress(3, "Reviewer Agent: reviewing the draft...")
        review = run_reviewer_agent(draft)
    except AgentError as error:
        print_error(error)
        return 1

    progress(4, "Assembling the final Markdown...")
    final_markdown = assemble_final_markdown(draft, review)

    progress(5, "Validating required sections...")
    validation_result = validate_required_sections(final_markdown)
    report_validation(validation_result)

    progress(6, "Saving the study guide...")
    save_result = save_markdown_file(OUTPUT_PATH, final_markdown)
    if save_result.startswith("Error"):
        print_error(save_result[len("Error: "):])
        return 1
    print("      " + save_result)

    if not validation_result["valid"]:
        print_error("the study guide was saved but is incomplete. "
                    "Run again or adjust the agent prompts.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
