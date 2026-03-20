#!/usr/bin/env python3
"""
Claude Code -> Langfuse hook

Supports:
- Main session turns (Stop hook)
- Subagent progress tracking (agent_progress events)
"""

import json
import os
import sys
import time
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# --- Langfuse import (fail-open) ---
try:
    from langfuse import Langfuse, propagate_attributes
except Exception:
    sys.exit(0)

# --- Paths ---
STATE_DIR = Path.home() / ".claude" / "state"
LOG_FILE = STATE_DIR / "langfuse_hook.log"
STATE_FILE = STATE_DIR / "langfuse_state.json"
LOCK_FILE = STATE_DIR / "langfuse_state.lock"

DEBUG = os.environ.get("CC_LANGFUSE_DEBUG", "").lower() == "true"
MAX_CHARS = int(os.environ.get("CC_LANGFUSE_MAX_CHARS", "20000"))

# ----------------- Logging -----------------
def _log(level: str, message: str) -> None:
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{ts} [{level}] {message}\n")
    except Exception:
        pass

def debug(msg: str) -> None:
    if DEBUG:
        _log("DEBUG", msg)

def info(msg: str) -> None:
    _log("INFO", msg)

def warn(msg: str) -> None:
    _log("WARN", msg)

def error(msg: str) -> None:
    _log("ERROR", msg)

# ----------------- State locking (best-effort) -----------------
class FileLock:
    def __init__(self, path: Path, timeout_s: float = 2.0):
        self.path = path
        self.timeout_s = timeout_s
        self._fh = None

    def __enter__(self):
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        self._fh = open(self.path, "a+", encoding="utf-8")
        try:
            import fcntl
            deadline = time.time() + self.timeout_s
            while True:
                try:
                    fcntl.flock(self._fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    if time.time() > deadline:
                        break
                    time.sleep(0.05)
        except Exception:
            pass
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            import fcntl
            fcntl.flock(self._fh.fileno(), fcntl.LOCK_UN)
        except Exception:
            pass
        try:
            self._fh.close()
        except Exception:
            pass

def load_state() -> Dict[str, Any]:
    try:
        if not STATE_FILE.exists():
            return {}
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}

def save_state(state: Dict[str, Any]) -> None:
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        tmp = STATE_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
        os.replace(tmp, STATE_FILE)
    except Exception as e:
        debug(f"save_state failed: {e}")

def state_key(session_id: str, transcript_path: str) -> str:
    raw = f"{session_id}::{transcript_path}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

# ----------------- Hook payload -----------------
def read_hook_payload() -> Dict[str, Any]:
    try:
        data = sys.stdin.read()
        if not data.strip():
            return {}
        return json.loads(data)
    except Exception:
        return {}

def extract_session_and_transcript(payload: Dict[str, Any]) -> Tuple[Optional[str], Optional[Path]]:
    session_id = (
        payload.get("sessionId")
        or payload.get("session_id")
        or payload.get("session", {}).get("id")
    )

    transcript = (
        payload.get("transcriptPath")
        or payload.get("transcript_path")
        or payload.get("transcript", {}).get("path")
    )

    if transcript:
        try:
            transcript_path = Path(transcript).expanduser().resolve()
        except Exception:
            transcript_path = None
    else:
        transcript_path = None

    return session_id, transcript_path

# ----------------- Transcript parsing helpers -----------------
def get_content(msg: Dict[str, Any]) -> Any:
    if not isinstance(msg, dict):
        return None
    if "message" in msg and isinstance(msg.get("message"), dict):
        return msg["message"].get("content")
    return msg.get("content")

def get_role(msg: Dict[str, Any]) -> Optional[str]:
    t = msg.get("type")
    if t in ("user", "assistant"):
        return t
    m = msg.get("message")
    if isinstance(m, dict):
        r = m.get("role")
        if r in ("user", "assistant"):
            return r
    return None

def is_tool_result(msg: Dict[str, Any]) -> bool:
    role = get_role(msg)
    if role != "user":
        return False
    content = get_content(msg)
    if isinstance(content, list):
        return any(isinstance(x, dict) and x.get("type") == "tool_result" for x in content)
    return False

