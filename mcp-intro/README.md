# MCP Servers in Python

## Description

A **Programming Learning MCP Server** built with FastMCP, plus a client
and an LLM agent that consume it through the Model Context Protocol.

The server exposes a small local dataset of Python study topics
(`data/topics.json`) as MCP **tools** and an MCP **resource**. A study
assistant agent (Google ADK + Ollama `llama3.2`) connects to the server
as an external capability, calls its tools, and writes a short
student-facing answer such as what to review before learning decorators.

```text
mcp-intro/
├── server/
│   ├── learning_server.py   # FastMCP server: tools + resource
│   └── __init__.py
├── client/
│   ├── mcp_client.py        # FastMCP client that tests the server
│   ├── agent.py             # ADK agent that uses the server over MCP
│   └── __init__.py
├── data/
│   └── topics.json          # 6 Python topics (the server's data)
├── output/
│   └── sample_agent_response.md
├── README.md
├── requirements.txt
├── .env.example
└── .gitignore
```

The server code and the agent code are independent: the agent never
imports anything from `server/` and never reads `topics.json` directly.

## MCP Architecture Summary

**What MCP is:** The Model Context Protocol is an open standard for how
AI applications talk to outside systems such as files, APIs, or
databases. It defines the message format (JSON-RPC 2.0), so any
MCP-compatible app can use any MCP-compatible server without a custom
integration for each pair.

**MCP host:** The AI application the user interacts with, for example an
agent, an IDE, or a desktop chat app. It runs the model, decides when
outside data or actions are needed, and manages one or more MCP clients.

**MCP client:** A connector that lives inside the host. Each client holds
one dedicated connection to one MCP server, so a host that uses three
servers creates three clients. The client discovers what the server
offers (`tools/list`, `resources/list`) and sends requests to it.

**MCP server:** A program that exposes capabilities to clients. It can run
locally (communicating over stdio) or remotely (over HTTP). In this
project, `server/learning_server.py` is the server and it serves data
from `data/topics.json`.

**Tools:** Functions the model can ask the server to run, with typed
inputs and a result. They perform an action or a lookup, for example
`search_topics("decorators")`.

**Resources:** Read-only data the server makes available as context,
each identified by a URI. They do not change anything, for example the
topic catalog at `topics://catalog`.

**Why expose only what is needed:** Every tool or resource a server
exposes is something a model can trigger, sometimes based on untrusted
input. Keeping the server small and read-only where possible limits the
damage from mistakes or misuse, makes the server easier to review and
test, and gives the model fewer, clearer choices.

**Example flow:** A student asks the agent, "I want to study Python
decorators. What should I review first?" The agent (host) uses its MCP
client to call `search_topics`, then `get_topic_details`. The server
looks up the topic in `topics.json` and returns its prerequisites, key
concepts, and common mistakes. The model then uses that structured data
to write a student-friendly answer.

## Requirements

- Python 3.10+ (FastMCP requires 3.10 or newer; developed on 3.14)
- Node.js 22.19+ and `npx` (for the MCP Inspector)
- Ollama with the `llama3.2` model pulled (`ollama pull llama3.2`)
- Python packages (`requirements.txt`): `fastmcp` (4.x),
  `python-dotenv`, `google-adk`, `litellm`

Developed and tested on Ubuntu (WSL2) with FastMCP 4.2.6 and MCP SDK
2.3.0.

## Setup

```bash
cd mcp-intro
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
fastmcp version              # confirms FastMCP is installed
cp .env.example .env         # then adjust values if needed
```

`.env` holds local configuration and is ignored by git. Variables:

| Variable | Default | Purpose |
|---|---|---|
| `MCP_SERVER_URL` | `http://localhost:8000/mcp` | Where the agent finds the MCP server |
| `MODEL_NAME` | `ollama_chat/llama3.2` | LiteLLM model string for the agent |
| `OLLAMA_API_BASE` | `http://localhost:11434` | Ollama address |

No API keys or secrets are needed.

## How to Run the Server

**stdio (default):**

```bash
python3 server/learning_server.py
```

FastMCP shows a banner and `Starting MCP server 'Programming Learning
Server' with transport 'stdio'` on **stderr**, then waits for MCP
messages on stdin, so the terminal looks idle. Stop it with `Ctrl+C`.
Normally a client starts the server for you over stdio.

**HTTP (needed by the agent):**

```bash
fastmcp run server/learning_server.py:mcp --transport http --port 8000
```

Wait for `Uvicorn running on http://127.0.0.1:8000`. The MCP endpoint is
`http://localhost:8000/mcp`. Leave it running while using the agent.

Note: in a stdio server, stdout carries the MCP messages, so the server
never calls `print()`. Only `logging` (stderr) is safe.

## How to Test the Server

The server was tested directly, before connecting any agent.

**FastMCP client (all checks in one command):**

```bash
python3 client/mcp_client.py 2>/dev/null
```

`client/mcp_client.py` starts the server over stdio and checks, one at a
time: the connection, the tool list, `search_topics`,
`get_topic_details`, the `topics://catalog` resource, and four invalid
inputs. `2>/dev/null` hides the server's banner.

