---
name: sync-backup
description: >
  GitHub와 Google Drive 간 스킬/작업자료 동기화 및 백업 스킬.
  PC 부팅 시 또는 수동으로 실행하여:
  (1) GitHub 리포(kjc0690-gif/idfenc_meet)에서 최신 스킬/자료를 pull
  (2) G드라이브 '클로드작업기록' 폴더에서 로컬로 동기화
  (3) 로컬 작업내용을 GitHub에 push
  (4) 로컬 작업내용을 G드라이브에 백업
  "동기화", "싱크", "sync", "백업", "backup", "스킬 가져와", "스킬 업데이트",
  "GitHub에서 내려받아", "pull", "push", "G드라이브 백업", "작업 올려",
  "스킬 복원", "restore" 등의 표현이 나오면 트리거한다.
  /sync-backup 명령으로도 실행 가능하다.
---

# GitHub & G드라이브 동기화/백업 스킬

## 역할

다른 PC에서 작업한 스킬과 작업자료를 GitHub/G드라이브에서 가져오고,
현재 PC의 작업내용을 GitHub/G드라이브에 백업하는 **양방향 동기화** 스킬.

## 핵심 경로

| 구분 | 경로 |
|------|------|
| **로컬 작업폴더** | `C:\Users\kjc06\클로드 작업기록\idfenc_meet` |
| **로컬 스킬폴더** | `C:\Users\kjc06\클로드 작업기록\idfenc_meet\skills` |
| **GitHub 리포** | `https://github.com/kjc0690-gif/idfenc_meet` (branch: master) |
| **G드라이브 폴더** | `G:\내 드라이브\클로드작업기록` |
| **G드라이브 폴더 ID** | `1xJA2AYRHXUffXlvbNAhsvY2-hMgtIsp7` |

## 동기화 매핑

| GitHub 리포 경로 | 로컬 경로 |
|-----------------|----------|
| `skills/` | `C:\Users\kjc06\클로드 작업기록\idfenc_meet\skills\` |
| `TBM/` | `C:\Users\kjc06\클로드 작업기록\idfenc_meet\TBM\` |
| `scripts/` | `C:\Users\kjc06\클로드 작업기록\idfenc_meet\scripts\` |
| `CLAUDE.md` | `C:\Users\kjc06\클로드 작업기록\idfenc_meet\CLAUDE.md` |

## 실행 모드

### 1. 풀 동기화 (기본) - `/sync-backup` 또는 "동기화해줘"
전체 과정을 순서대로 실행:
1. **Pull**: GitHub에서 최신 코드 pull
2. **G드라이브 → 로컬**: G드라이브 변경사항 확인 및 동기화
3. **스킬 업데이트**: 스킬백업 → .claude/skills로 SKILL.md 및 scripts 복사
4. **Push**: 로컬 변경사항을 GitHub에 push
5. **로컬 → G드라이브**: 변경된 파일을 G드라이브에 백업

### 2. 다운로드만 - "GitHub에서 가져와" / "스킬 내려받아"
GitHub pull + 스킬 업데이트만 수행

### 3. 업로드만 - "GitHub에 올려" / "백업해줘"
GitHub push + G드라이브 백업만 수행

### 4. 스킬 복원 - "스킬 복원해줘" / "스킬 업데이트해줘"
스킬백업 폴더의 내용을 .claude/skills에 반영

## 실행 절차

### Step 1: GitHub Pull (다운로드)
```bash
# 로컬 작업폴더가 git 초기화 안 되어 있으면 초기화
cd "C:\Users\kjc06\클로드 작업기록\idfenc_meet"
git init
git remote add origin https://github.com/kjc0690-gif/idfenc_meet.git
git pull origin master
```

### Step 2: G드라이브 → 로컬 동기화
- G드라이브 폴더(`G:\내 드라이브\클로드작업기록`)가 마운트되어 있으면 직접 복사
- 마운트 안 되어 있으면 Google Drive MCP로 파일 목록 조회 후 안내

```bash
# G드라이브가 마운트된 경우
if [ -d "G:/내 드라이브/클로드작업기록" ]; then
    # G드라이브 → 로컬 복사 (최신 파일만)
    robocopy "G:\내 드라이브\클로드작업기록\스킬백업" "C:\Users\kjc06\클로드 작업기록\idfenc_meet\스킬백업" /E /XO /NFL /NDL
fi
```

### Step 3: 스킬 활성화 (스킬백업 → .claude/skills)
스킬백업 폴더의 각 스킬을 .claude/skills에 복사하여 활성화:
```bash
# 각 스킬 디렉토리에 대해
for skill_dir in "C:\Users\kjc06\클로드 작업기록\idfenc_meet\스킬백업\*"; do
    skill_name=$(basename "$skill_dir")
    target="C:\Users\kjc06\클로드 작업기록\idfenc_meet\skills\$skill_name"
    mkdir -p "$target"
    cp -r "$skill_dir"/* "$target"/
done
```

### Step 4: GitHub Push (업로드)
```bash
cd "C:\Users\kjc06\클로드 작업기록\idfenc_meet"
git add -A
git commit -m "sync: 작업내용 백업 $(date +%Y-%m-%d_%H%M)"
git push origin master
```

### Step 5: 로컬 → G드라이브 백업
```bash
# G드라이브가 마운트된 경우
robocopy "C:\Users\kjc06\클로드 작업기록\idfenc_meet" "G:\내 드라이브\클로드작업기록" /E /XO /NFL /NDL
```

## .gitignore 규칙
다음 파일은 동기화에서 제외:
- `*.tmp`, `*.log`
- `__pycache__/`
- `.env`
- `node_modules/`
- `*.pyc`

## 주의사항
- **충돌 방지**: pull 시 로컬 변경이 있으면 먼저 stash 후 pull, 그 다음 stash pop
- **스킬 우선순위**: GitHub의 스킬이 로컬보다 최신이면 GitHub 것으로 덮어씀
- **G드라이브 미마운트**: G드라이브가 마운트 안 되어 있으면 사용자에게 알리고 GitHub만 동기화
- **첫 실행**: git init + remote 설정이 안 되어 있으면 자동으로 초기화
- **gh CLI 경로**: `PATH`에 `/c/Program Files/GitHub CLI` 추가 필요
