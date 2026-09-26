---
name: github-issues
description: Use when working with GitHub issues through the gh CLI, including creating, searching, editing, labeling, parent/sub-issues, implicit hierarchy dependencies, non-hierarchical blocks, and native or body-based related-to links.
compatibility: Requires an authenticated gh CLI; parent/sub-issue and block operations need a recent gh version, while native related-to uses the GitHub REST API.
---

# GitHub Issues через `gh`

## Назначение

Используй `gh` для работы с GitHub Issues. Не используй веб-интерфейс или ручные HTTP-запросы, если достаточно `gh`. Для native `related to` используй REST endpoint через `gh api`; body-ссылку используй только как согласованный fallback.

Поддерживай следующие операции:

- создание, поиск, просмотр и редактирование задач;
- добавление, удаление и проверка меток;
- установка parent/sub-issue;
- направленные связи `blocks` и `blocked by` для задач вне иерархии;
- native-связи `related to` через GitHub REST API и, при необходимости, body fallback для контекстных, исторических и альтернативных связей между задачами.

## Обязательные правила

1. Перед изменением определи репозиторий. Если команда выполняется внутри worktree, используй текущий репозиторий; иначе попроси `OWNER/REPO` и передавай `--repo OWNER/REPO` во всех командах.
2. Перед мутацией проверь issue командой `gh issue view`. Не угадывай номера по названию.
3. Если поиск дал несколько кандидатов или ни одного, запроси уточнение до изменения данных.
4. Не выполняй `close`, `reopen`, `delete`, `transfer` или массовые изменения без явного запроса пользователя.
5. Не печатай токены и содержимое `gh auth token`. Для проверки авторизации используй `gh auth status`.
6. После каждого изменения повторно читай issue и проверяй результат. Не сообщай об успехе, если команда завершилась с ошибкой.
7. Не подменяй `related to` связью `blocks` или `blocked by`: это разные отношения.
8. Считай parent/sub-issue основной иерархией задач: потомок неявно блокирует своего предка. Не добавляй для такой пары отдельные `blocks` или `blocked by`.
9. Не добавляй `related to` только для повторения parent/sub-issue связи. Если между предком и потомком есть отдельный смысл — история, причина, альтернатива или контекст — related-ссылка допустима.
10. Для follow-up, доработки или продолжения уже реализованной фичи по умолчанию создавай отдельную корневую задачу и ссылайся на исходную задачу через `related to`, если пользователь явно не попросил другую структуру. Целью ссылки может быть любая задача, включая подзадачу.
11. Используй явный `blocks` только когда блокируемая задача не является предком или потомком текущей задачи.
12. Считай `related to` навигационной связью с source-centric смыслом: из X должен быть доступ к Y, чтобы восстановить контекст; не изменяй body Y и не добавляй отдельную обратную body-ссылку автоматически. Native API возвращает relation с обеих сторон, но добавляй её один раз.
13. Сохраняй направление явной блокировки: `A blocks B` равносильно `B is blocked by A`; не добавляй обе команды одновременно, а после изменения проверь обе стороны.
14. Для native `related to` используй REST endpoints `relates_to` через `gh api`; в текущем `gh` отдельного CLI-флага или JSON-поля нет. Не подменяй native-связь блоком, parent-связью или body-ссылкой. Если REST-операция завершилась ошибкой или пользователь явно просит fallback, сначала сообщи об этом и согласуй body-вариант.

## Как выбирать связь

| Ситуация | Что делать |
| --- | --- |
| Задача является частью декомпозиции другой задачи | Установи parent/sub-issue; не добавляй `blocks` или `blocked by`, а `related` — только если есть отдельный контекст |
| Задача блокирует независимую задачу, sibling или другую ветвь | Добавь явный `blocks` |
| Независимая задача должна ждать другую | Добавь явный `blocked by` |
| После завершённой фичи создаётся доработка | Обычно создай новый корень и добавь native `related to` на исходную задачу; если native-связь недоступна или не разрешена, используй body fallback с согласия пользователя |
| Задача ссылается на источник, дубликат, альтернативу или связанный контекст | Добавь native-связь `related to` на эту задачу; target может быть root, sibling, предком, потомком, подзадачей или задачей другой ветки |

Иерархия и явные зависимости могут сосуществовать, если они относятся к разным парам задач. Не добавляй автоматически parent только потому, что задачи связаны, и не добавляй related только потому, что они блокируют друг друга. `related to` можно добавить к иерархической или блокирующей паре, только если он передаёт отдельный смысл.

## Определение репозитория и авторизации

