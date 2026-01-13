import json
import time
from dataclasses import dataclass
from agent_ops.config import get_settings


@dataclass
class RunResult:
    ok: bool
    result: dict
    error: str | None = None


def run_task(spec: dict) -> RunResult:
    """
    Executes a run spec. In production you flip RUNNER_MODE=openhands to execute via OpenHands SDK.
    Tests use mock mode.
    """
    settings = get_settings()
    mode = (settings.runner_mode or "mock").lower()

    if mode == "mock":
        # Deterministic: pretend we planned, coded, tested, produced an artifact.
        time.sleep(0.2)
        return RunResult(
            ok=True,
            result={
                "mode": "mock",
                "summary": "Mock run completed.",
                "inputs": spec,
                "artifacts": [{"type": "text", "name": "PLAN.md", "content": "Mock plan"}],
            },
        )

    if mode == "openhands":
        # Real agent execution via OpenHands SDK (requires LLM_API_KEY and a model).
        # OpenHands SDK is designed to run agents over a workspace with tools.
        from openhands.sdk import LLM, Agent, Conversation, Tool
        from openhands.tools.terminal import TerminalTool
        from openhands.tools.file_editor import FileEditorTool
        from openhands.tools.task_tracker import TaskTrackerTool

        if not settings.llm_api_key:
            return RunResult(ok=False, result={}, error="LLM_API_KEY is required for openhands mode.")
        if not settings.llm_model:
            return RunResult(ok=False, result={}, error="LLM_MODEL is required for openhands mode.")

        llm = LLM(
            model=settings.llm_model,
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
        )

        agent = Agent(
            llm=llm,
            tools=[
                Tool(name=TerminalTool.name),
                Tool(name=FileEditorTool.name),
                Tool(name=TaskTrackerTool.name),
            ],
        )

        workspace = spec.get("workspace", "/tmp")
        prompt = spec.get("prompt", "Explain what you can do in this repository.")

        conv = Conversation(agent=agent, workspace=workspace)
        conv.send_message(prompt)
        conv.run()

        return RunResult(ok=True, result={"mode": "openhands", "workspace": workspace, "prompt": prompt})

    return RunResult(ok=False, result={}, error=f"Unknown RUNNER_MODE: {mode}")