def iter_tool_results(content: Any) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    if isinstance(content, list):
        for x in content:
            if isinstance(x, dict) and x.get("type") == "tool_result":
                out.append(x)
    return out

def iter_tool_uses(content: Any) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    if isinstance(content, list):
        for x in content:
            if isinstance(x, dict) and x.get("type") == "tool_use":
                out.append(x)
    return out

def extract_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: List[str] = []
        for x in content:
            if isinstance(x, dict) and x.get("type") == "text":
                parts.append(x.get("text", ""))
            elif isinstance(x, str):
                parts.append(x)
        return "\n".join([p for p in parts if p])
    return ""

def truncate_text(s: str, max_chars: int = MAX_CHARS) -> Tuple[str, Dict[str, Any]]:
    if s is None:
        return "", {"truncated": False, "orig_len": 0}
    orig_len = len(s)
    if orig_len <= max_chars:
        return s, {"truncated": False, "orig_len": orig_len}
    head = s[:max_chars]
    return head, {"truncated": True, "orig_len": orig_len, "kept_len": len(head), "sha256": hashlib.sha256(s.encode("utf-8")).hexdigest()}

def get_model(msg: Dict[str, Any]) -> str:
    m = msg.get("message")
    if isinstance(m, dict):
        return m.get("model") or "claude"
    return "claude"

def get_message_id(msg: Dict[str, Any]) -> Optional[str]:
    m = msg.get("message")
    if isinstance(m, dict):
        mid = m.get("id")
        if isinstance(mid, str) and mid:
            return mid
    return None

# ----------------- Incremental reader -----------------
@dataclass
class SessionState:
    offset: int = 0
    buffer: str = ""
    turn_count: int = 0

def load_session_state(global_state: Dict[str, Any], key: str) -> SessionState:
    s = global_state.get(key, {})
    return SessionState(
        offset=int(s.get("offset", 0)),
        buffer=str(s.get("buffer", "")),
        turn_count=int(s.get("turn_count", 0)),
    )

def write_session_state(global_state: Dict[str, Any], key: str, ss: SessionState) -> None:
    global_state[key] = {
        "offset": ss.offset,
        "buffer": ss.buffer,
        "turn_count": ss.turn_count,
        "updated": datetime.now(timezone.utc).isoformat(),
    }

def read_new_jsonl(transcript_path: Path, ss: SessionState) -> Tuple[List[Dict[str, Any]], SessionState]:
    if not transcript_path.exists():
        return [], ss

    try:
        with open(transcript_path, "rb") as f:
            f.seek(ss.offset)
            chunk = f.read()
            new_offset = f.tell()
    except Exception as e:
        debug(f"read_new_jsonl failed: {e}")
        return [], ss

    if not chunk:
        return [], ss

    try:
        text = chunk.decode("utf-8", errors="replace")
    except Exception:
        text = chunk.decode(errors="replace")

    combined = ss.buffer + text
    lines = combined.split("\n")
    ss.buffer = lines[-1]
    ss.offset = new_offset

    msgs: List[Dict[str, Any]] = []
    for line in lines[:-1]:
        line = line.strip()
        if not line:
            continue
        try:
            msgs.append(json.loads(line))
        except Exception:
            continue

    return msgs, ss

# ----------------- Turn assembly -----------------
@dataclass
class Turn:
    user_msg: Dict[str, Any]
    assistant_msgs: List[Dict[str, Any]]
    tool_results_by_id: Dict[str, Any]

# ----------------- Subagent tracking -----------------
@dataclass
class SubagentSession:
    """Track a subagent's progress messages"""
    agent_id: str
    parent_tool_use_id: str
    description: str = ""
    prompt: str = ""
    result_text: str = ""
    messages: List[Dict[str, Any]] = field(default_factory=list)
    tool_uses: List[Dict[str, Any]] = field(default_factory=list)
    tool_results: Dict[str, Any] = field(default_factory=dict)
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    total_tokens: int = 0
    total_tool_count: int = 0
    status: str = "running"

