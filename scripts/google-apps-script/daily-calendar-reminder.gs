/**
 * 매일 아침 7시 캘린더 일정 + 할 일 알림 이메일 발송
 * Google Apps Script - 트리거로 자동 실행
 */

const RECIPIENT_EMAIL = 'kjc0690@gmail.com';
const TIMEZONE = 'Asia/Seoul';

const CALENDARS = [
  { id: 'primary', name: '기본' },
  { id: 'e61f4ef0a712197f746956b27a08ebb7ea5306a4fdc485197b84ba6a36f8f934@group.calendar.google.com', name: '업무' },
  { id: '773224cbd7e7a553f7dee7c63a7aa9f0c018b4d63338ec95250410c7134c7226@group.calendar.google.com', name: '현장스케줄' },
  { id: 'e372bc4c76aad7fe994d0cd791fba21ca128723d84b080a916705896b8a910fc@group.calendar.google.com', name: '경조사' },
  { id: 'c7768fd5fc87f7ebaa1130e13652fc8490ae309eafd871461c9afd489017fbc2@group.calendar.google.com', name: '월례회 및 만남' },
  { id: 'ko.south_korea#holiday@group.v.calendar.google.com', name: '공휴일' }
];

const DAYS_KR = ['일', '월', '화', '수', '목', '금', '토'];

function sendDailyReminder() {
  const today = new Date();
  const isMonday = today.getDay() === 1;

  let body;
  let subject;

  if (isMonday) {
    body = buildWeeklyReport(today);
    subject = '📅 [주간 일정] ' + formatDateKR(today) + ' 주간 알림';
  } else {
    body = buildDailyReport(today);
    subject = '📅 [일정 알림] ' + formatDateKR(today);
  }

  // 미완료 할 일 추가
  const todos = getIncompleteTasks();
  if (todos.length > 0) {
    body += '\n\n━━━ ⚠️ 미완료 할 일 ━━━\n';
    todos.forEach(function(task) {
      const dueInfo = task.due ? ' (기한: ' + Utilities.formatDate(new Date(task.due), TIMEZONE, 'M/d') + ' ⏰ 기한지남!)' : ' (기한 없음)';
      body += '• ' + task.title + dueInfo + '\n';
    });
  } else {
    body += '\n\n━━━ ✅ 할 일 ━━━\n• 미완료 할 일이 없습니다!\n';
  }

  body += '\n💡 오늘 하루도 화이팅!';

  MailApp.sendEmail({
    to: RECIPIENT_EMAIL,
    subject: subject,
    body: body
  });

  Logger.log('알림 이메일 발송 완료: ' + subject);
}

function buildDailyReport(today) {
  const tomorrow = addDays(today, 1);
  const dayAfter = addDays(today, 2);

  let body = '📅 ' + formatDateKR(today) + ' 일정 알림\n\n';

  body += '━━━ 오늘의 일정 (' + formatDateKR(today) + ') ━━━\n';
  body += getEventsForDate(today);

  body += '\n━━━ 내일 일정 (' + formatDateKR(tomorrow) + ') ━━━\n';
  body += getEventsForDate(tomorrow);

  body += '\n━━━ 모레 일정 (' + formatDateKR(dayAfter) + ') ━━━\n';
  body += getEventsForDate(dayAfter);

  return body;
}

function buildWeeklyReport(monday) {
  let body = '📅 ' + formatDateKR(monday) + ' 주간 일정 알림\n\n';

  for (let i = 0; i < 7; i++) {
    const date = addDays(monday, i);
    body += '━━━ ' + formatDateKR(date) + ' ━━━\n';
    body += getEventsForDate(date);
    body += '\n';
  }

  return body;
}

function getEventsForDate(date) {
  const startOfDay = new Date(date.getFullYear(), date.getMonth(), date.getDate(), 0, 0, 0);
  const endOfDay = new Date(date.getFullYear(), date.getMonth(), date.getDate(), 23, 59, 59);

  let allEvents = [];

  CALENDARS.forEach(function(cal) {
    try {
      const calendar = CalendarApp.getCalendarById(cal.id);
      if (!calendar) return;

      const events = calendar.getEvents(startOfDay, endOfDay);
      events.forEach(function(event) {
        allEvents.push({
          title: event.getTitle(),
          start: event.getStartTime(),
          end: event.getEndTime(),
          location: event.getLocation(),
          isAllDay: event.isAllDayEvent(),
          calName: cal.name
        });
      });
    } catch (e) {
      Logger.log('캘린더 조회 실패 (' + cal.name + '): ' + e.message);
    }
  });

  if (allEvents.length === 0) {
    return '• 일정이 없습니다 😊\n';
  }

  // 시간순 정렬
  allEvents.sort(function(a, b) { return a.start - b.start; });

  let result = '';
  allEvents.forEach(function(ev) {
    if (ev.isAllDay) {
      result += '• [종일] ' + ev.title;
    } else {
      const startTime = Utilities.formatDate(ev.start, TIMEZONE, 'HH:mm');
      const endTime = Utilities.formatDate(ev.end, TIMEZONE, 'HH:mm');
      result += '• [' + startTime + '~' + endTime + '] ' + ev.title;
    }
    if (ev.location) result += ' 📍' + ev.location;
    result += ' (' + ev.calName + ')\n';
  });

  return result;
}

function getIncompleteTasks() {
  let incompleteTasks = [];

  try {
    const taskLists = Tasks.Tasklists.list();
    if (!taskLists.items) return incompleteTasks;

    taskLists.items.forEach(function(taskList) {
      try {
        const tasks = Tasks.Tasks.list(taskList.id, {
          showCompleted: false,
          showHidden: false
        });

        if (tasks.items) {
          tasks.items.forEach(function(task) {
            if (task.status !== 'completed' && task.title) {
              incompleteTasks.push({
                title: task.title,
                due: task.due || null,
                listName: taskList.title
              });
            }
          });
        }
      } catch (e) {
        Logger.log('태스크 조회 실패 (' + taskList.title + '): ' + e.message);
      }
    });
  } catch (e) {
    Logger.log('Tasks API 오류: ' + e.message);
  }

  return incompleteTasks;
}

function formatDateKR(date) {
  const m = date.getMonth() + 1;
  const d = date.getDate();
  const day = DAYS_KR[date.getDay()];
  return m + '/' + d + ' (' + day + ')';
}

function addDays(date, days) {
  const result = new Date(date);
  result.setDate(result.getDate() + days);
  return result;
}

/**
 * 초기 설정 - 한 번만 실행
 * 매일 아침 7시 트리거 생성
 */
function setupDailyTrigger() {
  // 기존 트리거 삭제
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(function(trigger) {
    if (trigger.getHandlerFunction() === 'sendDailyReminder') {
      ScriptApp.deleteTrigger(trigger);
    }
  });

  // 매일 아침 7시 트리거 생성
  ScriptApp.newTrigger('sendDailyReminder')
    .timeBased()
    .atHour(7)
    .everyDays(1)
    .inTimezone(TIMEZONE)
    .create();

  Logger.log('매일 아침 7시 트리거가 설정되었습니다.');
}

/**
 * 테스트 실행
 */
function testReminder() {
  sendDailyReminder();
}
