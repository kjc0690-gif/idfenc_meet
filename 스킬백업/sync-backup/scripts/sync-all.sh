#!/bin/bash
# ============================================
# Claude 작업기록 동기화 스크립트
# GitHub <-> 로컬 <-> G드라이브 양방향 동기화
# ============================================

set -e

# 경로 설정
LOCAL_WORK="C:/Users/kjc06/클로드 작업기록/idfenc_meet"
LOCAL_SKILLS="C:/Users/kjc06/클로드 작업기록/idfenc_meet/skills"
SKILL_BACKUP="$LOCAL_WORK/스킬백업"
GDRIVE_WORK="G:/내 드라이브/클로드작업기록"
GITHUB_REPO="https://github.com/kjc0690-gif/idfenc_meet.git"
BRANCH="master"

export PATH="/c/Program Files/GitHub CLI:$PATH"

echo "========================================"
echo "  Claude 작업기록 동기화 시작"
echo "  $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"

# ---- Step 1: Git 초기화 확인 ----
echo ""
echo "[1/5] Git 저장소 확인..."
cd "$LOCAL_WORK"

if [ ! -d ".git" ]; then
    echo "  → Git 초기화 중..."
    git init
    git remote add origin "$GITHUB_REPO"
    echo "  ✅ Git 저장소 초기화 완료"
else
    echo "  ✅ Git 저장소 확인됨"
fi

# remote URL 확인/업데이트
CURRENT_REMOTE=$(git remote get-url origin 2>/dev/null || echo "")
if [ "$CURRENT_REMOTE" != "$GITHUB_REPO" ]; then
    git remote set-url origin "$GITHUB_REPO" 2>/dev/null || git remote add origin "$GITHUB_REPO"
fi

# ---- Step 2: GitHub Pull ----
echo ""
echo "[2/5] GitHub에서 최신 자료 가져오기..."
# 로컬 변경사항이 있으면 stash
HAS_CHANGES=$(git status --porcelain 2>/dev/null | head -1)
if [ -n "$HAS_CHANGES" ]; then
    echo "  → 로컬 변경사항 임시 저장 (stash)..."
    git add -A
    git stash push -m "auto-stash before sync $(date +%Y%m%d_%H%M%S)"
    STASHED=true
fi

# pull (첫 pull이면 --allow-unrelated-histories)
git pull origin "$BRANCH" --allow-unrelated-histories 2>/dev/null || \
git pull origin "$BRANCH" 2>/dev/null || \
echo "  ⚠️  Pull 실패 (새 리포이거나 네트워크 문제)"

# stash 복원
if [ "$STASHED" = true ]; then
    echo "  → 로컬 변경사항 복원..."
    git stash pop 2>/dev/null || echo "  ⚠️  Stash 복원 시 충돌 발생, 수동 확인 필요"
fi
echo "  ✅ GitHub Pull 완료"

# ---- Step 3: G드라이브 → 로컬 동기화 ----
echo ""
echo "[3/5] G드라이브 → 로컬 동기화..."
if [ -d "$GDRIVE_WORK" ]; then
    # 스킬백업 동기화
    if [ -d "$GDRIVE_WORK/스킬백업" ]; then
        cp -ru "$GDRIVE_WORK/스킬백업"/* "$SKILL_BACKUP"/ 2>/dev/null || true
        echo "  ✅ 스킬백업 동기화 완료"
    fi
    # TBM 동기화
    if [ -d "$GDRIVE_WORK/TBM" ]; then
        mkdir -p "$LOCAL_WORK/TBM"
        cp -ru "$GDRIVE_WORK/TBM"/* "$LOCAL_WORK/TBM"/ 2>/dev/null || true
        echo "  ✅ TBM 동기화 완료"
    fi
    echo "  ✅ G드라이브 → 로컬 동기화 완료"
else
    echo "  ⚠️  G드라이브 미마운트 (G: 드라이브 없음) - 건너뜀"
fi

# ---- Step 4: 스킬 활성화 (스킬백업 → .claude/skills) ----
echo ""
echo "[4/5] 스킬 활성화 중..."
SKILL_COUNT=0
if [ -d "$SKILL_BACKUP" ]; then
    for skill_dir in "$SKILL_BACKUP"/*/; do
        if [ -d "$skill_dir" ]; then
            skill_name=$(basename "$skill_dir")
            target="$LOCAL_SKILLS/$skill_name"
            mkdir -p "$target"
            cp -r "$skill_dir"* "$target"/ 2>/dev/null || true
            SKILL_COUNT=$((SKILL_COUNT + 1))
            echo "  → $skill_name 활성화됨"
        fi
    done
fi

# GitHub의 skills 폴더도 확인
if [ -d "$LOCAL_WORK/skills" ]; then
    for skill_dir in "$LOCAL_WORK/skills"/*/; do
        if [ -d "$skill_dir" ]; then
            skill_name=$(basename "$skill_dir")
            target="$LOCAL_SKILLS/$skill_name"
            # 이미 활성화된 스킬은 GitHub 것이 최신일 때만 덮어씀
            mkdir -p "$target"
            cp -ru "$skill_dir"* "$target"/ 2>/dev/null || true
            echo "  → $skill_name (GitHub) 활성화됨"
        fi
    done
fi
echo "  ✅ $SKILL_COUNT개 스킬 활성화 완료"

# ---- Step 5: GitHub Push (업로드) ----
echo ""
echo "[5/5] GitHub에 백업 중..."
cd "$LOCAL_WORK"
git add -A
CHANGES=$(git status --porcelain 2>/dev/null | head -1)
if [ -n "$CHANGES" ]; then
    git commit -m "sync: 자동 백업 $(date '+%Y-%m-%d %H:%M')"
    git push origin "$BRANCH" 2>/dev/null && \
        echo "  ✅ GitHub Push 완료" || \
        echo "  ⚠️  Push 실패 - 네트워크 확인 필요"
else
    echo "  ℹ️  변경사항 없음 - Push 건너뜀"
fi

# ---- G드라이브 백업 ----
if [ -d "$GDRIVE_WORK" ]; then
    echo ""
    echo "[추가] 로컬 → G드라이브 백업..."
    cp -ru "$LOCAL_WORK"/* "$GDRIVE_WORK"/ 2>/dev/null || true
    # .claude/skills도 G드라이브에 백업
    mkdir -p "$GDRIVE_WORK/스킬백업"
    for skill_dir in "$LOCAL_SKILLS"/*/; do
        if [ -d "$skill_dir" ]; then
            skill_name=$(basename "$skill_dir")
            mkdir -p "$GDRIVE_WORK/스킬백업/$skill_name"
            cp -r "$skill_dir"* "$GDRIVE_WORK/스킬백업/$skill_name"/ 2>/dev/null || true
        fi
    done
    echo "  ✅ G드라이브 백업 완료"
fi

echo ""
echo "========================================"
echo "  동기화 완료! $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"
