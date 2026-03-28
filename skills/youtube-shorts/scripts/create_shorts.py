"""
YouTube Shorts 자동 제작 스크립트
- 퀴즈형, 제품리뷰형, 팁형 숏폼 영상 생성
- 텍스트 카드 + 배경색 + 자막 스타일
"""

import json
import sys
import os
import textwrap
from pathlib import Path

# moviepy 2.x imports
from moviepy import (
    TextClip, ColorClip, CompositeVideoClip,
    concatenate_videoclips, AudioFileClip, ImageClip
)


# ===== 설정 =====
OUTPUT_DIR = Path(r"G:\내 드라이브\클로드작업기록\YouTube_Shorts")
FONT = "C:/Windows/Fonts/malgunbd.ttf"  # 맑은 고딕 Bold
WIDTH, HEIGHT = 1080, 1920  # 세로 9:16
FPS = 24


# ===== 색상 테마 =====
THEMES = {
    "golf": {
        "bg": "#1a472a",       # 골프 그린
        "text": "#FFFFFF",
        "accent": "#FFD700",   # 골드
        "subtitle": "#90EE90"
    },
    "product": {
        "bg": "#1a1a2e",       # 다크 네이비
        "text": "#FFFFFF",
        "accent": "#e94560",   # 레드
        "subtitle": "#a8d8ea"
    },
    "tip": {
        "bg": "#0f3460",       # 딥블루
        "text": "#FFFFFF",
        "accent": "#e94560",
        "subtitle": "#16c79a"
    }
}


