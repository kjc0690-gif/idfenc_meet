---
name: gcal-daily-reminder
description: 매일 아침 7시 구글 캘린더 일정 + 미완료 할 일 알림 → 대화창 + Gmail SMTP 발송
---

구글 캘린더 일간 알림을 실행해줘. gcal-reminder 스킬을 사용하여:
1. 오늘 일정을 gcal_list_events로 모든 캘린더에서 조회 (timeZone: Asia/Seoul)
2. 내일 일정을 gcal_list_events로 모든 캘린더에서 조회 (timeZone: Asia/Seoul)
3. 모레 일정을 gcal_list_events로 모든 캘린더에서 조회 (timeZone: Asia/Seoul)
4. 지난 30일간 모든 캘린더 이벤트 조회하여 미완료 할 일 자동 감지 후 todos.json 업데이트
5. ~/.claude/skills/gcal-reminder/todos.json에서 미완료 할 일(completed: false) 읽기
6. 스킬의 일간 알림 형식에 맞춰 보기 좋게 정리하여 대화창에 출력 (일정 없는 날에도 반드시 출력)
7. 미완료 할 일 섹션을 항상 포함 (기한 지남/기한 없음 구분)
8. 출력한 알림 내용을 python ~/.claude/skills/gcal-reminder/scripts/send_email.py 스크립트로 kjc0690@gmail.com에 이메일 발송

"3일간" = 오늘, 내일, 모레 (3일 후가 아님!)

조회할 캘린더 목록:
- primary (kjc0690@gmail.com)
- e61f4ef0a712197f746956b27a08ebb7ea5306a4fdc485197b84ba6a36f8f934@group.calendar.google.com (업무)
- 773224cbd7e7a553f7dee7c63a7aa9f0c018b4d63338ec95250410c7134c7226@group.calendar.google.com (현장스케줄)
- e372bc4c76aad7fe994d0cd791fba21ca128723d84b080a916705896b8a910fc@group.calendar.google.com (경조사)
- c7768fd5fc87f7ebaa1130e13652fc8490ae309eafd871461c9afd489017fbc2@group.calendar.google.com (월례회 및 만남)
- ko.south_korea#holiday@group.v.calendar.google.com (휴일)

오늘이 월요일이면 일간 알림 대신 주간 알림(이번 주 월~일 전체 일정 + 미완료 할 일)을 출력하고 이메일도 발송한다.