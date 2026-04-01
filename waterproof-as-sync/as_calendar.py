"""
(주)아이디에프이앤씨 AS 대응 시스템 - 구글 캘린더 연동 스크립트

AS 프로세스 JSON 데이터에서 일정(회의, 현장방문, 시공)을 추출하여
구글 캘린더 이벤트 형식으로 출력한다.

사용법:
  python as_calendar.py <json_file>       → 추출된 일정 목록 출력
  python as_calendar.py <json_file> --json → JSON 형식 출력

Claude Code의 gcal MCP 도구(gcal_create_event)와 연동하여 사용한다.
"""

import json
import sys
import os
import io
from datetime import datetime, timedelta

# Windows cp949 인코딩 문제 방지
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


# ──── 활동 유형별 캘린더 설정 ────
ACTIVITY_CONFIG = {
    'visit': {
        'label': '현장방문',
        'emoji': '🔍',
        'duration_hours': 2,
        'default_time': '10:00',
        'color': '9',      # blueberry (Google Calendar color ID)
        'calendar': '업무',
    },
    'meeting': {
        'label': '회의',
        'emoji': '💬',
        'duration_hours': 1.5,
        'default_time': '14:00',
        'color': '5',      # banana
        'calendar': '업무',
    },
    'construction': {
        'label': '시공',
        'emoji': '⚒️',
        'duration_hours': 8,
        'default_time': '08:00',
        'color': '10',     # basil
        'calendar': '현장스케줄',
    }
}


def parse_time(time_str, default='10:00'):
    """시간 문자열을 HH:MM 형식으로 변환한다."""
    if not time_str or time_str.strip() == '':
        return default
    t = time_str.strip().replace('시', ':').replace(' ', '')
    # 14:00, 14:30 형식
    if ':' in t:
        parts = t.split(':')
        h = int(parts[0]) if parts[0].isdigit() else 10
        m = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
        return f'{h:02d}:{m:02d}'
    # 숫자만 있으면 시간으로 해석
    if t.isdigit():
        h = int(t)
        if h <= 24:
            return f'{h:02d}:00'
    return default


def parse_date(date_str):
    """날짜 문자열을 YYYY-MM-DD 형식으로 변환한다."""
    if not date_str:
        return None
    d = date_str.strip()
    # 이미 YYYY-MM-DD 형식
    if len(d) == 10 and d[4] == '-' and d[7] == '-':
        return d
    # YYYYMMDD
    if len(d) == 8 and d.isdigit():
        return f'{d[:4]}-{d[4:6]}-{d[6:]}'
    # 기타 형식
    for fmt in ['%Y/%m/%d', '%Y.%m.%d', '%m/%d', '%m-%d']:
        try:
            dt = datetime.strptime(d, fmt)
            if dt.year == 1900:  # 연도 없으면 올해
                dt = dt.replace(year=datetime.now().year)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue
    return None


