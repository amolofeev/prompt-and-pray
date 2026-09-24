---
name: tasks-gh
description: Операции с GitHub Issues через gh: прочитать задачу/комментарии, проверить ready set (блокеры Depends on), создать/спланировать сабтаски (gh issue create --parent, рёбра, label atomic), закрыть задачу с [AI]-комментарием, поднять unblocked по Blocks. Use when работа с задачами/issues/сабтасками, команды gh issue view/create/close, проверка блокеров, DoD-гейт родителя.
---

# Работа с задачами (GitHub Issues via gh)

Операционный слой взаимодействия с задачником. Тут — команды и состояния.
Процессные конвенции (чек-лист атомарности, формат рёбер, [AI]-формат
commit/close, оркестрация) — в skill `harness-workflow`: сначала читай его,
потом возвращайся сюда за командами. Не распространяй эти команды в промпты
ролей — ссылки на этот skill достаточно.

## Чтение

```bash
gh issue view <n>                      # задача: title, body, labels, state
gh issue view <n> --comments           # комментарии (план, отчёты, DoD)
gh issue view <n> --json state,parent  # состояние, родитель (если сабтаска)
gh issue view <parent> --json subIssues # подчинённые вершины (id, state)
gh issue view <n> --json blockedBy,blocking # зависимости (если доступны)
```

`--json` — предпочтительный способ: стабильные поля, без пропарсинга текста.

## Ready set: проверка блокеров

Вершина READY iff все `Depends on:` блокеры CLOSED.

1. Из тела задачи возьми блокеры `Depends on: #x`.
2. Для каждого проверь состояние:

```bash
gh issue view <x> --json state -q .state   # ожидается "CLOSED"
```

3. Любой открытый блокер → вершина BLOCKED, в работу не берётся.
4. Открой закрытый ею блок (`Blocks: #y`) → кандидат в unblocked-отчёт.

## Создание/планирование сабтасок

Родителя спланировал team-lead (skill harness-workflow): атомарность, рёбра,
инфраструктурные вершины. Здесь — только исполнение через gh.

Сабтаска под родителя:

```bash
gh issue create --parent <root> \
  -l <labels> \
  --title "[AI] S<n> <краткое резюме>" \
  --body-file - <<'EOF'
[AI] <резюме>

<одна исполнимая вершина: что сделать и почему>
EOF
```

Определение корректности по чек-листу атомарности — из harness-workflow.

## Рёбра и label

Формат рёбер задаёт harness-workflow (`Depends on: #x` / `Blocks: #y`).
Простановка:

```bash
gh issue edit <n> --body-file - <<'EOF'
<тело с рёбрами>
EOF
gh issue edit <n> --add-label atomic
```

Проверить связность графа:

```bash
gh issue view <parent> --json subIssues
```

## Закрытие с [AI]-комментарием

```bash
gh issue close <n> --comment "..."   # строго [AI]-резюме
```

Формат close-комментария — из harness-workflow (`[AI] <краткое резюме>` +
содержимое).

## Unblocked

После close закрой им разблокированные вершины:

1. Из тела закрытой задачи возьми `Blocks: #y`.
2. Для каждого `#y` проверь состояние `gh issue view <y> --json state -q .state`.
3. Открытые → в отчёт `unblocked: [ <#y> ]` и к delivery для пересчёта ready set.