# AI memory: подпроект yt/ (локальная, gitignored)

Память подпроекта `yt`. Лежит в корне репозитория — `.opencode/yt_memory.md`.
Читай в начале работы над yt, обновляй по итогам рефлексии. Правила —
корневой AGENTS.md («Память агента») и `yt/AGENTS.md`.

## Проект yt (Go)

- `$Type` — невалидный Go-идентификатор (SPEC §2.4 ошибалась). Поле называется `Type`,
  json-тег `"$type"` (отклонение зафиксировано в коммите 34f36d9).
- Дизайн `internal/api/types.go`: `IssueCustomField.Value` = `json.RawMessage`
  (мульти-значения кастомных полей — массивы — не ломают декодирование; для рендера
  есть `ValueObject()`); `Guest/Archived/UntagOnResolve` — `*bool`, `Resolved` — `*int64`
  (omitempty). Списки полей — константы `FieldsXxx` в `internal/api/fields.go`
  (единый источник, SPEC §4.2).
- Снапшот спеки при недоступном сервере: `.opencode/openapi.json` (API 2025.3,
  статичный, gitignored). В репо слепок не хранится (SPEC §4.8); финальная
  сверка — Атом 8.4.
- `gh issue view N` с флагом `--comments` молча выводит пустоту — и plain-форма,
  и с `--json <fields>` (повторилось в #32). Тело+комментарии надёжно брать через
  `gh issue view N --json number,title,state,body,comments`.
- Тулчейн не в системном PATH: Go — `~/sdk/go1.24.0/bin/go`, пользуйся полным путём
  напрямую; golangci-lint — `~/go/bin/golangci-lint` (v1.64.7).
- Gotcha (#22): golangci-lint и `make build/lint` зовут `go` из PATH и падают с
  «go command required, not found», если PATH без Go. Запуск:
  `PATH="$HOME/sdk/go1.24.0/bin:$PATH" ~/go/bin/golangci-lint run` (или `make lint` с тем же PATH).
  С #42: `make lint` сам резолвит golangci-lint через `GOLANGCI_LINT ?= $(shell command -v ...)`
  с фолбэком на `$(HOME)/go/bin/golangci-lint` (бинарь не в PATH) — для `make lint`
  достаточно только PATH с Go.
- Cobra v1.10.2, факты, проверенные юнит-тестом (#21):
  - `rootCmd.Version` авто-генерирует флаг `--version`: печатает `"yt version <ver>\n"`
    в stdout, exit 0, выполняется ДО `PersistentPreRunE`.
  - persistent-флаги предков видны в подкоманде через `cmd.Flags().GetBool(...)`.
  - Поведение зависимостей проверять юнит-тестом, а не чтением исходников в module
    cache (это дёшево и доказуемо).
- Cobra v1.10.2, факты #22:
  - Help-шаблон печатает заголовки групп (`AddGroup`) даже если группа пустая.
  - Группы: `cmd.GroupID = "id"` у подкоманды; help/completion — через
    `SetHelpCommandGroupID` / `SetCompletionCommandGroupID`.
  - Проверка global-флага у подкоманды до Execute: `sub.InheritedFlags().Lookup(name)`
    (`cmd.Flags().Lookup` сработает только после merge persistent-флагов в Execute).
- Урок (#22): не добавлять в атом forward-looking код (контекст-геттер «на будущее») —
  golangci-lint unused отклонит, придётся выпиливать. В атоме только то, что
  используется сейчас.
- Gotcha (#22, post-review): `gh issue comment --body "..."` в двойных кавычках —
  бэктики и `$HOME`/`$PATH` интерпретируются shell-ом и портят текст. Многострочный
  текст — через `--body-file`. Удаление/правка комментария по GraphQL-`id`
  (`IC_kwDO...`) даёт 404 — нужен числовой `databaseId` (из того же запроса).
- Cobra v1.10.2, факт #25: root БЕЗ `RunE` не валидирует аргументы — `execute()`
  возвращает `flag.ErrHelp` по проверке `!c.Runnable()` ДО `ValidateArgs`. Итог:
  `yt bogus` печатал help и завершался с 0, а не с 2. Fix: root делается runnable
  (`RunE: cmd.Help()`), только тогда `root.Args` (unknown-command, exit 2) срабатывает.
- Атом 2.4 (#25), конвенции `internal/commands` для новых команд:
  - Валидация аргументов — ОБЯЗАТЕЛЬНО через `argsValidator(cobra.NoArgs)` (и т.п.):
    голый cobra-валидатор даст exit 1 вместо 2 (SPEC §4.4).
  - API-клиент уже в контексте (pipeline в PersistentPreRunE): брать через
    `requireClient(cmd)` (без токена — «no token provided», exit 1) или
    `configFromContext(cmd)`; свой `api.New` не создавать.
  - Exit-коды и формат «yt: <msg>» в stderr обрабатывает `run()` (root.go);
    `RunArgs` вешает signal-контекст (SIGINT/SIGTERM → 130).
  - Лог клиента режет scheme/host (`logTarget`): формат «GET /issues?$top=30»
    (SPEC §4.6); base URL и учётные данные в лог не попадают.
- Атом 3.3 (#23), API-обёртки чтения (все принимают `fields` + `$top/$skip`;
  `{id}` — ring-id/idReadable без преобразований через `EscapePath`):
  `Me(ctx, fields)`, `ListIssues(ctx, query, fields, top, skip)`,
  `Issue(ctx, id, fields)`, `IssueComments(ctx, id, fields, top, skip)`,
  `ListProjects(ctx, fields, top, skip)`, `ListTags(ctx, query, fields, top, skip)`,
  `Search(ctx, query, fields, top, skip)` (алиас ListIssues). Общий `listQuery()`
  в issues.go; нулевые `$top`/`$skip` не передаются.
- Покрытие `internal/api` после 3.3 временно 69.1% (обёртки без тестов — по DoD
  атома); httptest-тесты обёрток и возврат ≥70% — в Атоме 3.4 (#24). При закрытии
  этапа 3 порог должен быть подтверждён.
- Атом 4.2 (#28), формат yt issue view (нужно для golden #41):
  - Мета-строки объединяются через 2 пробела (`STATE: Open  PROJECT: PRJ  REPORTER: alex`);
    выравнивание в примере SPEC §3.4 (колонки 17/20) — мокап, не норма.
  - Разделители `─`×64 (секции) и `─`×11 (под Comments); даты `YYYY-MM-DD HH:MM` UTC
    (`formatDateTime`); пустое описание → `No description`; пустые мета/теги-блоки
    опускаются, при их отсутствии разделитель печатается один раз (без дубля).
  - `--json -c` всегда включает ключ `comments` (обёртка issueViewJSON), даже пустой
    список; без `-c` ключа нет.
- Атом 4.4 (#30), yt issue edit:
  - API: `UpdateIssue(ctx, id, fields, summary, description *string)` (POST
    /issues/{id}, query `fields`); тело — структура с `*string`-полями
    (`omitempty`): nil — поле не меняется (частичное обновление), пустая строка
    передаётся как есть. Поля ответа: `FieldsIssueEdit` = id,idReadable,summary,description.
  - Команда: `edit <id>`, флаги `--title`/`--body` БЕЗ шорткатов (в отличие от
    create с -t/-b — по SPEC §3.4), хотя бы один непустой (usage, exit 2).
    TTY: `✓ Updated issue <idReadable>`; `--json` — объект Issue.
  - Сверка эндпоинта с живым openapi.json (2025.3): query `fields` +
    `muteUpdateNotifications`; в v1 используется только `fields`.
  - Смоук против живого YouTrack: мишень — смоук-ишью `DEMO-20` (создан
    `yt issue create`, «Smoke test issue <ts>») — НЕ трогать реальные DEMO-N
    (1–19 — сид-ишью демо-проекта). Проверено: TTY/JSON, частичные правки
    title/body по отдельности, регистронезависимый idReadable (`demo-20`),
    404 → exit 1, валидация exit 2, лог без scheme/host/токена.
- Атом 4.5 (#31), yt issue close:
  - API: `ApplyCommand(ctx, query, comment string, issues []IssueRef, fields string)`
    (POST /commands, query `fields`); `IssueRef{ID,IDReadable}` — omitempty,
    валиден ровно один из двух. Тело: `{"query":"state: <s>","comment":...,"issues":[...]}`;
    пустой comment опускается (`omitempty`). Ответ — `CommandList{Issues []Issue}`,
    поля `FieldsCommandIssues = issues(id,idReadable,summary,resolved,project(id,shortName))`.
  - Эвристика id/idReadable (§4.1) — общий хелпер `parseIssueRef` (issueref.go,
    переиспользуется Атомом 5.4): ring-id `^[0-9]+-[0-9]+$` → `{id}`; idReadable
    `^[A-Za-z][A-Za-z0-9]*-[0-9]+$` БЕЗ учёта регистра → `{idReadable}`;
    остальное → `cannot parse issue id: <value>` (usageError, exit 2).
  - Команда: `close <id>...`, флаги `-s/--state` (дефолт `Fixed`), `-m/--message`,
    `-y/--yes`, `--json`. Без `-y` в TTY-режиме — подтверждение
    `! This will close N issue(s) via command "state: <s>". Continue? [y/N] `
    (в stderr, `readLineStdin`), отказ/EOF → `Aborted` (exit 1). TTY: `✓ <idReadable> → <state>`
    по строке; `--json` — массив issues (пустой → `[]`). Ошибка применения (400/403) —
    HTTP-ошибка с `error_description`, exit 1 (атомарность — интеграционный тест Атома 8.3).
  - Смоук против живого YouTrack: DEMO использует state `Done` (не `Fixed` —
    дефолт SPEC для стандартного воркфлоу) → `state: Fixed` даёт 400 «State expected: Fixed».
    Смоук-ишью DEMO-21/22/23 (созданы create, закрыты close). Рабочие проверки:
    TTY/JSON/batch/`-s`/`-m`/регистронезависимый idReadable (`demo-23`), подтверждение
    (EOF → Aborted, exit 1), invalid id → exit 2, stdout чист.
- Атом 4.6 (#32), yt issue delete:
  - API: `DeleteIssue(ctx, id)` — обёртка над уже готовым `Client.Delete`
    (DELETE /issues/{id} без тела; openapi 2025.3: ответ 200 без тела). id — как
    есть + `EscapePath`, БЕЗ `parseIssueRef` (path-based, как view/edit/comment list).
  - Команда: `delete <id>` (ExactArgs(1)), флаг `-y/--yes`. Без -y в TTY —
    подтверждение `! Warning: this will permanently delete <id>. Continue? [y/N] `
    (stderr, `readLineStdin`), отказ/EOF → `Aborted` (exit 1); успех —
    `✓ Deleted issue <id>` (exit 0). Сообщение эхо-ит входной id (регистр как ввёл,
    напр. ring-id `3-26`).
  - `--json` НЕ определён (SPEC §3.4: ответ «—», 200 без тела): JSON-ветки нет,
    печатается `✓ Deleted issue <id>` как auth logout; §4.3 запрещает обёртки без
    явного раздела. Формат фиксирован — закрепит golden Атома 7.3 (#41).
  - Смоук (живой сервер): смоук-ишью DEMO-24..28 (созданы create и удалены самой
    командой), ring-id работает, 404 → `request failed: 404 Not Found: Entity with
    id DEMO-999 not found` exit 1, невалидный токен exit 1, лог
    `DELETE /issues/DEMO-28` без scheme/host/токена.
  - Gotcha (тест 404): exact-match stderr не проходит — сервер добавляет
    `error_description` («... not found: no such issue»); сверять через
    `strings.Contains` (паттерн issue_view_test.go:252, issue_comment_test.go:369).
- Экономия токенов (командный атом): не читать issue.go целиком — регистрацию
  команды находить grep'ом (`AddCommand(newIssue`), паттерн подтверждения —
  в issue_close_cmd.go, тест-хелперы — grep `func (runRoot|runRootIn|isolatedConfig)`.
  То же при правке существующих рендеров вывода: `grep "func write" issue.go`
  и читать только целевые функции (writeIssueViewTTY, writeCommentListTTY и т.п.),
  а не весь файл (896 строк).
- Атом 5.1 (#33), yt issue comment list/create:
  - API: добавлена `CreateComment(ctx, id, text, fields)` (POST /issues/{id}/comments,
    тело `{"text": "..."}`, query `fields`); чтение — уже была `IssueComments`.
  - Разделитель в comment list — `─`×4 (`commentListRule`), дословно по примеру
    SPEC §3.4 «────»; в issue view под Comments — `─`×11 (`issueViewCommentRule`).
    Внутри SPEC разделители расходятся — выводить по секции каждой команды.
  - TTY list: «автор · дата», текст, между комментариями разделитель; пусто →
    `No comments for <id>` (exit 0). JSON — массив IssueComment (пустой → `[]`).
  - create: `-m/--message` либо `--editor` (взаимоисключающие, usage-ошибки exit 2);
    `--editor` — редактор с пустым буфером (`editCommentText`), текст TrimSpace,
    пусто → `no comment text provided` (exit 1). TTY: `✓ Added comment to <id>`.
  - Валидация list: `--limit must be at least 1`, `--skip must be non-negative`.
  - Смоук против живого YouTrack: list (непусто/пусто/`[]`), create (TTY/JSON),
    появление созданного комментария в list, usage-ошибки exit 2, stdout чист.
- Атом 5.2 (#37), yt search:
  - `search <query>` (ExactArgs(1)): сырой query передаётся как есть, без «умных»
    флагов issue list; флаги -l/--limit (дефолт 30, валидация 1..100), --skip (≥0),
    --json. Usage-ошибки те же, что у list: «--limit must be between 1 and 100»,
    «--skip must be non-negative» (exit 2).
  - Рендер полностью переиспользует issue list: writeIssueTTY/writeIssueJSON,
    FieldsIssueList; пустой результат — «No issues found for query "<q>"».
    API-обёртка `Search` — алиас `ListIssues` (тот же GET /issues).
  - Регистрация в root: группа "issues" (как issue), файл search_cmd.go.
  - Тест TTY-таблиц: проверяй наличие ячеек подстроками (`strings.Contains`),
    точный layout text/tabwriter не фиксировать — его закрепят golden-тесты
    Атома 7.3 (#41); для этого не нужно читать internal/output/table.go.
- Известные UTC-таймстампы (переиспользовать в фикстурах вместо счёта на глаз):
  1782864000000=2026-07-01 00:00, 1782914400000=2026-07-01 14:00,
  1783069200000=2026-07-03 09:00, 1783296000000=2026-07-06 00:00,
  1783245600000=2026-07-05 10:00.
- Атом 5.3 (#34), yt search suggest:
  - `yt search` — runnable-родитель с подкомандой `suggest` (cobra позволяет
    runnable-команде иметь подкоманды; флаги -l/--skip остаются локальными
    у родителя, у suggest их нет). Регистрация в root — как раньше, группа "issues".
  - API: `SearchSuggest(ctx, query, fields)` → POST /search/assist, тело
    `{"query":"..."}`, query `fields=FieldsSearchSuggest` (константа была с 3.2).
  - TTY: подсказки `option — description`, сгруппированы по `group`
    (заголовок `<group>:`), порядок групп — первого появления; пустая группа →
    заголовок `Suggestions:`; пустой результат → `No suggestions for "<query>"` (exit 0).
  - JSON: сырой объект SearchSuggestions; при пустых подсказках сервер
    ОПУСКАЕТ ключ suggestions (omitempty убирает его из вывода).
  - Живой сервер (localhost:8080): у ВСЕХ подсказок `group` пустой → TTY почти
    всегда с заголовком «Suggestions:». Демо-проект — `DEMO`, не `PRJ`
    (`search "project: PRJ"` → 400 invalid_query). Рабочий смоук:
    `bin/yt search suggest "has: "` (реальные подсказки).
  - Golden-тесты suggest (TTY/JSON) — Атом 7.3 (#41); формат выше не менять.
- Атом 5.4 (#35), yt command:
  - API: `ApplyCommand(ctx, query, comment, runAs string, issues []IssueRef, fields)`
    — runAs добавлен в общий commandRequest (`{query, comment?, runAs?, issues}`);
    пустой runAs не передаётся (omitempty). Сверено с openapi 2025.3: runAs —
    writable-поле CommandList.
  - Команда: `command "<commands>" <id>...` (MinimumNArgs(2); ПЕРВЫЙ аргумент —
    команда, остальные — id), флаги `-m/--message`, `--run-as` (БЕЗ шортката),
    `-y/--yes`, `--json`; группа "issues". id — через общий `parseIssueRef`
    (в `internal/commands/issueref.go`, не api).
  - TTY: `✓ <idReadable>: <rendered>`; `formatCommandQuery` — пары «name: value...»
    → «name → value», пары join «, » («state: Fixed Priority: High» →
    «state → Fixed, Priority → High»); команд не распознано → исходная строка.
    Формат зафиксирует golden Атома 7.3 (#41) — не менять.
  - Подтверждение: `! This will apply command "<query>" to N issue(s). Continue? [y/N] `
    (stderr, readLineStdin); отказ/EOF → `Aborted` exit 1. Текст промпта в SPEC
    §3.6 НЕ зафиксирован (в отличие от close/delete) — решение агента, закреплено тестом.
  - Gotcha (подтверждение в смоуке): `p.TTY() == (mode != JSON)` — промпт
    появляется и при pipe (не-терминале). Смоук команды без `-y` либо кормит stdin
    (`printf 'y\n' | bin/yt ...`), либо ожидает EOF → Aborted, exit 1 (это же
    объясняет поведение #31/#32).
  - Смоук (живой сервер): смоук-ишью DEMO-29 (create → command → delete);
    `priority: critical state: Done` — TTY-рендер «priority → critical, state → Done»,
    результат проверен `bin/yt issue view DEMO-29 --json` (resolved/state/prio).
    400 «State expected: BogusState» → exit 1; `--run-as admin` и `-m` (комментарий
    виден в comment list) работают; ring-id «3-29» → `{id}`; invalid id → exit 2;
    лог `POST /commands?fields=issues(...)` без scheme/host/токена.
- Атом 5.5 (#36), yt command assist:
  - `yt command` — runnable-родитель с подкомандой `assist` (как search/suggest);
    `assist <commands>` (ExactArgs(1), exit 2 при 0/2+ аргументах).
  - API: `CommandAssist(ctx, query, fields)` → POST /commands/assist, тело
    `{"query":"...","caret":N}`; caret = `utf8.RuneCountInString(query)` (символы,
    не байты — команды бывают не-ASCII). fields=FieldsCommandAssist (существовала с 3.2).
  - TTY: `OK: <option> — <description>` по строке на подсказку (БЕЗ группировки по
    group — в отличие от search suggest; SPEC §3.6 не требует). Пустой ответ →
    `No suggestions for "<query>"` (exit 0). `--json` — сырой объект CommandList.
  - Живой сервер (localhost:8080): `command assist "state: "` → реальные подсказки;
    полная команда («state: Fixed») и мусор («boguscommand!@#», «::») → ПУСТОЙ
    список (exit 0), НЕ ошибка — «сообщение об ошибке парсинга» в SPEC §3.6 = HTTP-ошибка
    (400 error_description), отдельного поля ошибки в fields нет.
  - Смоук: apply-путь после рефакторинга работает (`command "..." DEMO-N -y`);
    лог `POST /commands/assist?fields=query,suggestions(...)` без scheme/host/токена.
- Снапшот спеки (fallback при недоступном сервере): `.opencode/openapi.json`
  (API 2025.3, gitignored, переживает сессии — в отличие от /tmp). Слепок
  СТАТИЧНЫЙ: не перекачивать без причины; обновлять только при подозрении на
  смену версии API сервера (сверить `info.version`). Спека в репо не хранится
  (SPEC §4.8) — слепок только локально.
- Экономия токенов: для атома читай только релевантный раздел SPEC (§3.x),
  НЕ весь документ целиком (~933 строки). Формат команд уже зафиксирован
  в памяти по атомам — SPEC перечитывать целиком не нужно.
- Верификация поведения (смоук/интеграция) — по решению человека (#29):
  ТОЛЬКО против локального реального YouTrack (`localhost:8080`), тестовые/
  мок-серверы не создавать. Аутентификацию для смоука проверять САМОЙ
  утилитой: `bin/yt auth status` (живой GET /users/me, читает конфиг
  `~/.config/yt/config.yml`, при 401 → «✗ not logged in», exit 1) — это
  факт аутентификации, а не ручной заход в файл. Токен у человека /
  зондирование окружения — только если утилита сообщает об отсутствии
  валидной аутентификации (не выдумывать, не хардкодить).
  `~/.config/yt/config.yml` вручную НЕ открывать (содержит токен) — о конфиге
  судить только по выводу `bin/yt auth status`.
  Перед смоуком после правок кода пересобрать `bin/yt` (`PATH="$HOME/sdk/go1.24.0/bin:$PATH" make build`):
  stale-бинарь даёт misleading-ошибки («unknown shorthand flag: 'y' in -y» на новой команде).
  Для проверки state/полей живого сервера — `bin/yt issue view <id>` (дёшево),
  НЕ `search "project: DEMO" --json` (дамп всех кастомных полей всех задач — дорого).
   Смоук-ишью создавать ТОЛЬКО так:
   `id=$(bin/yt issue create -p DEMO -t "<summary>" --json | jq -r '.idReadable')` —
   summary передаётся флагом `-t`, НЕ позиционным аргументом (позиционный даёт
   «unknown command ... for yt issue create», exit 2); id из TTY-вывода
   (`✓ Created issue DEMO-N: <summary>`) через `tail -1` НЕ парсится — берётся вся
   строка с summary. В конце смоука — `bin/yt issue delete "$id" -y`.
  При «request failed: decode response» сначала проверяй сам запрос/ответ
  (в Python `BaseHTTPRequestHandler.self.path` включает query — path брать
  через `urlsplit`), а не дебагь CLI.
- Атом 6.1 (#38), yt project list:
  - API уже была: `ListProjects(ctx, fields, top, skip)` — GET /admin/projects,
    fields `FieldsProjectList` = id,name,shortName,archived,leader(id,login,fullName).
  - Команда: `project list`, флаги `-l/--limit` (дефолт 50, валидация
    «--limit must be at least 1»), `--skip` (≥0, «--skip must be non-negative»),
    `--json`. TTY-таблица SHORTNAME/NAME/ARCHIVED/LEADER (LEADER → login);
    пусто → «No projects found»; `--json` — массив Project (nil → []).
  - Смоук (живой сервер): DEMO/Demo project/false/admin; `--json` валиден (jq);
    `-l 1 --skip 0` работает; `--limit 0` → exit 2.
  - Формат зафиксирует golden Атома 7.3 (#41) — не менять.
- Атом 6.2 (#39), yt tag list:
  - API уже была: `ListTags(ctx, query, fields, top, skip)` — GET /tags,
    query — фильтр по имени тега, fields `FieldsTagList` = id,name,untagOnResolve.
  - Команда: `tag list`, флаги `-q/--query`, `-l/--limit` (дефолт 50, валидация
    «--limit must be at least 1»), `--json`. `--skip` НЕ определяется (в SPEC
    §3.9 его нет). TTY-таблица NAME/UNTAG ON RESOLVE (false/true); пусто →
    «No tags found»; `--json` — массив Tag (nil → []).
  - Смоук (живой сервер): productivity/tip/Star; `-q Star` фильтрует;
    `-q nonexistent` → «No tags found» exit 0; `--limit 0` → exit 2.
  - Формат зафиксирует golden Атома 7.3 (#41) — не менять.
- Атом 7.2 (#40), pager (internal/output/pager.go):
  - API Printer-а: `Page() bool` (запускает pager, перенаправляет `p.out` в его
    stdin) + `EndPage() error` (закрывает stdin, ждёт процесс, восстанавливает
    stdout). Вызов в TTY-рендерах: `if p.Page() { defer func(){ _ = p.EndPage() }() }`.
  - Условия запуска (§4.3): ModeTTY, без `--verbose`, терминальный stdout,
    `PAGER != cat` (точный «cat», «cat -n» НЕ отключает). Недоступный
    pager-исполняемый (Start-ошибка) → `Page()=false`, фолбэк на прямой вывод.
    epipeWriter глушит EPIPE (ранний выход из pager-а — не ошибка команды).
  - Опции: `WithVerbose(v)` (root.go пробрасывает --verbose), `WithTerminal(t)`
    (тесты pager-а — принудительный признак терминала).
  - Интеграция: страничатся ТОЛЬКО `issue view` (writeIssueViewTTY) и
    `issue comment list` (writeCommentListTTY, только при непустом списке).
    Таблицы (list/search/project/tag) — не страничатся. Условие §4.3 «> 1 экрана»
    делегировано дефолтному `less -FRX` (флаг -F выходит на коротком контенте) —
    отклонение осознанное, зафиксировано в комментарии #40.
  - Golden Атома 7.3 (#41): golden-тесты рендерят в buffer (не-терминал) →
    `Page()` возвращает false, pager не мешает; НО смоук против реального
    терминала (pty) страничит. Рецепт pty-смоука pager-а (stdout bash-инструмента
    — не терминал): `script -qec 'PAGER="/tmp/stub.sh /tmp/out" ./bin/yt issue
    view DEMO-1' /dev/null` — контент сверять в файле stub-а (`/tmp/out`),
    а не в pty-выводе; `PAGER=cat` → контент идёт в pty напрямую.
  - Тесты: запуск через stub-скрипт (пишет stdin в файл), отключение PAGER=cat/
    не-терминал/--verbose/--json/недоступный pager; покрытие output 89.7%.
- Атом 7.3 (#41), golden-тесты (testdata/ + флаг -update):
  - Файл: `internal/commands/golden_test.go`; golden-файлы — `yt/testdata/*.golden`
    (commitятся; корневой .gitignore их НЕ игнорирует).
  - Регенерация: `go test ./internal/commands -run TestGolden -update` (флаг
    `flag.Bool("update", ...)` в тест-файле). Без -update при расхождении —
    подсказка с командой генерации.
  - Хелперы: `runGolden(t, srv, args...)` (isolatedConfig + YT_TOKEN +
    `--base-url srv.URL` при srv != nil, напр. version без API);
    `assertGolden(t, name, got)`; нормализация вывода —
    `normalizeBaseURL` (httptest-URL уникален на запуск) и `normalizeRuntime`
    (go/os/arch) — плейсхолдеры `<base-url>`/`<goversion>`/`<os>`/`<arch>`.
  - Детерминизм обеспечен самим раннером: тесты пишут в strings.Builder →
    `output.IsTerminal`=false → без ANSI/pager. Кейс «длинное описание»
    (issue view) — только как проверка, что контент проходит насквозь;
    pager-смоук живёт отдельно (pty-рецепт #40).
  - Покрытие: все команды рендера × TTY/JSON (list + пустой список,
    search + suggest, view (+минимальный issue, +longdesc, +comments),
    create/edit/close/delete, comment list (+empty)/create, command + assist,
    project/tag list (+empty), auth status, user whoami, version).
  - Входные фикстуры — уже существующие JSON-тела серверов (searchIssuesBody,
    issueViewIssueBody, projectListBody и т.п.), версии timestamp-ов в memory (#37).
  - Проверка качества после правки формата вывода: перегенерить -update,
    просмотреть diff golden-файлов, прогнать гейты (fmt/vet/lint/build/test).
  - Gotcha (первый -update в сессии упал): `assertGolden` пишет через
    `os.WriteFile` БЕЗ `MkdirAll` — каталог `yt/testdata/` должен существовать
    заранее (`mkdir -p testdata`). Не догадываться, а создать сразу.
- Конвенция групп (#38/#39): server-сущности (project/tag) → группа «Сервер»
  (server); issues-команды → «Issues», auth/user → «Основное»,
  version/completion → «Служебное» (SPEC §2.3). Проект/теги не относятся к
  Issues — не совать их в группу issues.
- Атом 8.2 (#43), CI (GitHub Actions) — `.github/workflows/ci.yml` в КОРНЕ репо
  (не в `yt/`), триггеры: push в main + pull_request:
  - Степы: `actions/setup-go@v5` (go-version 1.24.0, `cache-dependency-path:
    yt/go.sum` — для монorepo), `make vet`, golangci-lint-action@v6
    (version v1.64.7 = локальная бинарь, input `working-directory: yt`),
    `make test`, `make build`. Интеграционные тесты (`YT_INTEGRATION=1`) в CI
    НЕ запускаются (SPEC §5.4) — только `make test` без флага.
  - Gotcha (golangci-lint-action): v4+ требует ЯВНЫЙ шаг `actions/setup-go`
    до себя (`skip-go-installation` удалён); `working-directory` — вход v6
    для монorepo. Проверено по README экшена (дорогой факт — не перечитывать).
  - Gotcha (CI, benign): аннотация «Node.js 20 is deprecated ... forced to run
    on Node.js 24» на checkout@v4/setup-go@v5/golangci-lint-action@v6 — это
    warning, НЕ ошибка; пайплайн при этом зелёный, фикс не требуется.
- Проверка после push, затрагивающего CI: `gh run list --workflow=ci.yml`
  (взять id) → `gh run watch <id> --exit-status --interval 20` (блокирует
  до завершения, заканчивается ненулевым кодом при падении).
- Атом 8.5 (#52), дефолтные флаги тестов:
  - `make test` = `go test -cover -bench=. -count=1 -v ./...` — флаги через
    переопределяемую `TESTFLAGS ?= -cover -bench=. -count=1 -v` (Makefile):
    `make test TESTFLAGS="-run X -count=1"` переопределяет полностью.
  - CI (`make test` в ci.yml) флаги получает автоматически, правок workflow не требует.
  - Покрытие на момент 8.5: api 89.2%, commands 87.7%, config 80.9%, output 89.7% —
    все ≥70%. Бенчмарков в пакетах НЕТ (`grep ^func Benchmark` — пусто),
    `-bench=.` их просто не находит.
  - `-count=1` отключает кэш go test — для актуальных цифр покрытия/детерминизма.
- Атом 8.3 (#44), интеграционные тесты (`internal/commands/integration_test.go`):
  - Запуск: `YT_INTEGRATION=1 YT_INTEGRATION_MUTATE=1 PATH="$HOME/sdk/go1.24.0/bin:$PATH" make integration`
    из yt/. Read-only тесты (auth status, whoami, list/view, search, suggest, assist,
    project/tag list) — только `YT_INTEGRATION=1`; мутирующие (create/edit/close/command/
    comment/delete) — + `YT_INTEGRATION_MUTATE=1`, иначе `t.Skip` (SPEC §5.4).
  - YT_TOKEN: брать из окружения; если не задан и владелец дал разрешение — рецепт
    `YT_TOKEN=$(sed -n 's/^token:[[:space:]]*//p' ~/.config/yt/config.yml)` (переменная
    ОБЯЗАНА называться ровно `YT_TOKEN` — в сессии задал `TOKEN=` и тесты скипнулись
    «YT_TOKEN is required», лишний прогон). Токен нигде не печатать; без разрешения
    владельца — спросить.
  - Атомарность /commands (зафиксирована тестом `TestIntegrationCommandAtomicity`):
    batch [валидная, несуществующая] → HTTP 400 «unable to locate an Issue-type entity»,
    валидная НЕ меняется (resolved пуст). Gotcha: «задача уже в запрошенном состоянии»
    ошибки НЕ даёт (идемпотентно) — для проверки атомарности нужен несуществующий id,
    а не закрытая задача.
  - Разрешающее состояние для create/command — динамически через `command assist "state: "`
    (последняя подсказка `description=="State"`); в DEMO — Done, дефолт `state: Fixed` даёт 400.
  - Проект для смоуков — динамически через `project list --json` (первый не-архивированный
    с shortName); резолвинг `-p` по shortName/имени/ring-id подтверждён живьём.
  - Смоук-ишью: уникальный summary (UTC timestamp) + удаление в `t.Cleanup`; после прогона
    проверять отсутствие остатков: `search "project: DEMO" --json -l 100 | jq -r '.[] |
    select(.summary | startswith("yt integration")) | .idReadable'`.
  - Хелперы `runRoot`/`isolatedConfig`/`exitOK` — в pipeline_test.go; для интеграционных
    тестов НЕ перечитывать golden_test.go целиком (формат вывода уже зафиксирован #41).
  - Сверка API: живой сервер localhost:8080 = 2025.3 = снапшот .opencode/openapi.json
    (дата сверки 2026-08-02, финальная — Атом 8.4 #45).
- Атом 8.4 (#45), README + итоговая сверка (закрыт 2026-08-02):
  - README — `yt/README.md` (НЕ корневой: там описание эксперимента). Структура:
    обзор команд, сборка, конфигурация (флаги/env/дефолты), примеры ключевых
    команд, справочник команд с эндпоинтами, формат вывода/exit-коды, pager, интеграция.
  - Gotcha (README): примеры в README — ТОЛЬКО фактический вывод с живого сервера,
    verbatim. Сначала наваял «примерные» create/command (DEMO-49/50) — пришлось
    переделывать на реально снятые DEMO-47/48 (DoD §6.3: совпадают с фактическим
    выводом). Порядок: смоук-захват вывода → вставка в README как есть.
  - Gotcha (конфиг, дефолты): DefaultLogLevel=error, DefaultHTTPTimeout=30s,
    DefaultBaseURL=http://localhost:8080/api (config.go, #45). Не писать дефолты
    по памяти — сверять с config.go, прежде чем класть в доки (написал info/10s —
    перечитывал).
  - `auth login` НЕ дёргает API — только сохраняет конфиг локально (config.Save);
    API-запрос делает только `auth status` (GET /users/me). В таблице эндпоинтов
    это отражать как «локально (конфиг)».
  - Gotcha (сервер): query-парсер DEMO-сервера отклоняет часть стандартного
    синтаксиса 400 invalid_query: `state: #Unresolved` (маппинг `-s open`),
    `state: {To do, In Progress}` — НЕ работают; работают `--project DEMO`,
    `project: DEMO has: State`. Для README/смоуков брать рабочие запросы,
    не спорить с сервером.
  - Итоговая сверка §4.8 (2026-08-02): все 9 используемых эндпоинтов +
    методы/параметры есть в живом openapi.json 2025.3, расхождений нет.
    Используются только `fields`/`query`/`$top`/`$skip`; прочие параметры
    операций (draftId, muteUpdateNotifications) осознанно не используются.
  - Gotcha (make): ВСЕ цели Makefile (`build/test/vet/integration`) требуют PATH
    с Go — `GO ?= go` резолвит go из PATH, без него «make: go: No such file or
    directory». Старая заметка «test/vet работают без PATH» — ложь (проверено).
    Всегда: `PATH="$HOME/sdk/go1.24.0/bin:$PATH" make <target>`.
