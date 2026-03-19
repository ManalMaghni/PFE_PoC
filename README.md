# 🤖 Multi-Agent System for Automated Project Generation

> **Final Year Project (PFE) — Proof of Concept**  
> An AI-powered multi-agent system that automates software project creation using MCP (Model Context Protocol), LangGraph, and Groq LLM.

---

## 📌 Overview

This PoC demonstrates how multiple AI agents can collaborate to automate software development tasks. A user submits a natural language request, and the system autonomously creates project structures, writes files, validates code, generates Dockerfiles, runs tests, and resolves dependencies.

The system is built around three core principles:
- **Separation of concerns** — each agent has one responsibility
- **Self-correction** — the Evaluator agent detects failures and sends feedback to the Worker
- **Decoupled tools** — tools live on a separate MCP server, shared by all agents

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     USER REQUEST                        │
│              (via ENV variable)                         │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   ORCHESTRATOR                          │
│              (LangGraph State Graph)                    │
│                                                         │
│   ┌─────────────────┐         ┌─────────────────────┐  │
│   │  Agent Worker   │ ──────► │  Agent Evaluator    │  │
│   │                 │         │                     │  │
│   │  - ReAct Loop   │ ◄────── │  - Judges output    │  │
│   │  - Calls tools  │feedback │  - complete?        │  │
│   │  - 1 tool/iter  │         │  - incomplete?      │  │
│   └────────┬────────┘         └──────────┬──────────┘  │
│            │                             │              │
└────────────┼─────────────────────────────┼──────────────┘
             │ MCP Protocol                │ STATUS: complete
             ▼                             ▼
┌─────────────────────┐          ┌─────────────────────┐
│   MCP Server        │          │    FINAL OUTPUT     │
│   (7 Tools)         │          │    displayed        │
│                     │          └─────────────────────┘
│  scaffold_project   │
│  write_file_safe    │
│  validate_syntax    │
│  generate_dockerfile│
│  run_tests          │
│  extract_api        │
│  dep_resolver       │
└─────────────────────┘
```

### Flow Description

```
1. User sends request via ENV variable
2. Orchestrator initializes MCP connection + LangGraph graph
3. Agent Worker receives request
4. Worker runs ReAct loop → asks Groq LLM which tool to call
5. Worker calls exactly ONE MCP tool
6. Agent Evaluator receives (request + tool output)
7. Evaluator asks Groq LLM: is the task complete?
   → STATUS: complete  → display final output, STOP
   → STATUS: incomplete → send feedback to Worker, RETRY
8. Max 3 iterations → force stop
```

---

## 📁 Project Structure

```
project_2/
│
├── docker-compose.yml              # Orchestrates 2 containers
├── .env                            # API keys (NOT committed to git)
│
├── mcp-serveur/                    # Container 1: MCP Tool Server
│   ├── Dockerfile
│   ├── requirements.txt            # fastmcp, uvicorn
│   ├── server.py                   # FastMCP entry point (port 8000)
│   └── tools/
│       ├── __init__.py             # Registers all tools
│       ├── scaffold.py             # Tool 1: project structure generator
│       ├── file_writer.py          # Tool 2: safe file writer
│       ├── syntax_validator.py     # Tool 3: code syntax validator
│       ├── dockerfile_gen.py       # Tool 4: Dockerfile generator
│       ├── test_runner.py          # Tool 5: pytest runner
│       ├── api_extractor.py        # Tool 6: FastAPI route extractor
│       └── dep_resolver.py         # Tool 7: dependency resolver
│
├── agents/                         # Container 2: AI Agents
│   ├── Dockerfile
│   ├── requirements.txt            # httpx, langgraph, python-dotenv
│   │
│   ├── shared/                     # Shared code across all agents
│   │   ├── config.py               # Global constants (URLs, model, max iterations)
│   │   ├── state.py                # LangGraph shared State (TypedDict)
│   │   └── core/
│   │       ├── groq_client.py      # Direct HTTP calls to Groq API
│   │       ├── mcp_client.py       # MCP HTTP client (no LangChain)
│   │       └── react_loop.py       # Custom ReAct loop implementation
│   │
│   ├── agent_worker/
│   │   └── agent.py                # Generalist worker agent
│   │
│   ├── agent_evaluator/
│   │   └── agent.py                # Task evaluator agent
│   │
│   └── orchestrator/
│       ├── graph.py                # LangGraph graph definition
│       └── main.py                 # Entry point (reads ENV, runs graph)
│
└── workspace/                      # Shared volume: generated project files
```

---

## 🔧 MCP Tools — Detailed

### Tool 1 — `scaffold_project`
Generates a complete empty project structure with base files.

```
Input  : project_name (str), project_type (str)
Types  : 'fastapi' | 'react' | 'fullstack'
Output : Creates /workspace/{project_name}/ with all folders and base files
Example: scaffold_project("my-api", "fastapi")
         → /workspace/my-api/app/main.py
         → /workspace/my-api/app/routers/__init__.py
         → /workspace/my-api/tests/test_main.py
         → /workspace/my-api/requirements.txt
