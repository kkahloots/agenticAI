# 🧱 Orchestrator Design

### Routing Logic

The orchestrator node in LangGraph evaluates the user's objective and dispatches it to the appropriate agent. The logic is expressed by the formula rule in `proposal.md`. It uses pattern matching on the goal's intent and required outputs.

- **Intent Detection**: Parse the user's request using an LLM (via the universal LLM factory in `src/llm.py`) to determine whether it is informational, analytical, action‑oriented or strategic.
- **Stateful Decision**: Maintain a short‑term memory of recent tasks. If a sequence of subtasks is underway, route subsequent steps to the same agent until completion.
- **Fallback Handler**: If no rule matches or the user's intent is ambiguous, the orchestrator calls a clarification subroutine that asks the user for more information.

### Formula Implementation

```python
if is_informational(goal):
    delegate('level1')
elif is_analytical(goal):
    delegate('level2')
elif requires_action(goal):
    delegate('level3')
elif is_strategic(goal):
    delegate('level4')
else:
    ask_user("Could you clarify your objective?")
```

### LLM Provider Selection

The orchestrator (and all agents) obtain their LLM through a single universal factory at `src/llm.py`. The active provider is controlled by the `LLM_PROVIDER` environment variable — no code changes are needed to switch providers.

| `LLM_PROVIDER` | Backend | Key env vars |
|----------------|---------|-------------|
| `openai` (default) | OpenAI API | `OPENAI_API_KEY`, `OPENAI_MODEL` |
| `ollama` | Local Ollama server | `OLLAMA_BASE_URL`, `OLLAMA_MODEL` |
| `gptec` | GPTec / any OpenAI-compatible endpoint | `GPTEC_API_URL`, `GPTEC_API_KEY`, `GPTEC_MODEL` |

**Rule**: `IF LLM_PROVIDER = "ollama" THEN use local model ELSE IF LLM_PROVIDER = "gptec" THEN use custom endpoint ELSE use OpenAI`

All providers return a LangChain `BaseChatModel` — the orchestrator and agents call `llm.invoke([SystemMessage, HumanMessage])` identically regardless of provider. If the LLM call fails for any reason, the orchestrator falls back to deterministic rule-based classification.

### Memory & Feedback

The orchestrator stores past interactions via `ChatMessageHistory` to avoid repeated questions. It evaluates agent responses and, if results are unsatisfactory, it can re‑route tasks or adjust parameters. Feedback loops ensure continuous improvement, aligning with the *Perceive → Reason → Act → Learn* cycle described in the overview.
