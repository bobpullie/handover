"""
handover/scripts/stop_hook.py
Claude Code Stop 이벤트 시 CURRENT_STATE.md.draft를 생성한다.

직접 실행:
    python stop_hook.py                     # config 자동 탐색
    python stop_hook.py --cwd /path/to/project

runner에서 호출:
    from stop_hook import main; main(cwd='/path/to/project')
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path


def find_config(start: Path) -> dict | None:
    """scripts/ → skill root → .claude/handover_config.json 순서로 탐색."""
    # 1) Skill root 기준 (scripts/../../..) — runner가 explicit cwd 없이 호출 시
    #    패턴: <skill_dir>/scripts/stop_hook.py
    skill_dir = Path(__file__).parent.parent
    # Assume project is 3 levels up from skill dir when installed in ~/.claude/skills/handover
    # but that heuristic is fragile — just read from runner-injected cwd.
    # Fallback: look for handover_config.json walking up from CWD.
    search = Path.cwd()
    for _ in range(8):
        candidate = search / ".claude" / "handover_config.json"
        if candidate.exists():
            try:
                return json.loads(candidate.read_text(encoding="utf-8"))
            except Exception:
                return None
        parent = search.parent
        if parent == search:
            break
        search = parent
    return None


def run_git(cwd_str: str, args: list[str]) -> str:
    """Run a git command, return stdout or fallback message."""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "-C", cwd_str] + args,
            capture_output=True, text=True, timeout=10, encoding="utf-8", errors="replace"
        )
        return result.stdout.strip() if result.returncode == 0 else "git unavailable"
    except Exception as e:
        return f"git unavailable ({e})"


def count_session_number(handover_doc: Path) -> int:
    """세션 번호 = 기존 세션 문서 수 + 1."""
    try:
        existing = [
            f for f in os.listdir(handover_doc)
            if f.endswith(".md") and not f.startswith("CURRENT")
        ]
        return len(existing) + 1
    except Exception:
        return 1


def main(cwd: str | None = None) -> int:
    # ----------------------------------------------------------------
    # Resolve CWD
    # ----------------------------------------------------------------
    if cwd is not None:
        project_cwd = Path(cwd).resolve()
        config_path = project_cwd / ".claude" / "handover_config.json"
        if config_path.exists():
            try:
                config = json.loads(config_path.read_text(encoding="utf-8"))
            except Exception:
                config = {"agent_id": "unknown", "cwd": str(project_cwd), "adapter": None}
        else:
            config = {"agent_id": "unknown", "cwd": str(project_cwd), "adapter": None}
    else:
        config = find_config(Path.cwd())
        if config is None:
            # No config found — exit quietly
            return 0
        project_cwd = Path(config.get("cwd", ".")).resolve()

    cwd_str = str(project_cwd).replace("\\", "/")
    agent_id = config.get("agent_id", "unknown")

    # ----------------------------------------------------------------
    # Rate limit: 300s cooldown
    # ----------------------------------------------------------------
    marker = project_cwd / ".handover_last_run"
    now = time.time()
    if marker.exists():
        try:
            last = float(marker.read_text(encoding="utf-8").strip())
            if now - last < 300:
                # Too soon — exit quietly
                return 0
        except Exception:
            pass

    # ----------------------------------------------------------------
    # Verify handover_doc/ exists
    # ----------------------------------------------------------------
    handover_doc = project_cwd / "handover_doc"
    if not handover_doc.exists():
        # Not initialized — exit quietly
        return 0

    # ----------------------------------------------------------------
    # Gather git context
    # ----------------------------------------------------------------
    git_log = run_git(cwd_str, ["log", "--oneline", "-10"])
    git_status = run_git(cwd_str, ["status", "--short"])
    git_head = run_git(cwd_str, ["rev-parse", "--short", "HEAD"])

    # ----------------------------------------------------------------
    # Session number
    # ----------------------------------------------------------------
    session_n = count_session_number(handover_doc)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    # ----------------------------------------------------------------
    # Build draft content
    # ----------------------------------------------------------------
    draft_content = f"""# {agent_id} — 현재 프로젝트 상태 (Rolling State)
> 마지막 갱신: {timestamp} Session {session_n} [DRAFT — 에이전트 완성 필요]

## 현재 마일스톤
<!-- TODO: 현재 진행 중인 주요 작업/목표 -->

## 이번 세션 성과 (Session {session_n})
<!-- TODO: 결정, 구현, 해결한 문제 서술 -->

## 다음 세션 부트
```
작업 디렉토리: {cwd_str}
HEAD: {git_head}

최근 커밋:
{git_log}

변경 파일:
{git_status}
```

## Task 대기열
| ID | 우선순위 | 내용 |
|----|---------|------|
<!-- TODO: 미완료 작업 -->

## 핵심 결정 이력
| 결정 | 근거 | 날짜 |
|------|------|------|
<!-- TODO: 이번 세션 핵심 결정 추가 -->
"""

    # ----------------------------------------------------------------
    # Write draft (always overwrite)
    # ----------------------------------------------------------------
    draft_path = handover_doc / "CURRENT_STATE.md.draft"
    try:
        draft_path.write_text(draft_content, encoding="utf-8")
    except Exception as e:
        print(f"[stop_hook] ERROR: draft 파일 쓰기 실패: {e}", file=sys.stderr)
        return 1

    # ----------------------------------------------------------------
    # Update rate limit marker
    # ----------------------------------------------------------------
    try:
        marker.write_text(str(now), encoding="utf-8")
    except Exception:
        pass

    # ----------------------------------------------------------------
    # Emit structured signal to stdout
    # ----------------------------------------------------------------
    print(f'<handover-draft-ready path="handover_doc/CURRENT_STATE.md.draft" session="{session_n}"/>')
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="handover stop hook — CURRENT_STATE.md.draft 생성")
    parser.add_argument("--cwd", default=None, help="프로젝트 절대경로 (없으면 config 자동 탐색)")
    args = parser.parse_args()
    sys.exit(main(cwd=args.cwd))
