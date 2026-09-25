[AI] Evidence контрактной матрицы S4 (#105)

Дата проверки: 2026-09-25.

## Итог

**PASS: 15/15 cases.** Ни один сценарий не изменял #100 и не вызывал writer
операцию трекера. До завершения #105 parent #100 остаётся `OPEN`; успешное
закрытие #105 допустимо, но не заменяет отдельный Delivery DoD и PO-авторизованное
закрытие #100.

Этот документ фиксирует результаты проверки, а не новый нормативный источник
правил. Нормативные правила остаются в `.opencode/skills/harness-workflow/SKILL.md`,
зеркальные контракты — в ролях и `docs/harness-agents.md`.

## Артефакты

- Machine-readable fixtures: `tests/fixtures/harness-contracts.json`.
- Изолированная модель и 15 отдельных test cases: `tests/test_harness_contracts.py`.
- Спецификация: `docs/harness-agents.md`.
- Нормативный workflow: `.opencode/skills/harness-workflow/SKILL.md`.
- Операционный слой трекера: `.opencode/skills/tasks-gh/SKILL.md`.

Fixture использует target `#9001` и полностью in-memory состояние. Root #100
присутствует только как read-only snapshot метаданных; close к нему не применяется.

## Матрица D1–D4, R1–R2, C1–C2, V1–V5, ROOT1–ROOT2

| Case | Изолированный сценарий | Однозначный ожидаемый результат | Факт |
|---|---|---|---|
| D1 | Delivery DoD для parent | evidence и `close|hold` recommendation, `decision_owner: PO`; close-права нет | PASS |
| D2 | свежий DoD `pass`, target OPEN | `recommendation: close`, `state: awaiting_po_closure`, `authorization: pending`, target OPEN, 0 close attempts | PASS |
| D3 | PO-запросы для #9001 | канонический явный запрос допускается; `сделай`, голый `закрой`, другой и несколько target отклоняются; 0 close attempts | PASS |
| D4 | явная авторизация #9001 + свежий DoD `pass` | один simulated close, один `[AI]`-комментарий с детерминированным marker | PASS |
| R1 | каталог ролей и `permission.task` | ровно 10 существующих ролей; `harness-router` не является файлом, subagent или task node; авторизация/close запрещены | PASS |
| R2 | router state machine | `dispatch`, `hold`, `blocked`, `awaiting_po_closure`, `done` различаются и имеют только допустимые next actions | PASS |
| C1 | legacy `route` #100 | `container/action/to/reasoning/acceptance` сохранены; `dod` и `router` аддитивны | PASS |
| C2 | PO-close orchestration | переход вне ролей, повторный DoD, максимум одна writer-операция, marker и `[AI]`-комментарий обязательны | PASS |
| V1 | все листья закрыты, PO-авторизации нет | target остаётся OPEN, close не вызывается | PASS |
| V2 | авторизация есть, свежий DoD `fail` | `hold`, 0 close attempts, 0 комментариев | PASS |
| V3 | авторизация есть, свежий DoD `pass` | `done`, ровно 1 close attempt, 1 `[AI]`-комментарий | PASS |
| V4 | target уже CLOSED и marker существует | `done` без новой операции и без дубля комментария | PASS |
| V5 | попытка close из Delivery | запрещена: recommendation не равна close, close-права нет | PASS |
| ROOT1 | snapshot #100 | `OPEN`, label `meta`, без `atomic`, зависит от #101 и #105 | PASS |
| ROOT2 | DoD root `pass`, но close не подтверждён | `awaiting_po_closure`, `done` не подтверждается | PASS |

## Выполненные проверки

| Проверка | Результат |
|---|---|
| `python3 -B -m unittest discover -s tests -p 'test_*.py' -v` | PASS, 15 tests, 15 OK |
| `python3 -S -B -m unittest discover -s tests -p 'test_*.py' -v` | PASS, 15 tests без PyYAML через минимальный frontmatter fallback |
| `PYTHONPYCACHEPREFIX=/tmp/opencode/issue-105-pycache python3 -m compileall -q tests` | PASS |
| `python3 -B -m tabnanny tests/test_harness_contracts.py` | PASS |
| `git diff --check` | PASS |
| `opencode agent list` | PASS, все 10 проектных ролей загружены, `harness-router` отсутствует |
| `opencode agent list --pure` | PASS, тот же проектный registry без внешних plugins |
| read-only Task smoke через `opencode run --pure --agent build` | PASS, `Developer-Harness Agent` вернул существующий `done/unblocked` YAML |
| read-only `gh issue view` для #100, #104, #105 | PASS; #104 CLOSED, #100/#105 OPEN; writer-вызовов не было |

Проверка также подтвердила:

- strict YAML разбор frontmatter всех 10 ролей;
- точное совпадение `permission.task` с файловым registry и каталогом ролей;
- точное совпадение содержимого fenced `router`-контракта в `harness-workflow`,
  `delivery` и `docs/harness-agents.md`;
- совпадение `closure`-контракта и close-комментария между skill и спецификацией;
- сохранение legacy route/action/to и аддитивность `dod`/`router`;
- отсутствие concrete `gh issue`/`gh pr` команд в body prompt-контрактов и
  текущей спецификации; операционные команды остались в `tasks-gh`.

## Найденные и устранённые расхождения

1. В восьми descriptions во frontmatter ролей двоеточие-пробел внутри значения
   без кавычек делал строгий YAML-разбор неоднозначным, хотя
   `opencode agent list` принимал конфигурацию. Значения заменены на
   эквивалентные YAML-строки в кавычках: `business-analyst`,
   `systems-analyst`, `developer-go`, `developer-harness`, `developer-python`,
   `team-lead-go`, `team-lead-python`, `specificator`.
2. Спецификация `team-lead-meta` дублировала конкретные команды трекера, хотя
   операции должны жить только в `tasks-gh`. Раздел заменён ссылкой на skill.
3. `opencode run --agent developer-harness` не умеет выбирать subagent напрямую и
   переключается на primary agent. Поэтому минимальный read-only probe запущен
   через primary `build`, который вызвал `Developer-Harness Agent` ровно один
   раз. Tracker, edit, commit, push и close в probe не вызывались.

После исправлений повторный полный прогон дал 15/15 PASS. Нерешённых
контрактных расхождений не осталось. Проектного Node/lint/typecheck runner в
репозитории нет; использованы доступные проверки Python standard library и
штатная валидация конфигурации opencode.

## Parent gate

- #100 не изменён и не закрыт.
- До закрытия #105 его `Blocks: #100` сохраняет parent gate в состоянии
  `blocked`.
- После успешного close #105 downstream #100 становится READY только для
  повторного Delivery DoD; при `pass` он переходит в `awaiting_po_closure` и
  остаётся OPEN до отдельного разрешения PO.