```

### Tool 2 — `write_file_safe`
Writes a file safely with security checks and diff detection.

```
Input  : filepath (str), content (str)
Security: path must be under /workspace
Detects: new file / modified / unchanged
Output : ✅ Created | ✏️ Modified +3 -1 | ℹ️ No change
```

### Tool 3 — `validate_code_syntax`
Validates code syntax without executing it.

```
Python : ast.parse() → detects SyntaxError with line number
JS/TS  : heuristics (balanced braces, parentheses, brackets)
Output : ✅ Valid syntax (X lines) | ❌ Error at line Y: message
```

### Tool 4 — `generate_dockerfile`
Analyzes project and generates adapted Dockerfile + docker-compose.yml.

```
Detects: requirements.txt → FastAPI | package.json → React | both → Fullstack
Creates: /workspace/{project}/Dockerfile
         /workspace/{project}/docker-compose.yml
```

### Tool 5 — `run_tests_in_sandbox`
Runs pytest in an isolated subprocess with timeout.

```
Input  : test_path (str) — path to test file
Runs   : pytest as subprocess (timeout 30s)
Output : ✅ All tests pass | ❌ Some tests failed | ⚠️ Execution error
```

### Tool 6 — `extract_api_contract`
Analyzes FastAPI file via AST and extracts all HTTP routes.

```
Input    : filepath (str) — FastAPI main.py
Analyzes : @app.get, @router.post... via ast.parse()
Saves    : api_contract.json in same folder
Output   : JSON with method, route, function name, parameters
```

### Tool 7 — `dependency_resolver`
Scans all .py files in a project and generates requirements.txt.

```
Input  : project_path (str)
Scans  : all imports in all .py files recursively
Filters: Python stdlib (os, sys, typing...) → ignored
Saves  : requirements.txt at project root
Output : ✅ 5 dependency(ies) detected: fastapi, sqlalchemy, pydantic...
```

---

## 🧠 Agents — Detailed

### Agent Worker

**Role**: Generalist executor — calls the right tool for the user request.

**How it works**:
1. Receives `user_request` from State (+ `feedback` if retry)
2. Runs custom ReAct loop:
   - Sends messages to Groq LLM with all 7 tools available
   - LLM decides which tool to call and with what arguments
   - Executes exactly ONE tool via MCP client
   - Returns the tool result
3. Updates `worker_output` in State

**System Prompt** (key rules):
- Call ONLY ONE tool per response
- Know the exact limits of each tool
- If request cannot be fulfilled, explain why honestly
- Do NOT invent capabilities that don't exist

**Why it's an agent**: The LLM autonomously decides which tool to call among 7 options, with what parameters, based on natural language context. It's not hardcoded logic.

---

### Agent Evaluator

**Role**: Judge — decides if the task is complete or needs correction.

**How it works**:
1. Receives `user_request` + `worker_output` from State
2. Calls Groq LLM directly (no tools) with evaluation prompt
3. LLM returns structured judgment:
   - `STATUS: complete` → sets `final_output`, graph stops
   - `STATUS: incomplete\nFEEDBACK: ...` → sets `feedback`, Worker retries

**Why it's an agent**: It uses LLM reasoning to judge quality — not simple string matching or rule-based checks. It understands context.

---

### Orchestrator

**Role**: Coordinator — manages the flow between agents using LangGraph.

**Graph definition**:
```python
worker → evaluator              # always
evaluator → worker              # if incomplete AND iterations < 3
evaluator → END                 # if complete OR max iterations reached
```

**Shared State**:
```python
class State(TypedDict):
    user_request  : str   # original user request
    worker_output : str   # last tool result
    feedback      : str   # evaluator feedback if incomplete
    iterations    : int   # loop counter (max 3)
    final_output  : str   # validated final result