**MCP Inspector CLI (manual checks):**

```bash
npx @modelcontextprotocol/inspector --cli python3 server/learning_server.py \
  --method tools/list --format json

npx @modelcontextprotocol/inspector --cli python3 server/learning_server.py \
  --method tools/call --tool-name search_topics \
  --tool-args-json '{"query": "decorators"}' --format json

npx @modelcontextprotocol/inspector --cli python3 server/learning_server.py \
  --method tools/call --tool-name get_topic_details \
  --tool-args-json '{"topic_id": "python-decorators"}' --format json

npx @modelcontextprotocol/inspector --cli python3 server/learning_server.py \
  --method resources/read --uri topics://catalog --format json
```

**MCP Inspector UI:**

```bash
npx @modelcontextprotocol/inspector python3 server/learning_server.py
```

Open the URL it prints, click **Connect**, and use the Tools and
Resources tabs.

**Style:**

```bash
pycodestyle server/ client/
```

## How to Run the Agent

The agent connects to the server over Streamable HTTP, so it needs two
terminals. Ollama must be running.

```bash
# Terminal 1: MCP server
fastmcp run server/learning_server.py:mcp --transport http --port 8000

# Terminal 2: agent (default question, or pass your own)
python3 client/agent.py
python3 client/agent.py "I want to study list comprehensions"
```

How it connects: `client/agent.py` creates an ADK `McpToolset` with
`StreamableHTTPConnectionParams(url=MCP_SERVER_URL)` and
`tool_filter=["search_topics", "get_topic_details"]`, so the model can
only see those two tools. Before running the model it lists the
server's tools to prove the server is reachable. Each MCP tool call is
printed (`[MCP call] ...`), and the question, tool calls, and answer
are saved to `output/sample_agent_response.md`. If the model answers
without calling `search_topics`, the response is not saved and the
script exits with an error.

## Available Tools

### `search_topics(query: str) -> list[dict]`

Searches topic titles and key concepts (case-insensitive substring
match) and returns up to 5 matches, each with `id`, `title`, and
`summary`. Read-only (`readOnlyHint`) and deterministic.

- Empty query: error `The search query is empty. Provide a keyword such
  as 'decorators' or 'classes'.`
- No match: error `No topics matched '<query>'. Try a broader keyword
  such as 'functions' or 'classes'.`

### `get_topic_details(topic_id: str) -> dict`

Returns the full record for one topic by exact id (case and surrounding
spaces are ignored): `id`, `title`, `summary`, `prerequisites`,
`key_concepts`, `common_mistakes`, `practice_idea`. Read-only.

- Unknown id: error listing all valid ids.
- Wrong type or missing argument: rejected by FastMCP input validation
  before the function runs.

Typical flow: `search_topics` to find an id, then `get_topic_details`
for the full topic. The practice activity comes from the topic's
`practice_idea` field.

## Available Resources

### `topics://catalog`

Read-only JSON (`application/json`) list of every topic's `id` and
`title`, for browsing what the server offers:

```json
[
  {"id": "python-functions", "title": "Python Functions"},
  {"id": "python-scope-closures", "title": "Scope and Closures"},
  {"id": "python-decorators", "title": "Python Decorators"},
  {"id": "python-list-comprehensions", "title": "List Comprehensions"},
  {"id": "python-classes-objects", "title": "Classes and Objects"},
  {"id": "python-exceptions", "title": "Exception Handling"}
]
```

## Third-Party MCP Server Review

**Server reviewed:** Filesystem MCP server
(`@modelcontextprotocol/server-filesystem`, from the official
`modelcontextprotocol/servers` repository).

**What I reviewed:** the official "Connect to local MCP servers" guide,
the server's README, and the server itself through the MCP Inspector
CLI (`initialize`, `tools/list`, `resources/list`, and two tool calls),
pointed at an empty test folder `~/mcp-sandbox`. I did not connect it
to any agent and did not run its write tools.

1. **What it does:** gives an AI application file operations on the
   local machine: reading, listing, searching, writing, editing, and
   moving files and directories.
2. **Local or remote:** local. It is a Node.js program started by the
   client with `npx` and it communicates over stdio. It does not need a
   network service of its own.
3. **Tools and resources:** 14 tools and no resources. Ten are
   read-only (for example `read_text_file`, `list_directory`,
   `search_files`, `list_allowed_directories`). Four modify the disk:
   `write_file`, `edit_file`, `move_file` (marked destructive), and
   `create_directory`.
4. **Permissions and credentials:** no API keys or accounts. Its
   permissions are the directories passed as arguments on the command
   line. Inside those, it acts with my own user account's permissions.
   In my test, a read of a file outside the allowed folder was refused
   with "Access denied - path outside allowed directories".
5. **Risk:** if it is given a broad directory (such as the home
   folder), a model could read private files (SSH keys, `.env`
   secrets) or overwrite and move files with `write_file`, `edit_file`,
   or `move_file`, either by mistake or because of a prompt injection
   hidden in a file it reads. Also, `npx -y` downloads and runs the
   latest published package without asking, so a compromised or
   changed release would run immediately.