В корне Git-репозитория:

```bash
gh auth status
gh repo view --json nameWithOwner --jq .nameWithOwner
```

Вне репозитория или при работе с другим репозиторием используй явный `--repo`:

```bash
gh issue list --repo OWNER/REPO --state open --limit 30
```

Если `gh` не авторизован, попроси пользователя запустить `gh auth login`. Не начинай интерактивный login вместо пользователя.

## Просмотр и поиск задач

Для точной задачи используй номер или URL:

```bash
gh issue view ISSUE --json id,number,title,state,url,labels,parent,subIssues,blockedBy,blocking,body
```

Для поиска кандидатов:

```bash
gh issue list --state all --search "SEARCH_TEXT" --json id,number,title,state,url,labels,parent,blockedBy,blocking --limit 100
```

Для фильтрации по меткам:

```bash
gh issue list --state all --label "bug" --label "priority: high" --json number,title,state,labels,url
```

Поля `parent`, `subIssues`, `blockedBy` и `blocking` возвращаются GitHub как connection-объекты. Для извлечения данных используй встроенные `--json` и `--jq`, а не предполагай, что это обычные массивы. Поле `id` в `gh issue view/list --json` — GraphQL node ID (`I_...`), а не числовой REST ID; для `issue_id` из native related-to используй `gh api`. Native `related to` обычно не входит в поля `gh issue view --json`; для него используй REST endpoint из раздела `## Related to`.

Перед изменением нескольких задач сначала выведи полный список найденных номеров и попроси подтверждение, если пользователь не указал однозначный набор.

## Создание задачи

Для неинтерактивной работы всегда передавай `--title` и `--body` или `--body-file`. Не запускай `gh issue create` без них, если пользователь не просил интерактивный режим.

Для дочерней задачи используй только parent и метки:

```bash
gh issue create --repo OWNER/REPO \
  --title "TITLE" \
  --body "BODY" \
  --parent PARENT \
  --label "bug" \
  --label "priority: high"
```

Для независимой задачи, которая блокирует другую, добавь только `--blocking`:

```bash
gh issue create --repo OWNER/REPO \
  --title "TITLE" \
  --body "BODY" \
  --blocking BLOCKED
```

Для независимой задачи, которая ждёт другую, добавь только `--blocked-by`:

```bash
gh issue create --repo OWNER/REPO \
  --title "TITLE" \
  --body "BODY" \
  --blocked-by BLOCKER
```

Флаг `--parent` задаёт родителя новой задачи. `--blocked-by` перечисляет независимые задачи, которые блокируют новую задачу. `--blocking` перечисляет независимые задачи, которые блокирует новая задача. Указание `--label` можно повторять. Не объединяй parent с block-флагом для того же родителя или предка. У `gh issue create` нет флага native `related to`; после создания добавь связь отдельным REST-вызовом.

Сохрани URL, напечатанный `gh`, и используй его для последующей проверки:

```bash
gh issue view NEW_ISSUE --json number,title,url,parent,blockedBy,blocking,labels
```

## Parent и sub-issue

Пусть `CHILD` — дочерняя задача, а `PARENT` — её родитель. В рамках этого skill parent/sub-issue — источник неявной зависимости: прямой или косвенный потомок считается блокером своего предка. Не дублируй эту зависимость через `--blocking` или `--blocked-by`. GitHub может не отражать неявную иерархию в поле `blockedBy`; это не повод создавать отдельную block-связь.

Установить или заменить parent:

```bash
gh issue edit CHILD --parent PARENT
```

Удалить parent:

```bash
gh issue edit CHILD --remove-parent
```

Добавить существующую задачу как sub-issue:

```bash
gh issue edit PARENT --add-sub-issue CHILD
```

Удалить существующую задачу из списка sub-issue:

```bash
gh issue edit PARENT --remove-sub-issue CHILD
```

Не используй `--parent` и `--remove-parent` одновременно. У задачи может быть один parent, но у parent может быть несколько sub-issues.

Проверяй обе стороны связи:

```bash
gh issue view CHILD --json number,parent,subIssues
gh issue view PARENT --json number,parent,subIssues
```

## Blocks и blocked by

Явные связи направленные и нужны только для задач, которые не являются предком и потомком в parent/sub-issue иерархии. Если `A` и `B` уже связаны через parent/sub-issue, используй только эту структуру и не добавляй `--blocking` или `--blocked-by`. Для остальных пар:

