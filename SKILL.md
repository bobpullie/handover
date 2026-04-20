---
name: handover
upstream: https://github.com/bobpullie/handover
update_cmd: cd ~/.claude/skills/handover && git pull
description: 세션 간 컨텍스트 유지 핸드오버 시스템 — CURRENT_STATE.md 롤링 상태 + 세션 핸드오버 문서 + SessionStart/Stop hook
---

# Handover — 세션 컨텍스트 유지 시스템

## Boot Protocol (세션 시작 시 자동 — SessionStart hook)

1. `handover_doc/CURRENT_STATE.md` 읽기 → 이전 상태 복원
2. `handover_doc/CURRENT_STATE.md.draft` 존재하면 → "미완성 핸드오버 있음" 경고 출력 후 draft 완성 요청

## Shutdown Protocol (트리거: "퇴근" / "종료" / "끝" / "마무리" 감지 시)

Stop hook이 이미 `.draft` 생성 완료됨. 아래 단계를 순서대로 실행:

1. `handover_doc/CURRENT_STATE.md.draft` 열기
2. `<!-- TODO -->` 섹션 채우기:
   - 이번 세션 성과 (결정, 구현, 해결한 문제)
   - 다음 세션 부트 컨텍스트 (어디서 멈췄는지, 불확실한 점)
   - Task 대기열 갱신
   - 핵심 결정 이력 추가
3. `handover_doc/CURRENT_STATE.md` 덮어쓰기 (draft 내용으로)
4. `handover_doc/YYYY-MM-DD_sN.md` 저장 (`templates/session-doc.md` 형식)
5. **[adapter: triad만]** QMD recap → `qmd_drive/recaps/YYYY-MM-DD_sN.md`
6. **[adapter: triad만]** TWK L2 추출:
   ```
   python ~/.claude/skills/TWK/scripts/extract_session_raw.py --config ./wiki.config.json
   ```
7. `.draft` 파일 삭제

## 파일 구조

```
handover_doc/
├── CURRENT_STATE.md          ← 롤링 상태 (항상 최신)
├── CURRENT_STATE.md.draft    ← stop_hook 생성, 에이전트가 완성 후 삭제
└── YYYY-MM-DD_sN.md          ← 세션별 상세 기록
```

## 설정 파일

`.claude/handover_config.json`:
```json
{
  "agent_id": "...",
  "cwd": "...",
  "adapter": "triad"   // 없으면 null
}
```
