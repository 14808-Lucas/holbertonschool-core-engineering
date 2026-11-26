#!/usr/bin/env python3
"""Shared model configuration and setup checks for every agent.

Reads MODEL_NAME and OLLAMA_API_BASE from the project's .env file, and
provides check_configuration() to report setup problems clearly before
any agent runs.
"""
import json
import os
import urllib.error
import urllib.request

from dotenv import load_dotenv
from google.adk.models.lite_llm import LiteLlm

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(PROJECT_ROOT, ".env")
load_dotenv(ENV_PATH)

MODEL_NAME = os.getenv("MODEL_NAME", "").strip()
OLLAMA_API_BASE = os.getenv("OLLAMA_API_BASE", "").strip()
OLLAMA_PREFIXES = ("ollama_chat/", "ollama/")


class ConfigError(Exception):
    """Raised when the project is not configured correctly."""


def build_model():
    """Return a LiteLlm model object configured from MODEL_NAME."""
    return LiteLlm(model=MODEL_NAME)


def check_environment():
    """Check that the required environment variables are set."""
    if not os.path.isfile(ENV_PATH):
        raise ConfigError(
            ".env file not found at {}.\n"
            "  Fix: cp .env.example .env".format(ENV_PATH))
    if not MODEL_NAME:
        raise ConfigError(
            "MODEL_NAME is not set in .env.\n"
            "  Example: MODEL_NAME=ollama_chat/llama3.2")
    if MODEL_NAME.startswith(OLLAMA_PREFIXES) and not OLLAMA_API_BASE:
        raise ConfigError(
            "OLLAMA_API_BASE is not set in .env.\n"
            "  Example: OLLAMA_API_BASE=http://localhost:11434")


def get_ollama_models():
    """Return the names of the models installed in Ollama."""
    url = OLLAMA_API_BASE.rstrip("/") + "/api/tags"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, OSError) as error:
        raise ConfigError(
            "Cannot reach Ollama at {} ({}).\n"
            "  Fix: start it with 'sudo systemctl start ollama' or "
            "'ollama serve'.".format(OLLAMA_API_BASE, error))
    return [model["name"] for model in data.get("models", [])]


def check_ollama_model():
    """Check that Ollama is running and the configured model is pulled."""
    model = MODEL_NAME.split("/", 1)[1]
    if ":" not in model:
        model += ":latest"
    installed = get_ollama_models()
    if model not in installed:
        raise ConfigError(
            "Model '{}' is not available in Ollama.\n"
            "  Installed models: {}\n"
            "  Fix: ollama pull {}".format(
                model, ", ".join(installed) or "none", model))


def check_configuration():
    """Run every setup check. Raise ConfigError on the first problem."""
    check_environment()
    if MODEL_NAME.startswith("ollama/"):
        print("Warning: use the 'ollama_chat/' prefix instead of "
              "'ollama/' to avoid tool-call loops.")
    if MODEL_NAME.startswith(OLLAMA_PREFIXES):
        check_ollama_model()