| Смысл | Команда |
| --- | --- |
| `A` blocks `B` | `gh issue edit A --add-blocking B` |
| `A` is blocked by `B` | `gh issue edit A --add-blocked-by B` |
| убрать `A` blocks `B` | `gh issue edit A --remove-blocking B` |
| убрать `A` is blocked by `B` | `gh issue edit A --remove-blocked-by B` |

Если пользователь говорит «`B` блокирует `A`», выполняй `--add-blocked-by B` на задаче `A`. Не меняй направление молча.

Не добавляй обе противоположные связи (`--add-blocking` и `--add-blocked-by`) для одной пары без отдельного запроса. Не добавляй явную block-связь между родителем, ребёнком или любыми их предками и потомками. Для массовых значений используй список номеров через запятую, например `--add-blocked-by 10,11`.

Проверяй результат с обеих сторон:

```bash
gh issue view A --json number,blockedBy,blocking
gh issue view B --json number,blockedBy,blocking
```

При ожидаемой связи `A` blocks `B` задача `A` должна содержать `B` в `blocking`, а задача `B` — `A` в `blockedBy`.

## Related to

В GitHub web UI есть нативная связь `Related to` рядом с `Parent` и `Blocked by`. Это отдельная структурированная связь, а не body-ссылка, `blocks` или `blocked by`. В текущем `gh` отдельного CLI-флага или JSON-поля для native `related to` нет; этот skill фиксирует REST API через `gh api` как единственный путь.

Для native-связи доступны REST endpoints:

- `GET /repos/OWNER/REPO/issues/ISSUE/relates_to` — получить связанные задачи;
- `POST /repos/OWNER/REPO/issues/ISSUE/relates_to` с `issue_id` — добавить связь;
- `DELETE /repos/OWNER/REPO/issues/ISSUE/relates_to/ISSUE_ID` — удалить связь.

`ISSUE` в пути — номер issue, а `ISSUE_ID` и `issue_id` — числовой database ID, не номер задачи. В текущем `gh` поле `id` из `gh issue view --json` содержит GraphQL node ID (`I_...`), поэтому не передавай его в `issue_id`. Сначала проверь X и Y и получи target ID через REST:

```bash
gh api --header 'Accept: application/vnd.github+json' \
  repos/OWNER/REPO/issues/TARGET \
  --jq '{id,number,title,state,html_url}'
```

Поле `id` в ответе этого запроса — числовой ID, который можно передать в POST как `TARGET_ID`.

Проверить native-связи текущей задачи:

```bash
gh api --header 'Accept: application/vnd.github+json' \
  repos/OWNER/REPO/issues/ISSUE/relates_to \
  --paginate \
  --jq '.[] | {id,number,title,state,url}'
```

Добавить native-связь из X к Y:

```bash
gh api --method POST \
  --header 'Accept: application/vnd.github+json' \
  repos/OWNER/REPO/issues/ISSUE/relates_to \
  -F issue_id=TARGET_ID
```

Удалить native-связь из X к Y:

```bash
gh api --method DELETE \
  --header 'Accept: application/vnd.github+json' \
  repos/OWNER/REPO/issues/ISSUE/relates_to/TARGET_ID
```

После добавления native relation API возвращает связанную задачу при чтении `relates_to` с обеих сторон. Это не требует изменять body Y или создавать отдельную обратную body-ссылку: добавляй native-связь один раз, а source-centric смысл сохраняй в цели операции. Если target находится в другом репозитории, при проверке используй его `OWNER/REPO` и номер.

Используй `related to`, когда текущей задаче X нужна явная ссылка на задачу Y, чтобы при чтении X можно было перейти к Y и восстановить источник, историю, дубликат, альтернативу или дополнительный контекст. Y может быть любой задачей: корневой, sibling, предком, потомком, подзадачей или задачей из другой ветки. Не копируй содержимое Y в X без необходимости и не добавляй related только для повторения parent/sub-issue или block-связи; если link передаёт отдельный смысл, он допустим и внутри иерархии.

Для native related-to:

1. Проверь X и Y, их репозитории, номера, URL и numeric ID.
2. Прочитай существующий `relates_to` для X и не добавляй дубликат.
3. Определи, нужен ли новый корень или пользователь явно просит другую структуру.
4. Добавь только native-связь; не добавляй `--parent`, `--blocking` или `--blocked-by`, если пользователь не запросил эти отношения отдельно.
5. Повторно прочитай `relates_to` для X и Y; при удалении проверь, что удалена только запрошенная связь.
6. Не меняй body Y и не добавляй отдельную обратную body-ссылку без явного запроса.