def extract_events(case_data):
    """AS 케이스 데이터에서 캘린더 이벤트를 추출한다."""
    events = []
    site_name = case_data.get('siteName', 'AS 현장')
    case_id = case_data.get('caseId', '')

    for i, activity in enumerate(case_data.get('activities', [])):
        a_type = activity.get('type', 'visit')
        config = ACTIVITY_CONFIG.get(a_type, ACTIVITY_CONFIG['visit'])

        date = parse_date(activity.get('date'))
        if not date:
            continue

        time_str = parse_time(
            activity.get('time'),
            config['default_time']
        )

        # 시작/종료 시간 계산
        start_dt = f'{date}T{time_str}:00'
        try:
            start = datetime.strptime(start_dt, '%Y-%m-%dT%H:%M:%S')
            end = start + timedelta(hours=config['duration_hours'])
            end_dt = end.strftime('%Y-%m-%dT%H:%M:%S')
        except ValueError:
            end_dt = f'{date}T18:00:00'

        # 이벤트 제목
        title = f'{config["emoji"]} [AS] {site_name} - {config["label"]}'
        if activity.get('content'):
            content_short = activity['content'][:30]
            if len(activity['content']) > 30:
                content_short += '...'
            title += f' ({content_short})'

        # 이벤트 설명
        description_parts = [
            f'AS 번호: {case_id}',
            f'현장명: {site_name}',
            f'활동유형: {config["label"]}',
            f'내용: {activity.get("content", "")}',
        ]

        # 회의 세부사항
        if a_type == 'meeting' and activity.get('meetingMinutes'):
            mm = activity['meetingMinutes']
            if mm.get('attendees'):
                description_parts.append(f'참석자: {", ".join(mm["attendees"])}')
            if mm.get('decisions'):
                description_parts.append(f'결정사항: {mm["decisions"]}')
            if mm.get('pending'):
                description_parts.append(f'보류사항: {mm["pending"]}')
            if mm.get('actionItems'):
                items = []
                for item in mm['actionItems']:
                    line = f'  - {item.get("task", "")}'
                    if item.get('assignee'):
                        line += f' (담당: {item["assignee"]})'
                    if item.get('deadline'):
                        line += f' [기한: {item["deadline"]}]'
                    items.append(line)
                description_parts.append('액션아이템:\n' + '\n'.join(items))

        # 시공 세부사항
        if a_type == 'construction' and activity.get('constructionLog'):
            cl = activity['constructionLog']
            if cl.get('weather'):
                description_parts.append(f'기상: {cl["weather"]}')
            if cl.get('workers'):
                description_parts.append(f'투입인원: {cl["workers"]}명')
            if cl.get('work'):
                description_parts.append(f'작업내용: {cl["work"]}')
            if cl.get('materials'):
                description_parts.append(f'사용자재: {cl["materials"]}')
            if cl.get('progress'):
                description_parts.append(f'진척도: {cl["progress"]}%')
            if cl.get('notes'):
                description_parts.append(f'특이사항: {cl["notes"]}')

        description = '\n'.join(description_parts)

        # 액션아이템 기한도 별도 이벤트로 추출
        action_events = []
        if a_type == 'meeting' and activity.get('meetingMinutes', {}).get('actionItems'):
            for item in activity['meetingMinutes']['actionItems']:
                deadline = parse_date(item.get('deadline'))
                if deadline:
                    action_events.append({
                        'title': f'📌 [AS 액션] {item.get("task", "")} - {item.get("assignee", "")}',
                        'date': deadline,
                        'start': f'{deadline}T09:00:00',
                        'end': f'{deadline}T09:30:00',
                        'description': (
                            f'AS 번호: {case_id}\n'
                            f'현장명: {site_name}\n'
                            f'할일: {item.get("task", "")}\n'
                            f'담당자: {item.get("assignee", "")}\n'
                            f'회의일: {date}'
                        ),
                        'calendar': '업무',
                        'type': 'action_item',
                        'timezone': 'Asia/Seoul',
                    })

        event = {
            'title': title,
            'date': date,
            'start': start_dt,
            'end': end_dt,
            'description': description,
            'calendar': config['calendar'],
            'type': a_type,
            'timezone': 'Asia/Seoul',
        }
        events.append(event)
        events.extend(action_events)

    return events


def format_for_display(events):
    """이벤트 목록을 사람이 읽기 좋은 형태로 포맷한다."""
    if not events:
        return '추출된 일정이 없습니다.'

    lines = [f'📅 추출된 캘린더 일정: 총 {len(events)}건\n']
    lines.append('=' * 50)

    for i, ev in enumerate(events, 1):
        lines.append(f'\n{i}. {ev["title"]}')
        lines.append(f'   날짜: {ev["date"]}')
        lines.append(f'   시간: {ev["start"].split("T")[1][:5]} ~ {ev["end"].split("T")[1][:5]}')
        lines.append(f'   캘린더: {ev["calendar"]}')
        if ev['type'] == 'action_item':
            lines.append(f'   ⚠️ 액션아이템 기한 알림')
        lines.append(f'   ---')

    lines.append(f'\n총 {len(events)}건의 일정을 구글 캘린더에 등록할 수 있습니다.')
    return '\n'.join(lines)


def format_for_gcal_mcp(events):
    """
    Claude Code의 gcal_create_event MCP 도구에 전달할 형식으로 변환한다.

    각 이벤트를 gcal_create_event 호출 파라미터 형식으로 출력한다:
    - summary: 이벤트 제목
    - start_time: ISO 형식 시작 시간
    - end_time: ISO 형식 종료 시간
    - description: 이벤트 설명
    - timezone: Asia/Seoul
    """
    gcal_events = []
    for ev in events:
        gcal_event = {
            'summary': ev['title'],
            'start_time': ev['start'],
            'end_time': ev['end'],
            'description': ev['description'],
            'timezone': 'Asia/Seoul',
        }
        gcal_events.append(gcal_event)
    return gcal_events


def main():
    if len(sys.argv) < 2:
        print('사용법: python as_calendar.py <json_file> [--json]')
        print()
        print('AS 백업 JSON 파일에서 캘린더 일정을 추출합니다.')
        print()
        print('옵션:')
        print('  --json    JSON 형식으로 출력 (gcal MCP 연동용)')
        print('  --gcal    gcal_create_event 파라미터 형식으로 출력')
        sys.exit(1)

    json_path = sys.argv[1]
    output_mode = 'display'
    if '--json' in sys.argv:
        output_mode = 'json'
    elif '--gcal' in sys.argv:
        output_mode = 'gcal'

    if not os.path.exists(json_path):
        print(f'파일을 찾을 수 없습니다: {json_path}')
        sys.exit(1)

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    events = extract_events(data)

    if output_mode == 'json':
        print(json.dumps(events, ensure_ascii=False, indent=2))
    elif output_mode == 'gcal':
        gcal_params = format_for_gcal_mcp(events)
        print(json.dumps(gcal_params, ensure_ascii=False, indent=2))
    else:
        print(format_for_display(events))


if __name__ == '__main__':
    main()