6. **Safety measure:** allow only one dedicated, non-sensitive folder
   (never `~` or a project with secrets), pin the package version in
   the configuration instead of always taking the latest, inspect the
   tools with the MCP Inspector before connecting it to an agent, and
   keep per-action approval turned on in the client so every write is
   confirmed by a person.

## Example Output

**Server test (`python3 client/mcp_client.py 2>/dev/null`, shortened):**

```text
1. Server started and connected: True
2. Tools listed: ['search_topics', 'get_topic_details']
3. search_topics('decorators'):
[
  {
    "id": "python-decorators",
    "title": "Python Decorators",
    "summary": "A way to wrap a function with extra behavior, such as logging or timing, without changing the function's own code."
  }
]
...
6. Invalid inputs:
  search_topics({'query': 'rust'}) -> error: No topics matched 'rust'. Try a broader keyword such as 'functions' or 'classes'.
  get_topic_details({'topic_id': 'does-not-exist'}) -> error: No topic found with id 'does-not-exist'. Valid ids are: python-functions, python-scope-closures, python-decorators, python-list-comprehensions, python-classes-objects, python-exceptions.
```

**Agent (`python3 client/agent.py`):** the full saved response is in
[`output/sample_agent_response.md`](output/sample_agent_response.md).
Excerpt:

```text
PASTE THE FIRST LINES OF YOUR REAL output/sample_agent_response.md HERE
(the "MCP Tool Calls" list and the start of the answer)
```

## Known Limitations

- **Simple search:** `search_topics` is a substring match on titles and
  key concepts only. A multi-word query such as `"decorators in
  python"` returns no match, and summaries and prerequisites are not
  searched. Results are in file order with no ranking (max 5).
- **Small, static dataset:** 6 topics in a JSON file that is reloaded on
  every call (fine for this size, not for a large dataset).
  Prerequisites such as "Lists" are plain text and not always topics in
  the dataset.
- **Small model:** `llama3.2` (3B) sometimes skips a tool or searches
  with a keyword that has no match. The agent refuses to save a
  response if `search_topics` was not called, but it cannot verify that
  the answer contains no invented details. Re-running usually fixes it.
- **Agent needs two terminals:** the agent uses HTTP, so the server must
  be started separately first.
- **No authentication on HTTP:** the HTTP endpoint has no auth and is
  meant for local development only (`127.0.0.1`).
- **Single-turn agent:** no memory or follow-up questions.

**Errors encountered during development:**

- Typing Python (`client = Client(...)`) into bash gave `syntax error
  near unexpected token '('`; Python code must go in a `.py` file.
- With the MCP server stopped, ADK did not raise an error: it gave the
  model an empty tool list and the agent produced a useless answer.
  Fixed by listing the server's tools before running the model, which
  now fails with a clear "could not run the agent" message.
- The MCP Inspector timed out (`Connection timed out after 15000 ms`)
  when the server had to be downloaded with `npx` first; fixed with
  `--connect-timeout 60000`.
- Working from a clone on the Windows drive (`/mnt/c/...`) in WSL
  showed an outdated repository and unreliable file permissions; the
  project was moved to a fresh clone in the WSL home directory.

## Reflection

1. **What problem does MCP solve?** Without MCP, every AI app needs a
   custom integration for every tool or data source. MCP standardizes
   the connection, so a capability is built once as a server and any
   MCP-compatible client (my agent, the Inspector, an IDE) can discover
   and use it without changes.

2. **What is the difference between an MCP tool and an MCP resource?**
   A tool is a function the model calls with arguments to perform a
   lookup or action (`tools/call`). A resource is read-only data at a
   fixed URI that a client reads for context (`resources/read`). My
   `search_topics` takes a query and computes matches; my
   `topics://catalog` just returns the catalog and takes no input.

3. **What does your MCP server expose?** Two read-only tools,
   `search_topics` and `get_topic_details`, and one resource,
   `topics://catalog`, all backed by `data/topics.json`.

4. **How does your agent use the MCP server?** It connects over HTTP
   with ADK's `McpToolset`, filtered to the two tools. The model calls
   `search_topics` to find a topic id, then `get_topic_details` for the
   full record, and writes the answer only from that data. The agent
   never imports the server code.

5. **What should you check before using a third-party MCP server?** Who
   publishes it and whether the source is official or trusted; what
   tools and resources it exposes (with the Inspector, before
   connecting an agent); which tools can write or delete; what
   directories, network access, or credentials it needs; whether it
   runs locally or remotely and what data would be sent to it; and
   whether the version can be pinned.

6. **What limitation did you observe in your implementation?** The
   combination of a strict substring search and a small model is
   fragile: if `llama3.2` passes a phrase like `"Python decorators
   review"` instead of `"decorators"`, the search finds nothing even
   though the topic exists. Keyword-based search (splitting the query
   into words) or a larger model would make the agent more reliable.