Если native REST operation недоступна, версия API её не поддерживает или пользователь требует body-ссылку, сначала сообщи об этом и получи согласие на fallback. Не выдавай body fallback за native relation.

Если пользователь явно согласился на body-вариант, добавь в body X раздел `## Related` со ссылкой на target Y; по возможности добавь короткое пояснение, зачем X ссылается на Y. Для follow-up после уже реализованной или закрытой фичи обычно создавай новый корень X без `--parent` и добавляй ссылку на исходную задачу Y; Y может быть и подзадачей.

```markdown
## Related

- [OWNER/REPO#123](https://github.com/OWNER/REPO/issues/123)
```

Для задач одного репозитория можно использовать короткую ссылку:

```markdown
- #123 — причина, по которой X ссылается на Y
```

Примеры контекста:

- `X` — follow-up или регрессия, который ссылается на исходную задачу `Y`, даже если `Y` является подзадачей;
- `X` фиксирует решение или контекст из sibling, предка или потомка `Y`;
- `X` ссылается на дубликат, альтернативу или связанное исследование `Y` в другой ветке;
- `X` может быть parent, который ссылается на отдельную независимую задачу `Y`.

Для изменения существующей задачи:

1. Прочитай её текущее body:
   ```bash
   gh issue view ISSUE --json body --jq .body
   ```
2. Найди существующий заголовок `## Related` с учётом регистра.
3. Сохрани body во временный файл и измени только записи в разделе `## Related`. Остальной текст, форматирование и ссылки не трогай.
4. Добавь ссылку только если её ещё нет. При удалении удаляй только запрошенную ссылку.
5. Запиши body обратно:
   ```bash
   gh issue edit ISSUE --body-file BODY_FILE
   ```
6. Удали временный файл и снова прочитай задачу, чтобы убедиться, что ссылка присутствует.

Обратную body-ссылку в target не добавляй по умолчанию: related-to — навигационная связь из X в Y, а не обязательная синхронизация двух задач. Native API может показывать relation с обеих сторон, но это не требует отдельной body-ссылки. Не используй в `## Related` ключевые слова `closes`, `fixes` или `resolves`: они имеют другую семантику и могут создать неверную связь с pull request.

При создании новой задаки можно сразу добавить `## Related` в переданный body только для согласованного body-варианта. Для существующей задаки не заменяй body целиком без чтения и сохранения остального содержимого. Для native-запроса используй REST endpoint, а body fallback согласуй отдельно.

## Метки

Сначала посмотри существующие метки и не создавай дубликаты:

```bash
gh label list --repo OWNER/REPO --limit 100 --json name,description,color
```

Добавить метки:

```bash
gh issue edit ISSUE --add-label "bug" --add-label "help wanted"
```

Удалить метки:

```bash
gh issue edit ISSUE --remove-label "obsolete" --remove-label "invalid"
```

Добавить метки при создании:

```bash
gh issue create --repo OWNER/REPO --title "TITLE" --body "BODY" --label "bug" --label "priority: high"
```

Не удаляй и не переименовывай метки без явного запроса. Создание новой метки допустимо только по запросу пользователя:

```bash
gh label create "LABEL" --repo OWNER/REPO --description "DESCRIPTION" --color "RRGGBB"
```

Не указывай `--force`, если обновление существующей метки не было явно согласовано.

## Комбинированные операции

Один `gh issue edit` может менять несколько полей, но перед комбинированием проверь, что операции не конфликтуют:

Для независимой связи и меток:

```bash
gh issue edit ISSUE \
  --add-blocked-by BLOCKER \
  --add-blocking BLOCKED \
  --add-label "needs-review" \
  --remove-label "triage"
```

Не объединяй `--parent` с block-флагом для того же родителя или предка. Не объединяй `--parent` с `--remove-parent`, не добавляй и не удаляй одну и ту же метку в одном вызове, и не смешивай операции над разными задачами без явного списка. Native `related to` изменяй отдельным REST-вызовом, а не комбинируй с `gh issue edit` или body-редактированием.

После комбинированной операции проверь issue и все затронутые задачи:

```bash
gh issue view ISSUE --json number,title,state,url,labels,parent,subIssues,blockedBy,blocking
```

## Формат ответа

После выполнения сообщи:

- репозиторий `OWNER/REPO`;
- номера и URL изменённых задач;
- какие parent/sub-issue, явные blocks, blocked by, native related-to или body fallback связи и метки изменились;
- какие зависимости остались неявными через parent/sub-issue иерархию;
- результат проверки.

Если команда завершилась ошибкой, укажи ошибку и не утверждай, что изменение применено.