```

**Why it's an agent**: It perceives global state and makes routing decisions. It's a coordinator agent in the multi-agent architecture sense.

---

## ⚙️ Technical Choices

| Choice | Alternative | Reason |
|--------|-------------|--------|
| Direct HTTP to Groq | LangChain | Full control, no abstraction overhead |
| Custom ReAct loop | LangChain agents | Understand exactly what happens |
| MCP Protocol | Direct function calls | Tools decoupled from agents, shareable |
| LangGraph | Custom state machine | Production-grade graph with built-in retry |
| ENV variable for input | stdin | Docker stdin issues with compose |
| 1 tool per iteration | Multiple tools | Prevents uncontrolled chaining, easier to debug |
| Volume hot reload | Rebuild on change | Faster development cycle |

---

## 🚀 Setup & Usage

### Prerequisites
- Docker Desktop installed and running
- Groq API key → https://console.groq.com

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/pfe-multi-agent-poc.git
cd pfe-multi-agent-poc
```

**2. Create `.env` file**
```bash
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama3-groq-70b-8192-tool-use-preview
```

**3. Build containers**
```bash
docker-compose build
```

**4. Start MCP server (background)**
```bash
docker-compose up mcp-serveur -d
```

**5. Run a request**
```bash
docker-compose run --rm -e USER_REQUEST="Create a fastapi project called my-api" agents
```

### Usage Examples

```bash
# Create a FastAPI project
docker-compose run --rm -e USER_REQUEST="Create a fastapi project called my-api" agents

# Create a React project
docker-compose run --rm -e USER_REQUEST="Create a react project called my-frontend" agents

# Create a fullstack project
docker-compose run --rm -e USER_REQUEST="Create a fullstack project called my-app" agents

# Resolve dependencies
docker-compose run --rm -e USER_REQUEST="Resolve dependencies for /workspace/my-api" agents

# Generate Dockerfile
docker-compose run --rm -e USER_REQUEST="Generate dockerfile for /workspace/my-api" agents
```

### Expected Output

```
✅ 7 tools available

✅ Request: 'Create a fastapi project called my-api'

🔧 Agent Worker — iteration 1
  🔄 ReAct step 1
  🔧 Tool: scaffold_project({'project_name': 'my-api', 'project_type': 'fastapi'})
  📤 Result: ✅ Project 'my-api' (fastapi) created in /workspace/my-api
             📁 Folders: 4
             📄 Files: app/__init__.py, app/main.py, ...

⚖️  Agent Evaluator — evaluating...
⚖️  Evaluation: STATUS: complete

==================================================
🎯 FINAL RESULT:
==================================================
✅ Project 'my-api' (fastapi) created in /workspace/my-api
📁 Folders: 4
📄 Files: app/__init__.py, app/main.py, app/routers/__init__.py...
```

---

## 🔄 Self-Correction Example

When the Worker makes a mistake, the Evaluator catches it and triggers a retry:

```
Request: "Create a kafka project called my-project"

🔧 Worker iteration 1
  → scaffold_project(type='fastapi')   # wrong type chosen
  → Result: FastAPI skeleton created

⚖️  Evaluator
  → STATUS: incomplete
  → FEEDBACK: Task was to create Kafka project but FastAPI skeleton was created.
              No Kafka-specific setup found.

🔧 Worker iteration 2  (receives feedback)
  → write_file_safe(kafka main.py with producer/consumer)
  → Result: Kafka file created

⚖️  Evaluator
  → STATUS: incomplete
  → FEEDBACK: Only one file created, missing requirements.txt, docker-compose...

🔧 Worker iteration 3
  → write_file_safe(requirements.txt with kafka-python)

⚖️  Evaluator
  → STATUS: incomplete (still missing full structure)

⚠️  Max iterations reached → display last result
```

---

## 🐳 Docker Configuration

```yaml
services:
  mcp-serveur:
    build: ./mcp-serveur
    container_name: mcp-serveur
    ports:
      - "8000:8000"          # Expose MCP tools via HTTP
    volumes:
      - ./mcp-serveur:/app   # Hot reload
      - ./workspace:/workspace  # Shared generated files

  agents:
    build: ./agents
    volumes:
      - ./agents:/app        # Hot reload
      - ./workspace:/workspace  # Access generated files
    depends_on:
      - mcp-serveur
    env_file:
      - .env
```

---

## 📊 MCP Protocol Communication

```
agents container                    mcp-serveur container
      │                                      │
      │  POST /mcp                           │
      │  {"method": "initialize"}  ────────► │
      │  ◄──────────── session-id ────────── │
      │                                      │
      │  POST /mcp                           │
      │  {"method": "tools/list"}  ─────────►│
      │  ◄────────── 7 tools JSON ────────── │
      │                                      │
      │  POST /mcp                           │
      │  {"method": "tools/call",            │
      │   "name": "scaffold_project",        │
      │   "arguments": {...}}      ─────────►│
      │  ◄────────── tool result ─────────── │
```

---

