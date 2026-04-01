---
name: 유튜브쇼츠
description: 유튜브 숏폼 영상 자동 제작 스킬. 주제를 입력하면 계획→대본→영상(MP4) 자동 생성. 골프 퀴즈, 제품 리뷰, 팁 등. '숏폼', 'shorts', '유튜브 영상', '영상 만들어', '숏츠' 등을 언급하면 이 스킬 사용.
argument-hint: [주제] 예: "골프 퀴즈", "드라이버 추천", "퍼팅 팁"
allowed-tools: [Bash, Read, Write, Glob, Grep]
---

# 유튜브 숏폼 자동 제작 스킬

## 채널 정보
- **채널명**: Master Collection (@MasterCollection_KR)
- **채널 URL**: youtube.com/@MasterCollection_KR
- **주요 주제**: 골프, 여행, 라이프스타일
- **인포크링크**: link.inpock.co.kr/master.collection
- **스타일**: 텍스트 카드 기반 숏폼 (9:16 세로)

## 사용법

사용자가 숏폼 제작을 요청하면:

### 1단계: 계획 수립
$ARGUMENTS 에서 주제를 파악하고, 영상 유형을 결정:
- **quiz**: 퀴즈형 (3문제 + 정답/해설)
- **product**: 제품 리뷰형 (특징 3개 + 추천)
- **tip**: 팁/명언형 (팁 3개 + 마무리)

### 2단계: 대본 작성 (JSON)
영상 유형에 맞는 JSON 데이터를 생성하여 임시 파일로 저장.

#### 퀴즈형 JSON 예시:
```json
{
  "type": "quiz",
  "filename": "golf_quiz_20260328",
  "title": "골프 규칙 퀴즈!",
  "questions": [
    {
      "question": "OB가 나면 몇 타 벌타?",
      "answer": "1벌타 (스트로크와 거리)",
      "explanation": "OB는 1벌타 후 원래 위치에서 다시 칩니다"
    }
  ]
}
```

#### 제품 리뷰형 JSON 예시:
```json
{
  "type": "product",
  "filename": "volvik_v12_review",
  "product_name": "볼빅 V12 골프공",
  "category": "골프공 추천",
  "features": [
    {"title": "360도 퍼팅라인", "detail": "정확한 퍼팅 방향 잡기 가능"},
    {"title": "고반발 3피스", "detail": "비거리와 스핀 모두 잡는 구조"},
    {"title": "소프트 타구감", "detail": "부드러운 필링으로 컨트롤 UP"}
  ],
  "recommendation": "가성비 최강 골프공!"
}
```

#### 팁형 JSON 예시:
```json
{
  "type": "tip",
  "filename": "putting_tips",
  "title": "퍼팅 실력 올리는 비법",
  "tips": [
    {"title": "눈 아래에 공을", "detail": "어드레스 시 눈 바로 아래에 공이 오도록"},
    {"title": "백스윙과 폴로스루 같게", "detail": "진자운동처럼 균일한 스트로크"},
    {"title": "홀 뒤쪽을 노려라", "detail": "짧은 퍼팅보다 긴 퍼팅이 유리"}
  ],
  "closing": "연습만이 답이다!"
}
```

### 3단계: 영상 생성
```bash
python "C:/Users/kjc06/.claude/skills/youtube-shorts/scripts/create_shorts.py" "<json_file_path>"
```

### 4단계: 결과 안내
영상 생성 후 사용자에게 안내:
```
═══════════════════════════════
  🎬 숏폼 영상 생성 완료!
═══════════════════════════════
유형: (quiz/product/tip)
제목: (영상 제목)
파일: G:\내 드라이브\클로드작업기록\YouTube_Shorts\(파일명).mp4
───────────────────────────────
📌 다음 단계:
1. 영상을 확인하세요
2. YouTube Studio에서 업로드
3. 제목/설명/태그 추가
4. 쿠팡 파트너스 링크 연결 (제품 리뷰인 경우)
═══════════════════════════════
```

## 대본 작성 가이드라인
- 퀴즈는 정확한 골프 규칙/상식 기반
- 제품 리뷰는 실제 특징 중심 (과장 금지)
- 팁은 실용적이고 초보자도 이해 가능하게
- 모든 텍스트는 짧고 임팩트 있게 (한 줄 15자 이내)
- 해시태그: #골프 #골프규칙 #골프용품 #MasterCollection

## 출력 경로
- 영상: `G:\내 드라이브\클로드작업기록\YouTube_Shorts\`
- 대본: `G:\내 드라이브\클로드작업기록\YouTube_Shorts\scripts\`
