---
name: harness-workflow
description: Оркестрация harness-фаз при команде «реши задачу N», «возьми в работу N», «solve issue N» или любой другой задаче на GitHub Issues: запустить planner → scheduler → executor как субагентов, передавать результат между фазами, понять когда остановиться. Use when the user points at a GitHub issue to work on.
---

# Harness workflow: planner → scheduler → executor

Оркестратор harness-модели из AGENTS.md (GitHub Issues Workflow). Фазы исполняются
как opencode-субагенты; основной агент только передаёт результат следующей фазе.

## Фазы

### 1. Planner
Вызови субагента planner через Task tool (`subagent_type: planner`) с номером
задачи N. Он вернёт YAML-граф: атомарность вершины, список вершин,
ready-candidates, созданные сабтаски.

Если субагент недоступен (opencode не перезапущен после добавления) — выполни
планирование прямо: `gh issue view N` + `--comments`, критерий атомарности,
при необходимости `gh issue create --parent N` с рёбрами `Depends on:`/`Blocks:`,
label `atomic`.

### 2. Scheduler
Вызови субагента scheduler (`subagent_type: scheduler`) со списком кандидатов
(вершины графа из отчёта planner). Он вернёт ready-set и blocked.

Фолбэк без субагента: для каждой вершины распарси `Depends on:`/`Blocks:` из тела
и проверь `gh issue view <n> --json state`; READY = все блокеры CLOSED.

### 3. Executor
Для каждой вершины из ready-set вызови субагента executor
(`subagent_type: executor`) с номером вершины. Он вернёт done (issue, commit) и
unblocked (открывшиеся вершины).

Фолбэк без субагента: строго по AGENTS.md (explore → implement → verify → commit
`[AI] #<id> ...` → push → close c [AI]-комментарием).

## Петля и остановка

1. После закрытия каждой вершины пересчитай scheduler — состояния меняются.
2. Закрытие блокера добавляет вершины в ready-set; исполняй их тем же executor.
3. Когда все листья родителя закрыты, но родитель ещё открыт — DoD-закрытие
   родителя: проверь его чек-лист и закрой с [AI]-комментарием.
4. Остановка: целевая вершина закрыта и её DoD подтверждён. Если ready-set пуст,
   а blocked непуст — это блокер: остановись и сообщи пользователю, какие вершины
   ждут и от каких зависимостей.

## Правила

- Роли не выполняют работу друг друга: planner не имплементирует, scheduler не
  трогает код, executor не планирует.
- Передача между фазами — только через отчёты субагентов (YAML), не через память
  сессии субагента.
- Все issue-комментарии и close-сообщения — в [AI]-формате.
- Каждый этап заканчивается `git push`.