---
name: harness-workflow
description: Оркестрация harness-фаз при команде «реши задачу N», «возьми в работу N», «solve issue N» или любой другой задаче на GitHub Issues: запустить team-lead → scrum-master → developer как субагентов, передавать результат между фазами, понять когда остановиться. Use when the user points at a GitHub issue to work on.
---

# Harness workflow: Team Lead → Scrum Master → Developer

Оркестратор harness-модели из AGENTS.md (GitHub Issues Workflow). Фазы исполняются
как opencode-субагенты по реальным позициям IT-команды; основной агент только
передаёт результат следующей фазе.

Маппинг «позиция → фаза графа» (`docs/harness-agents.md`): Team Lead = Planning,
Scrum Master = Scheduling (ready set), Developer = Execution.

## Фазы

### 1. Team Lead (Planning)
Вызови субагента team-lead через Task tool (`subagent_type: team-lead`) с номером
задачи N. Он вернёт YAML-граф: атомарность вершины, список вершин,
ready-candidates, созданные сабтаски.

Если субагент недоступен (opencode не перезапущен после добавления) — выполни
планирование прямо: `gh issue view N` + `--comments`, критерий атомарности,
при необходимости `gh issue create --parent N` с рёбрами `Depends on:`/`Blocks:`,
label `atomic`.

### 2. Scrum Master (Scheduling)
Вызови субагента scrum-master (`subagent_type: scrum-master`) со списком кандидатов
(вершины графа из отчёта team-lead). Он вернёт ready-set и blocked.

Фолбэк без субагента: для каждой вершины распарси `Depends on:`/`Blocks:` из тела
и проверь `gh issue view <n> --json state`; READY = все блокеры CLOSED.

### 3. Developer (Execution)
Для каждой вершины из ready-set вызови субагента developer
(`subagent_type: developer`) с номером вершины. Он вернёт done (issue, commit) и
unblocked (открывшиеся вершины).

Фолбэк без субагента: строго по AGENTS.md (explore → implement → verify → commit
`[AI] #<id> ...` → push → close c [AI]-комментарием).

## Петля и остановка

1. После закрытия каждой вершины пересчитай scrum-master — состояния меняются.
2. Закрытие блокера добавляет вершины в ready-set; исполняй их тем же developer.
3. Когда все листья родителя закрыты, но родитель ещё открыт — DoD-закрытие
   родителя: проверь его чек-лист и закрой с [AI]-комментарием.
4. Остановка: целевая вершина закрыта и её DoD подтверждён. Если ready-set пуст,
   а blocked непуст — это блокер: остановись и сообщи пользователю, какие вершины
   ждут и от каких зависимостей.

## Правила

- Позиции не выполняют работу друг друга: team-lead не имплементирует,
  scrum-master не трогает код, developer не планирует.
- Передача между фазами — только через отчёты субагентов (YAML), не через память
  сессии субагента.
- Все issue-комментарии и close-сообщения — в [AI]-формате.
- Каждый этап заканчивается `git push`.