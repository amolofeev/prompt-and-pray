# docs/PROGRESS.md — трекер прогресса по этапам #5

Статусы: `✅ закрыт` — задача выполнена (DoD) и закрыта; `🟡 открыт` — в работе/ждёт
закрытия. Декомпозиция и зависимости — [docs/PLAN.md](PLAN.md), обязательные требования —
[docs/SPEC.md](SPEC.md) (rev 1.1), процессные правила (DoR/DoD) — [AGENTS.md](../AGENTS.md).

Обновляется после закрытия каждого этапа/атома: статус, новые решения/отклонения,
находки интеграционных проверок, дата сверки с `openapi.json` (§4.8).

**Последнее обновление:** 2026-08-02 (создание; DoD-закрытие этапа 1 — #7).

## Сводка

| Показатель | Значение |
|---|---|
| Этапы | 2/8 закрыто (3, 1); остальные 6: все атомы закрыты, ждут DoD-закрытия |
| Атомы | 30/30 закрыто (включая #52 — добавлен в этап 8) |
| Покрытие (8.5, #52) | `internal/api` 89.2% · `internal/commands` 87.7% · `internal/config` 80.9% · `internal/output` 89.7% (порог ≥70%) |
| Сверка с openapi.json | 2026-08-02, API 2025.3, расхождений нет |
| Meta-задачи | #47 (этот трекер, закрывается при создании), #46 (закрыт 2026-08-02) |

---

## Фаза A — Фундамент

| Атом | Задача | Статус |
|---|---|---|
| 2.1 | [#17](https://github.com/amolofeev/prompt-and-pray/issues/17) Bootstrap: go.mod, main.go, version, Makefile | ✅ закрыт |
| 1.1 | [#16](https://github.com/amolofeev/prompt-and-pray/issues/16) Пакет `internal/config` | ✅ закрыт |
| 3.1 | [#18](https://github.com/amolofeev/prompt-and-pray/issues/18) Клиент core: transport, таймауты, retry, ошибки | ✅ закрыт |
| 3.2 | [#19](https://github.com/amolofeev/prompt-and-pray/issues/19) `types.go` + `fields.go` | ✅ закрыт |
| 7.1 | [#20](https://github.com/amolofeev/prompt-and-pray/issues/20) Пакет `internal/output` | ✅ закрыт |

## Фаза B — Каркас и API

| Атом | Задача | Статус |
|---|---|---|
| 2.2 | [#21](https://github.com/amolofeev/prompt-and-pray/issues/21) `yt version` + `--version` | ✅ закрыт |
| 2.3 | [#22](https://github.com/amolofeev/prompt-and-pray/issues/22) Cobra root, глобальные флаги, help-группы, completion | ✅ закрыт |
| 3.3 | [#23](https://github.com/amolofeev/prompt-and-pray/issues/23) Обёртки чтения API | ✅ закрыт |
| 3.4 | [#24](https://github.com/amolofeev/prompt-and-pray/issues/24) Тесты на `httptest.Server` | ✅ закрыт |

## Фаза C — Пайплайн и auth

| Атом | Задача | Статус |
|---|---|---|
| 2.4 | [#25](https://github.com/amolofeev/prompt-and-pray/issues/25) Пайплайн, ошибки/exit-коды, логирование | ✅ закрыт |
| 1.2 | [#26](https://github.com/amolofeev/prompt-and-pray/issues/26) `auth login/logout/status`, `user whoami` | ✅ закрыт |

## Фаза D — Команды

| Атом | Задача | Статус |
|---|---|---|
| 4.1 | [#27](https://github.com/amolofeev/prompt-and-pray/issues/27) `yt issue list` | ✅ закрыт |
| 4.2 | [#28](https://github.com/amolofeev/prompt-and-pray/issues/28) `yt issue view` | ✅ закрыт |
| 4.3 | [#29](https://github.com/amolofeev/prompt-and-pray/issues/29) `yt issue create` | ✅ закрыт |
| 4.4 | [#30](https://github.com/amolofeev/prompt-and-pray/issues/30) `yt issue edit` | ✅ закрыт |
| 4.5 | [#31](https://github.com/amolofeev/prompt-and-pray/issues/31) `yt issue close` | ✅ закрыт |
| 4.6 | [#32](https://github.com/amolofeev/prompt-and-pray/issues/32) `yt issue delete` | ✅ закрыт |
| 5.1 | [#33](https://github.com/amolofeev/prompt-and-pray/issues/33) `yt issue comment list/create` | ✅ закрыт |
| 5.2 | [#37](https://github.com/amolofeev/prompt-and-pray/issues/37) `yt search` | ✅ закрыт |
| 5.3 | [#34](https://github.com/amolofeev/prompt-and-pray/issues/34) `yt search suggest` | ✅ закрыт |
| 5.4 | [#35](https://github.com/amolofeev/prompt-and-pray/issues/35) `yt command` | ✅ закрыт |
| 5.5 | [#36](https://github.com/amolofeev/prompt-and-pray/issues/36) `yt command assist` | ✅ закрыт |
| 6.1 | [#38](https://github.com/amolofeev/prompt-and-pray/issues/38) `yt project list` | ✅ закрыт |
| 6.2 | [#39](https://github.com/amolofeev/prompt-and-pray/issues/39) `yt tag list` | ✅ закрыт |

## Фаза E — Вывод и полировка

| Атом | Задача | Статус |
|---|---|---|
| 7.2 | [#40](https://github.com/amolofeev/prompt-and-pray/issues/40) Pager | ✅ закрыт |
| 7.3 | [#41](https://github.com/amolofeev/prompt-and-pray/issues/41) Golden-тесты вывода | ✅ закрыт |
| 8.1 | [#42](https://github.com/amolofeev/prompt-and-pray/issues/42) Статанализ: fmt/vet/lint/tidy | ✅ закрыт |
| 8.2 | [#43](https://github.com/amolofeev/prompt-and-pray/issues/43) CI (GitHub Actions) | ✅ закрыт |
| 8.3 | [#44](https://github.com/amolofeev/prompt-and-pray/issues/44) Интеграционные тесты | ✅ закрыт |
| 8.4 | [#45](https://github.com/amolofeev/prompt-and-pray/issues/45) README + сверка с API | ✅ закрыт |
| 8.5 | [#52](https://github.com/amolofeev/prompt-and-pray/issues/52) Дефолтные флаги тестов | ✅ закрыт |

## Этапы

| Этап | Задача | Атомы | Статус |
|---|---|---|---|
| 1 | [#7](https://github.com/amolofeev/prompt-and-pray/issues/7) Аутентификация и конфигурация | 1.1–1.2 | ✅ закрыт 2026-08-02 |
| 2 | [#9](https://github.com/amolofeev/prompt-and-pray/issues/9) CLI-каркас | 2.1–2.4 | 🟡 открыт — атомы закрыты, ждёт DoD-закрытия |
| 3 | [#8](https://github.com/amolofeev/prompt-and-pray/issues/8) API-клиент | 3.1–3.4 | 🟡 открыт — атомы закрыты, ждёт DoD-закрытия |
| 4 | [#10](https://github.com/amolofeev/prompt-and-pray/issues/10) Issue-команды | 4.1–4.6 | 🟡 открыт — атомы закрыты, ждёт DoD-закрытия |
| 5 | [#11](https://github.com/amolofeev/prompt-and-pray/issues/11) Комментарии, поиск, командный язык | 5.1–5.5 | 🟡 открыт — атомы закрыты, ждёт DoD-закрытия |
| 6 | [#12](https://github.com/amolofeev/prompt-and-pray/issues/12) Проекты и теги | 6.1–6.2 | 🟡 открыт — атомы закрыты, ждёт DoD-закрытия |
| 7 | [#13](https://github.com/amolofeev/prompt-and-pray/issues/13) Формат вывода | 7.1–7.3 | 🟡 открыт — атомы закрыты, ждёт DoD-закрытия |
| 8 | [#14](https://github.com/amolofeev/prompt-and-pray/issues/14) Полировка | 8.1–8.5 | 🟡 открыт — атомы закрыты, ждёт DoD-закрытия |

---

## Решения и отклонения

Зафиксированные в комментариях задач/памяти агента (источник — комментарии атомов):

| # | Решение/отклонение | Где зафиксировано |
|---|---|---|
| 1 | Порядок этапов — топологический по фазам A–E вместо SPEC §7 (круговая зависимость 1–3); согласовано с владельцем 2026-07-31 | docs/PLAN.md |
| 2 | `$Type` — невалидный Go-идентификатор: поле названо `Type` с json-тегом `"$type"` (SPEC §2.4 ошибалась) | коммит 34f36d9 |
| 3 | `issue delete` НЕ имеет `--json` (SPEC §3.4: ответ «—»); §4.3 запрещает обёртки без явного раздела | #32 |
| 4 | Pager: условие §4.3 «> 1 экран» делегировано дефолтному `less -FRX` (флаг -F выходит на коротком контенте) | #40 |
| 5 | Текст промпта подтверждения `command` в SPEC §3.6 не зафиксирован — решение агента, закреплено тестом | #35 |
| 6 | Форматы TTY search suggest / command assist / command-рендер — решения агента, закреплены golden (#41) | #34, #36, #35 |
| 7 | `auth login` не дёргает API — только сохраняет конфиг локально; API-запрос делает только `auth status` | #45 (README) |
| 8 | Дефолты конфига: log level `error`, timeout `30s`, base URL `http://localhost:8080/api` | #45, config.go |
| 9 | `state: Fixed` (дефолт SPEC §3.4) валиден для стандартного воркфлоу; в проекте DEMO разрешающее состояние — `Done` | #31, #44 |
| 10 | README-примеры — только verbatim-вывод с живого сервера (§6, критерий 3) | #45 |

## Находки интеграционных проверок

Проверки против живого сервера `http://localhost:8080` (integration-тесты #44,
смоуки #31/#35/#45):

- **Атомарность `/commands` подтверждена**: применение одной командой к batch
  `[валидная, несуществующая]` → HTTP 400 (`unable to locate an Issue-type entity`),
  валидная задача НЕ изменяется (resolved пуст). Частичного применения нет.
  Применение к задаче, уже находящейся в запрошенном состоянии, ошибки НЕ даёт
  (идемпотентно) — для проверки атомарности нужен именно несуществующий id.
- **Резолвинг проекта подтверждён**: `-p` по shortName (без учёта регистра),
  полному имени и ring-id — все варианты создают задачу в нужном проекте.
- **Разрешающее состояние** для create/command берётся динамически через
  `command assist "state: "` (в DEMO — `Done`).
- Мутирующие тесты (create/edit/close/command/comment/delete) создают смоук-ишью
  с уникальным summary и удаляют её в `t.Cleanup`; после прогонов остатков нет.
- Смоук-команды без `-y` при pipe-выводе ждут подтверждения: кормить stdin или
  ожидать EOF → `Aborted`, exit 1.

## Сверка с openapi.json (§4.8)

| Дата | Версия API | Результат |
|---|---|---|
| 2026-08-02 | 2025.3 (живой localhost:8080 = снапшот `.opencode/openapi.json`) | расхождений нет |

Проверены все используемые CLI эндпоинты (методы + параметры): `GET/POST
/issues`, `GET/POST/DELETE /issues/{id}`, `GET/POST /issues/{id}/comments`,
`POST /commands`, `POST /commands/assist`, `POST /search/assist`,
`GET /admin/projects`, `GET /tags`, `GET /users/me`. Из query-параметров
используются только `fields`, `query`, `$top`, `$skip`; прочие параметры
операций (draftId, muteUpdateNotifications) осознанно не используются.

---

## Meta-задачи

| Задача | Статус |
|---|---|
| [#47](https://github.com/amolofeev/prompt-and-pray/issues/47) docs/PROGRESS.md — этот трекер | закрывается при создании |
| [#46](https://github.com/amolofeev/prompt-and-pray/issues/46) Workflow интеграционных тестов против живого YouTrack (AGENTS.md) | ✅ закрыт 2026-08-02 |
