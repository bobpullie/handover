# handover — Claude Code 에이전트 핸드오버 스킬

세션 간 컨텍스트를 유지하는 핸드오버 시스템. 새 에이전트에 다운로드 즉시 적용 가능.

---

## 5-Asset 4 원칙 (Independence + Local-Only + Separate-Repo + Universal Portability)

본 자산은 Triad Chord Studio 5-Asset 체계 (**TEMS / SDC / DVC / TWK / handover**) 의 한 축. 다음 4 게이트 원칙을 모두 만족해야 canonical GitHub 레포에 push 허용:

1. **Independence** — 5자산 상호 의존 0. handover 는 TEMS / SDC / DVC / TWK 미설치 환경에서도 self-contained 작동 (`--adapter triad` 는 옵션). 이 4 자산이 모두 있을 때만 추가 연동 단계 활성화.
2. **Local-Only** — 핸드오버 산출물 (`handover_doc/`, `CURRENT_STATE.md`) 은 각 에이전트 프로젝트 폴더 내부에만. 스킬 자체는 `~/.claude/skills/handover` (사용자 글로벌 스킬 디렉토리) 한정.
3. **Separate-Repo** — 각 자산 별도 canonical 레포 보유. 한 PR 에 두 레포 묶지 않음.
4. **Universal Portability** — Windows/Linux/macOS, 임의 OS user, 임의 에이전트명 작동. 절대경로/특정 user-name/hub 의존 금지 — `--cwd <PROJECT_PATH>` 인자로 프로젝트 경로 동적 주입.

위반 발견 시 즉시 일반화 PR.

---

## 설치 (PC당 1회)
git clone https://github.com/bobpullie/handover ~/.claude/skills/handover

## 에이전트 초기화 (프로젝트 디렉토리에서)
python ~/.claude/skills/handover/scripts/setup.py \
    --agent-id <ID> \
    --cwd <PROJECT_PATH> \
    [--adapter triad]

## 업데이트
cd ~/.claude/skills/handover && git pull

## 옵션
- `--adapter triad` : TEMS/QMD/TWK 연동 단계 활성화
- `--update`        : hook만 재등록 (CURRENT_STATE.md 보존)
- `--migrate`       : 기존 수동 핸드오버 시스템 → 이 스킬로 전환