def is_agent_progress(msg: Dict[str, Any]) -> bool:
    """Check if message is an agent progress event"""
    return (
        msg.get("type") == "progress" and
        msg.get("data", {}).get("type") == "agent_progress"
    )

def extract_agent_progress_data(msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Extract agent progress data from a progress message"""
    # Check if this is an agent_progress message
    data = msg.get("data", {})
    if msg.get("type") != "progress" or data.get("type") != "agent_progress":
        return None

    # The actual message content is nested: data.message.message
    # parentToolUseID and toolUseID are at the TOP LEVEL of msg, not in data
    outer_msg = data.get("message", {})
    inner_msg = outer_msg.get("message", {})

    return {
        "agent_id": data.get("agentId", ""),
        "parent_tool_use_id": msg.get("parentToolUseID", ""),  # Top level!
        "tool_use_id": msg.get("toolUseID", ""),  # Top level!
        "prompt": data.get("prompt", ""),
        "message_type": outer_msg.get("type", ""),  # "user" or "assistant"
        "message": inner_msg,
        "timestamp": msg.get("timestamp", ""),
    }

def build_subagents(messages: List[Dict[str, Any]]) -> Dict[str, SubagentSession]:
    """Build subagent sessions from progress messages and agent results"""
    subagents: Dict[str, SubagentSession] = {}

    for msg in messages:
        # First check if this is an agent result (tool_result with toolUseResult containing agentId)
        if msg.get("type") == "user":
            content = msg.get("message", {}).get("content", [])
            tool_use_result = msg.get("toolUseResult", {})

            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "tool_result":
                        # Check for agent result
                        if "agentId" in tool_use_result:
                            agent_id = tool_use_result.get("agentId", "")
                            # Find matching subagent by looking for the parent tool use
                            for key, sa in subagents.items():
                                if sa.agent_id == agent_id:
                                    sa.status = tool_use_result.get("status", "completed")
                                    sa.total_tokens = tool_use_result.get("totalTokens", 0)
                                    sa.total_tool_count = tool_use_result.get("totalToolUseCount", 0)
                                    # Extract result text from content
                                    result_content = item.get("content", "")
                                    if isinstance(result_content, list):
                                        for rc in result_content:
                                            if isinstance(rc, dict) and rc.get("type") == "text":
                                                sa.result_text = rc.get("text", "")[:MAX_CHARS]
                                                break
                                    elif isinstance(result_content, str):
                                        sa.result_text = result_content[:MAX_CHARS]
                                    break

        # Then handle progress messages
        progress_data = extract_agent_progress_data(msg)
        if not progress_data:
            continue

        agent_id = progress_data["agent_id"]
        parent_tool_id = progress_data["parent_tool_use_id"]

        # Create or get subagent session
        key = f"{agent_id}::{parent_tool_id}"
        if key not in subagents:
            subagents[key] = SubagentSession(
                agent_id=agent_id,
                parent_tool_use_id=parent_tool_id,
                prompt=progress_data.get("prompt", ""),
                start_time=progress_data.get("timestamp", ""),
            )

        sa = subagents[key]
        sa.messages.append(msg)

        # Extract tool use/result from the inner message
        inner_msg = progress_data.get("message", {})
        msg_type = progress_data.get("message_type", "")

        if isinstance(inner_msg, dict):
            inner_content = inner_msg.get("content", [])
            if isinstance(inner_content, list):
                for item in inner_content:
                    if isinstance(item, dict):
                        if item.get("type") == "tool_use":
                            sa.tool_uses.append(item)
                        elif item.get("type") == "tool_result":
                            tid = item.get("tool_use_id", "")
                            if tid:
                                content = item.get("content", "")
                                if isinstance(content, str) and len(content) > MAX_CHARS:
                                    content = content[:MAX_CHARS] + "...[truncated]"
                                sa.tool_results[tid] = content

        if not sa.end_time:
            sa.end_time = progress_data.get("timestamp", "")

    return subagents

def build_turns(messages: List[Dict[str, Any]]) -> List[Turn]:
    turns: List[Turn] = []
    current_user: Optional[Dict[str, Any]] = None

    assistant_order: List[str] = []
    assistant_latest: Dict[str, Dict[str, Any]] = {}

    tool_results_by_id: Dict[str, Any] = {}

    def flush_turn():
        nonlocal current_user, assistant_order, assistant_latest, tool_results_by_id, turns
        if current_user is None:
            return
        if not assistant_latest:
            return
        assistants = [assistant_latest[mid] for mid in assistant_order if mid in assistant_latest]
        turns.append(Turn(user_msg=current_user, assistant_msgs=assistants, tool_results_by_id=dict(tool_results_by_id)))

    for msg in messages:
        role = get_role(msg)

        if is_tool_result(msg):
            for tr in iter_tool_results(get_content(msg)):
                tid = tr.get("tool_use_id")
                if tid:
                    tool_results_by_id[str(tid)] = tr.get("content")
            continue

        if role == "user":
            flush_turn()
            current_user = msg
            assistant_order = []
            assistant_latest = {}
            tool_results_by_id = {}
            continue

        if role == "assistant":
            if current_user is None:
                continue

            mid = get_message_id(msg) or f"noid:{len(assistant_order)}"
            if mid not in assistant_latest:
                assistant_order.append(mid)
            assistant_latest[mid] = msg
            continue

    flush_turn()
    return turns

# ----------------- Langfuse emit -----------------
def _tool_calls_from_assistants(assistant_msgs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    calls: List[Dict[str, Any]] = []
    for am in assistant_msgs:
        for tu in iter_tool_uses(get_content(am)):
            tid = tu.get("id") or ""
            calls.append({
                "id": str(tid),
                "name": tu.get("name") or "unknown",
                "input": tu.get("input") if isinstance(tu.get("input"), (dict, list, str, int, float, bool)) else {},
            })
    return calls

def emit_turn(langfuse: Langfuse, session_id: str, turn_num: int, turn: Turn, transcript_path: Path) -> None:
    user_text_raw = extract_text(get_content(turn.user_msg))
    user_text, user_text_meta = truncate_text(user_text_raw)

    last_assistant = turn.assistant_msgs[-1]
    assistant_text_raw = extract_text(get_content(last_assistant))
    assistant_text, assistant_text_meta = truncate_text(assistant_text_raw)

    model = get_model(turn.assistant_msgs[0])

    tool_calls = _tool_calls_from_assistants(turn.assistant_msgs)

    for c in tool_calls:
        if c["id"] and c["id"] in turn.tool_results_by_id:
            out_raw = turn.tool_results_by_id[c["id"]]
            out_str = out_raw if isinstance(out_raw, str) else json.dumps(out_raw, ensure_ascii=False)
            out_trunc, out_meta = truncate_text(out_str)
            c["output"] = out_trunc
            c["output_meta"] = out_meta
        else:
            c["output"] = None

    with propagate_attributes(
        session_id=session_id,
        trace_name=f"Claude Code - Turn {turn_num}",
        tags=["claude-code"],
    ):
        with langfuse.start_as_current_observation(
            name=f"Claude Code - Turn {turn_num}",
            input={"role": "user", "content": user_text},
            metadata={
                "source": "claude-code",
                "session_id": session_id,
                "turn_number": turn_num,
                "transcript_path": str(transcript_path),
                "user_text": user_text_meta,
            },
        ) as trace_span:
            with langfuse.start_as_current_observation(
                name="Claude Response",
                as_type="generation",
                model=model,
                input={"role": "user", "content": user_text},
                output={"role": "assistant", "content": assistant_text},
                metadata={
                    "assistant_text": assistant_text_meta,
                    "tool_count": len(tool_calls),
                },
            ):
                pass

            for tc in tool_calls:
                in_obj = tc["input"]
                if isinstance(in_obj, str):
                    in_obj, in_meta = truncate_text(in_obj)
                else:
                    in_meta = None

                with langfuse.start_as_current_observation(
                    name=f"Tool: {tc['name']}",
                    as_type="tool",
                    input=in_obj,
                    metadata={
                        "tool_name": tc["name"],
                        "tool_id": tc["id"],
                        "input_meta": in_meta,
                        "output_meta": tc.get("output_meta"),
                    },
                ) as tool_obs:
                    tool_obs.update(output=tc.get("output"))

            trace_span.update(output={"role": "assistant", "content": assistant_text})

# ----------------- Subagent emit -----------------
def emit_subagent(langfuse: Langfuse, session_id: str, subagent: SubagentSession, transcript_path: Path) -> None:
    """Emit a subagent session as a span with tool calls and generation"""

    debug(f"emit_subagent: agent_id={subagent.agent_id[:8]}, tool_uses={len(subagent.tool_uses)}, tool_results={len(subagent.tool_results)}")

    # Extract final content/result from last message
    result_text = ""
    if subagent.messages:
        # Look for text content in the messages
        for msg in reversed(subagent.messages):
            msg_data = msg.get("data", {}).get("message", {})
            inner_msg = msg_data.get("message", {})
            if isinstance(inner_msg, dict):
                content = inner_msg.get("content", "")
                if isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "text":
                            result_text = item.get("text", "")[:MAX_CHARS]
                            break
                elif isinstance(content, str):
                    result_text = content[:MAX_CHARS]
                if result_text:
                    break

    # Build tool calls list
    tool_calls = []
    for tu in subagent.tool_uses:
        tool_name = tu.get("name", "unknown")
        tool_input = tu.get("input", {})
        tool_id = tu.get("id", "")

        call = {
            "id": tool_id,
            "name": tool_name,
            "input": tool_input if isinstance(tool_input, (dict, list, str)) else {},
        }
        if tool_id and tool_id in subagent.tool_results:
            out_raw = subagent.tool_results[tool_id]
            out_str = out_raw if isinstance(out_raw, str) else json.dumps(out_raw, ensure_ascii=False)
            if len(out_str) > MAX_CHARS:
                out_str = out_str[:MAX_CHARS] + "...[truncated]"
            call["output"] = out_str
        tool_calls.append(call)

    # Extract description from prompt if available
    prompt_text = subagent.prompt[:200] if subagent.prompt else ""
    description = prompt_text.split('\n')[0][:50] if prompt_text else f"Subagent {subagent.agent_id[:8]}"

    with propagate_attributes(
        session_id=session_id,
        trace_name=f"Subagent: {description}",
        tags=["claude-code", "subagent"],
    ):
        with langfuse.start_as_current_observation(
            name=f"Subagent: {description}",
            as_type="span",
            input={"prompt": subagent.prompt[:MAX_CHARS] if subagent.prompt else ""},
            metadata={
                "source": "claude-code-subagent",
                "session_id": session_id,
                "agent_id": subagent.agent_id,
                "parent_tool_use_id": subagent.parent_tool_use_id,
                "status": subagent.status,
                "total_tokens": subagent.total_tokens,
                "total_tool_count": subagent.total_tool_count,
                "tool_calls_count": len(tool_calls),
                "transcript_path": str(transcript_path),
            },
        ) as span:

            # Emit a generation for the model call (input prompt -> output result)
            # Use actual token usage from agent result
            model_name = "claude-sonnet"  # Default subagent model
            result_text_to_use = subagent.result_text if subagent.result_text else result_text

            # Calculate usage - use actual if available
            if subagent.total_tokens > 0:
                # Estimate input/output split based on typical ratios
                input_tokens = int(subagent.total_tokens * 0.9)  # Most tokens are input context
                output_tokens = int(subagent.total_tokens * 0.1)
            else:
                input_tokens = 0
                output_tokens = 0

            with langfuse.start_as_current_observation(
                name="Model Generation",
                as_type="generation",
                model=model_name,
                input={"role": "user", "content": subagent.prompt[:MAX_CHARS] if subagent.prompt else ""},
                output={"role": "assistant", "content": result_text_to_use[:MAX_CHARS] if result_text_to_use else "Task completed"},
                metadata={
                    "tool_count": len(tool_calls),
                    "total_tokens": subagent.total_tokens,
                    "total_tool_count": subagent.total_tool_count,
                    "status": subagent.status,
                    "estimated_input_tokens": input_tokens,
                    "estimated_output_tokens": output_tokens,
                },
            ) as gen:
                # Update with usage info after creation
                gen.update(usage={
                    "input": input_tokens,
                    "output": output_tokens,
                    "total": subagent.total_tokens if subagent.total_tokens else 0,
                })

            # Emit each tool call as a child observation
            for tc in tool_calls:
                in_obj = tc.get("input", {})
                if isinstance(in_obj, str):
                    in_obj, in_meta = truncate_text(in_obj)
                else:
                    in_meta = None

                with langfuse.start_as_current_observation(
                    name=f"Tool: {tc['name']}",
                    as_type="tool",
                    input=in_obj,
                    metadata={
                        "tool_name": tc["name"],
                        "tool_id": tc["id"],
                        "input_meta": in_meta,
                    },
                ) as tool_obs:
                    tool_obs.update(output=tc.get("output"))

            span.update(output={"result": result_text[:MAX_CHARS] if result_text else "completed", "tool_count": len(tool_calls)})

# ----------------- Main -----------------
def main() -> int:
    start = time.time()
    debug("Hook started")

    if os.environ.get("TRACE_TO_LANGFUSE", "").lower() != "true":
        return 0

    public_key = os.environ.get("CC_LANGFUSE_PUBLIC_KEY") or os.environ.get("LANGFUSE_PUBLIC_KEY")
    secret_key = os.environ.get("CC_LANGFUSE_SECRET_KEY") or os.environ.get("LANGFUSE_SECRET_KEY")
    host = os.environ.get("CC_LANGFUSE_BASE_URL") or os.environ.get("LANGFUSE_BASE_URL") or "https://cloud.langfuse.com"

    if not public_key or not secret_key:
        return 0

    payload = read_hook_payload()
    session_id, transcript_path = extract_session_and_transcript(payload)

    if not session_id or not transcript_path:
        debug("Missing session_id or transcript_path from hook payload; exiting.")
        return 0

    if not transcript_path.exists():
        debug(f"Transcript path does not exist: {transcript_path}")
        return 0

    try:
        langfuse = Langfuse(public_key=public_key, secret_key=secret_key, host=host)
    except Exception:
        return 0

    try:
        with FileLock(LOCK_FILE):
            state = load_state()
            key = state_key(session_id, str(transcript_path))
            ss = load_session_state(state, key)

            msgs, ss = read_new_jsonl(transcript_path, ss)
            if not msgs:
                write_session_state(state, key, ss)
                save_state(state)
                return 0

            turns = build_turns(msgs)
            if not turns:
                write_session_state(state, key, ss)
                save_state(state)
                return 0

            # emit turns
            emitted = 0
            for t in turns:
                emitted += 1
                turn_num = ss.turn_count + emitted
                try:
                    emit_turn(langfuse, session_id, turn_num, t, transcript_path)
                except Exception as e:
                    debug(f"emit_turn failed: {e}")

            ss.turn_count += emitted

            # emit subagents from progress messages
            subagents = build_subagents(msgs)
            subagent_count = 0
            for sa_key, sa in subagents.items():
                subagent_count += 1
                try:
                    emit_subagent(langfuse, session_id, sa, transcript_path)
                except Exception as e:
                    debug(f"emit_subagent failed: {e}")

            write_session_state(state, key, ss)
            save_state(state)

        try:
            langfuse.flush()
        except Exception:
            pass

        dur = time.time() - start
        info(f"Processed {emitted} turns, {subagent_count} subagents in {dur:.2f}s (session={session_id})")
        return 0

    except Exception as e:
        debug(f"Unexpected failure: {e}")
        return 0

    finally:
        try:
            langfuse.shutdown()
        except Exception:
            pass

if __name__ == "__main__":
    sys.exit(main())
