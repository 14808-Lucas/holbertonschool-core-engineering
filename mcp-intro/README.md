## MCP Architecture Summary

**What MCP is:** The Model Context Protocol is an open standard for how AI
applications talk to outside systems such as files, APIs, or databases. It
defines the message format, so any MCP-compatible app can use any
MCP-compatible server without a custom integration for each pair.

**MCP host:** The AI application the user interacts with, for example an
agent, an IDE, or a desktop chat app. It runs the model, decides when
outside data or actions are needed, and manages one or more MCP clients.

**MCP client:** A connector that lives inside the host. Each client holds
one dedicated connection to one MCP server, so a host that uses three
servers creates three clients. The client discovers what the server offers
(`tools/list`, `resources/list`) and sends requests to it.

**MCP server:** A program that exposes capabilities to clients. It can run
locally (communicating over stdio) or remotely (over HTTP). In this
project, `server/learning_server.py` is the server and it serves data from
`data/topics.json`.

**Tools:** Functions the model can ask the server to run, with typed
inputs and a result. They perform an action or a lookup, for example
`search_topics("decorators")`.

**Resources:** Read-only data the server makes available as context, each
identified by a URI. They do not change anything, for example the full
topic catalog.

**Why expose only what is needed:** Every tool or resource a server exposes
is something a model can trigger, sometimes based on untrusted input.
Keeping the server small and read-only where possible limits the damage
from mistakes or misuse, makes the server easier to review and test, and
gives the model fewer, clearer choices.

**Example flow:** A student asks the agent, "I want to study Python
decorators. What should I review first?" The agent (host) uses its MCP
client to call the server's topic tool. The server looks up "decorators"
in `topics.json` and returns its prerequisites and description. The model
then uses that structured data to write a student-friendly answer.

## Setup

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

## Running the Server

The server uses FastMCP with the stdio transport (the default).

    python3 server/learning_server.py

The server name is `Programming Learning Server`. When it starts, FastMCP
shows a banner and a "Starting MCP server ... with transport 'stdio'"
message on stderr. The server then waits for MCP messages on stdin, so the
terminal appears idle. Stop it with `Ctrl+C`. Normally an MCP client starts
the server for you.

Note: in a stdio server, stdout carries the MCP messages, so the server
must never `print()`. Use `logging`, which writes to stderr.