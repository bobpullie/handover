# handover — Claude Code 에이전트 핸드오버 스킬

세션 간 컨텍스트를 유지하는 핸드오버 시스템. 새 에이전트에 다운로드 즉시 적용 가능.

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