def hex_to_rgb(hex_color):
    """HEX 색상을 RGB 튜플로 변환"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def create_text_clip(text, fontsize=60, color="#FFFFFF", duration=3, position="center"):
    """텍스트 클립 생성"""
    # 긴 텍스트 줄바꿈
    wrapped = textwrap.fill(text, width=16)

    clip = TextClip(
        text=wrapped,
        font_size=fontsize,
        color=color,
        font=FONT,
        text_align="center",
        size=(WIDTH - 100, None),
        method="caption"
    )
    clip = clip.with_duration(duration).with_position(position)
    return clip


def create_slide(text, fontsize=60, color="#FFFFFF", bg_color="#1a472a",
                 duration=3, subtitle=None, subtitle_color="#90EE90"):
    """배경 + 텍스트로 한 장의 슬라이드 생성"""
    bg = ColorClip(size=(WIDTH, HEIGHT), color=hex_to_rgb(bg_color)).with_duration(duration)

    # 채널 워터마크
    watermark = TextClip(
        text="@MasterCollection_KR",
        font_size=28,
        color="#FFFFFF80",
        font=FONT
    ).with_duration(duration).with_position(("center", 50))

    # 메인 텍스트
    main_text = create_text_clip(text, fontsize=fontsize, color=color,
                                  duration=duration, position="center")

    layers = [bg, watermark, main_text]

    # 서브타이틀 (있으면)
    if subtitle:
        sub_text = TextClip(
            text=subtitle,
            font_size=36,
            color=subtitle_color,
            font=FONT,
            text_align="center",
            size=(WIDTH - 120, None),
            method="caption"
        ).with_duration(duration).with_position(("center", HEIGHT - 300))
        layers.append(sub_text)

    return CompositeVideoClip(layers, size=(WIDTH, HEIGHT))


def create_quiz_video(data, output_path):
    """퀴즈형 숏폼 생성"""
    theme = THEMES["golf"]
    slides = []

    # 인트로
    slides.append(create_slide(
        data["title"],
        fontsize=70,
        color=theme["accent"],
        bg_color=theme["bg"],
        duration=2,
        subtitle="3개 다 맞히면 고수!"
    ))

    # 퀴즈 Q&A
    for i, qa in enumerate(data["questions"], 1):
        # 질문
        slides.append(create_slide(
            f"Q{i}. {qa['question']}",
            fontsize=55,
            color=theme["text"],
            bg_color=theme["bg"],
            duration=4,
            subtitle="잠시 생각해보세요..."
        ))

        # 정답
        slides.append(create_slide(
            f"정답: {qa['answer']}",
            fontsize=65,
            color=theme["accent"],
            bg_color="#0d2818",
            duration=3,
            subtitle=qa.get("explanation", ""),
            subtitle_color=theme["subtitle"]
        ))

    # 아웃트로
    slides.append(create_slide(
        "몇 개 맞히셨나요?\n구독 & 좋아요!",
        fontsize=60,
        color=theme["accent"],
        bg_color=theme["bg"],
        duration=3,
        subtitle="@MasterCollection_KR"
    ))

    video = concatenate_videoclips(slides)
    video.write_videofile(str(output_path), fps=FPS, codec="libx264",
                          audio=False, logger=None)
    return output_path


def create_product_video(data, output_path):
    """제품 리뷰형 숏폼 생성"""
    theme = THEMES["product"]
    slides = []

    # 인트로 - 제품명
    slides.append(create_slide(
        data["product_name"],
        fontsize=55,
        color=theme["accent"],
        bg_color=theme["bg"],
        duration=3,
        subtitle=data.get("category", "추천 제품")
    ))

    # 특징들
    for i, feature in enumerate(data["features"], 1):
        slides.append(create_slide(
            f"#{i} {feature['title']}",
            fontsize=55,
            color=theme["text"],
            bg_color=theme["bg"],
            duration=4,
            subtitle=feature["detail"],
            subtitle_color=theme["subtitle"]
        ))

    # 추천 포인트
    slides.append(create_slide(
        data.get("recommendation", "강력 추천!"),
        fontsize=60,
        color=theme["accent"],
        bg_color="#0d0d1a",
        duration=3,
        subtitle="링크는 프로필에서!"
    ))

    # 아웃트로
    slides.append(create_slide(
        "더 많은 추천은\n구독 후 확인!",
        fontsize=60,
        color=theme["text"],
        bg_color=theme["bg"],
        duration=2,
        subtitle="@MasterCollection_KR"
    ))

    video = concatenate_videoclips(slides)
    video.write_videofile(str(output_path), fps=FPS, codec="libx264",
                          audio=False, logger=None)
    return output_path


def create_tip_video(data, output_path):
    """팁/명언형 숏폼 생성"""
    theme = THEMES["tip"]
    slides = []

    # 인트로
    slides.append(create_slide(
        data["title"],
        fontsize=65,
        color=theme["accent"],
        bg_color=theme["bg"],
        duration=2
    ))

    # 팁들
    for i, tip in enumerate(data["tips"], 1):
        slides.append(create_slide(
            f"TIP {i}\n{tip['title']}",
            fontsize=55,
            color=theme["text"],
            bg_color=theme["bg"],
            duration=4,
            subtitle=tip["detail"],
            subtitle_color=theme["subtitle"]
        ))

    # 마무리
    slides.append(create_slide(
        data.get("closing", "오늘도 좋은 라운딩!"),
        fontsize=60,
        color=theme["accent"],
        bg_color=theme["bg"],
        duration=3,
        subtitle="구독하고 더 많은 팁 받기!"
    ))

    video = concatenate_videoclips(slides)
    video.write_videofile(str(output_path), fps=FPS, codec="libx264",
                          audio=False, logger=None)
    return output_path


def main():
    if len(sys.argv) < 2:
        print("사용법: python create_shorts.py <json_data_file>")
        sys.exit(1)

    json_path = sys.argv[1]
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 출력 폴더 생성
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    video_type = data.get("type", "quiz")
    filename = data.get("filename", f"shorts_{video_type}")
    output_path = OUTPUT_DIR / f"{filename}.mp4"

    if video_type == "quiz":
        result = create_quiz_video(data, output_path)
    elif video_type == "product":
        result = create_product_video(data, output_path)
    elif video_type == "tip":
        result = create_tip_video(data, output_path)
    else:
        print(f"알 수 없는 유형: {video_type}")
        sys.exit(1)

    print(f"영상 생성 완료: {result}")
    print(json.dumps({"output": str(result), "type": video_type}, ensure_ascii=False))


if __name__ == "__main__":
    main()
