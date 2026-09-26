Feature: Проверка skill для GitHub Issues

  Background:
    Given репозиторий определён как OWNER/REPO
    And аутентифицированный gh CLI доступен

  Scenario: Native Related использует REST API как единственный путь
    Given в текущем gh нет отдельного CLI-флага или JSON-поля для native Related
    When пользователь просит связать X с Y
    Then агент проверяет X, Y, репозиторий, номера и URL
    And агент получает numeric ID Y через gh api repos/OWNER/REPO/issues/TARGET
    And агент не использует GraphQL node ID из gh issue view как issue_id
    And агент выполняет POST к repos/OWNER/REPO/issues/ISSUE/relates_to с issue_id=TARGET_ID

  Scenario: Native relation читается с обеих сторон
    Given X уже связан с Y через native Related
    When агент читает relates_to для X и Y
    Then Y присутствует в relates_to X
    And X присутствует в relates_to Y
    And body X и body Y не изменяются
    And отдельная обратная body-ссылка не добавляется

  Scenario: Повторная native-связь не создаётся
    Given X уже связан с Y через native Related
    When пользователь повторно просит связать X с Y
    Then агент сначала читает существующий relates_to X
    And агент не выполняет дублирующий POST

  Scenario: Удаление native relation проверяется адресно
    Given X связан с Y и с другими задачами через native Related
    When пользователь просит удалить только связь X с Y
    Then агент получает numeric ID Y через REST
    And агент выполняет DELETE только для TARGET_ID
    And агент проверяет, что другие связи X не изменились
    And body X и body Y не изменяются

  Scenario: Parent и sub-issue не дублируются другими связями
    Given CHILD является sub-issue PARENT
    When пользователь просит изменить иерархию
    Then агент использует parent или sub-issue
    And агент не добавляет related to только для повторения parent/sub-issue
    And агент не добавляет blocks или blocked by для этой же пары

  Scenario: Явная блокировка используется только для независимых задач
    Given A и B не являются предком и потомком
    When пользователь говорит, что A блокирует B
    Then агент выполняет добавление A blocks B без обратной одновременной связи
    And агент проверяет A в blocking и B в blockedBy
    And агент не подменяет эту связь native Related

  Scenario: Body fallback требует явного согласия
    Given native REST-операция завершилась ошибкой или пользователь явно запросил body-вариант
    When агент рассматривает fallback
    Then агент сообщает о проблеме или запрошенном варианте
    And агент получает согласие перед изменением body
    And агент не выдаёт body fallback за native Related

  Scenario: Согласованный body fallback сохраняет содержимое
    Given пользователь явно согласился на body fallback
    And агент прочитал существующий body X
    When агент добавляет ссылку на Y
    Then агент сохраняет остальной текст и форматирование X
    And агент добавляет ссылку в раздел ## Related только если её ещё нет
    And агент не изменяет body Y
    And агент не копирует содержимое Y в X без необходимости
    And агент не использует в ## Related слова closes, fixes или resolves

  Scenario: Неоднозначный поиск останавливает мутацию
    Given поиск задач возвращает несколько кандидатов или ни одного кандидата
    When пользователь просит изменить задачу
    Then агент запрашивает уточнение до любой мутации
    And агент не меняет issue наугад

  Scenario: Опасные операции требуют явного запроса
    Given пользователь не просил close, reopen, delete, transfer или массовое изменение
    When агент выполняет обычную операцию с GitHub Issues
    Then агент не выполняет эти опасные операции

  Scenario: Контекст репозитория и авторизация проверяются безопасно
    Given агент начинает работу внутри Git-репозитория
    When агент проверяет доступность gh
    Then агент выполняет gh auth status
    And агент получает OWNER/REPO через gh repo view --json nameWithOwner --jq .nameWithOwner
    And агент не выполняет gh auth token

  Scenario: Точная задача читается по номеру или URL
    Given пользователь указал номер или URL issue
    When агент читает задачу
    Then агент использует gh issue view ISSUE --json id,number,title,state,url,labels,parent,subIssues,blockedBy,blocking,body
    And агент не угадывает номер задачи по названию

  Scenario: Существующая задача проверяется до и после изменения
    Given пользователь просит изменить существующую задачу X
    When агент применяет изменение
    Then агент сначала выполняет gh issue view X
    And после успешной команды повторно читает X
    And агент проверяет результат перед сообщением

  Scenario: Ошибка изменения не считается успешной
    Given команда изменения завершилась ошибкой
    When агент проверяет результат
    Then агент указывает ошибку
    And агент не сообщает, что изменение применено

  Scenario: Набор задач для пакетного изменения подтверждается
    Given поиск вернул несколько кандидатов
    When пользователь просит изменить несколько задач без однозначного набора
    Then агент выводит полный список номеров
    And агент запрашивает подтверждение до любой мутации

  Scenario: Новая задача создаётся неинтерактивно и проверяется
    Given пользователь просит создать новую задачу
    When агент создаёт задачу
    Then агент передаёт gh issue create с --title и --body или --body-file
    And агент сохраняет URL новой задачи
    And агент повторно читает NEW_ISSUE

  Scenario: Дочерняя задача создаётся через parent и метки
    Given пользователь просит создать дочернюю задачу для PARENT
    When агент создаёт задачу
    Then агент использует --parent PARENT
    And агент может повторять --label
    And агент не добавляет block-флаг для того же родителя или предка

  Scenario: Независимая блокирующая задача использует blocking
    Given новая задача должна блокировать B
    When агент создаёт задачу
    Then агент использует --blocking B
    And агент не использует --blocked-by для той же пары

  Scenario: Независимая ожидающая задача использует blocked by
    Given новая задача должна ждать B
    When агент создаёт задачу
    Then агент использует --blocked-by B
    And агент не использует --blocking для той же пары

  Scenario: Follow-up создаётся отдельным корнем и получает native related
    Given Y — уже реализованная или закрытая фича
    When пользователь просит создать follow-up X, связанный с Y
    Then агент создаёт X без --parent
    And агент получает numeric ID Y через gh api
    And агент добавляет native related из X в Y отдельным REST-вызовом
    And агент не добавляет blocks, blocked by или body-ссылку
    And агент повторно читает relates_to для X и Y

  Scenario: Parent устанавливается и проверяется с обеих сторон
    Given у задачи CHILD нужно установить или заменить parent
    When агент изменяет иерархию
    Then агент выполняет gh issue edit CHILD --parent PARENT
    And агент проверяет parent и subIssues у CHILD и PARENT

  Scenario: Parent удаляется отдельно
    Given CHILD является sub-issue PARENT
    When пользователь просит удалить parent
    Then агент выполняет gh issue edit CHILD --remove-parent
    And агент не объединяет --remove-parent с --parent
    And агент проверяет обе стороны после изменения

  Scenario: Существующая задача добавляется как sub-issue
    Given PARENT и CHILD являются независимыми задачами
    When пользователь просит добавить CHILD в список sub-issue PARENT
    Then агент выполняет gh issue edit PARENT --add-sub-issue CHILD
    And агент проверяет обе стороны после изменения

  Scenario: Существующая задача удаляется из sub-issue
    Given CHILD является sub-issue PARENT
    When пользователь просит удалить CHILD из списка sub-issue
    Then агент выполняет gh issue edit PARENT --remove-sub-issue CHILD
    And агент не меняет parent CHILD отдельной операцией
    And агент проверяет обе стороны после изменения

  Scenario: Иерархия задаёт неявную блокировку
    Given CHILD является прямым или косвенным потомком PARENT
    When агент определяет зависимость между ними
    Then агент считает потомок неявным блокером предка
    And агент не добавляет отдельные blocks или blocked by для этой пары

  Scenario: Обратная формулировка blocked by сохраняет направление
    Given пользователь говорит, что B блокирует A
    When агент изменяет зависимость
    Then агент выполняет gh issue edit A --add-blocked-by B
    And агент не выполняет --add-blocking B для той же пары
    And агент проверяет B в blocking и A в blockedBy

  Scenario: Явная блокировка удаляется адресно
    Given A блокирует B
    When пользователь просит удалить связь A blocks B
    Then агент выполняет gh issue edit A --remove-blocking B
    And агент не меняет обратную или native related-связь
    And агент проверяет результат у A и B

  Scenario: Обратная блокировка удаляется адресно
    Given A заблокирована задачей B
    When пользователь просит удалить связь A is blocked by B
    Then агент выполняет gh issue edit A --remove-blocked-by B
    And агент не меняет противоположную или native related-связь
    And агент проверяет результат у A и B

  Scenario: Несколько blockers передаются списком
    Given пользователь явно запросил blockers 10 и 11
    When агент добавляет ожидаемые задачи
    Then агент использует --add-blocked-by 10,11
    And агент проверяет результат после изменения

  Scenario: Native related допускает иерархические и sibling targets
    Given Y является root, sibling, предком, потомком или подзадачей X
    When пользователь просит добавить native related с отдельным контекстом
    Then агент использует native REST-связь X к Y
    And агент не добавляет дублирующую parent/sub- или block-связь

  Scenario: Related к связанной паре требует отдельного смысла
    Given X и Y уже имеют parent/sub- или block-связь
    And пользователь хочет сохранить историю, причину, альтернативу или контекст
    When пользователь просит добавить related
    Then агент может добавить native related с этим отдельным смыслом

  Scenario: Native related остаётся отдельной операцией
    Given пользователь просит добавить native related между X и Y
    When агент выполняет связь
    Then агент использует только native REST-операцию
    And агент не объединяет её с parent, blocks, blocked by или body-редактированием
    And агент не добавляет отдельную обратную body-ссылку

  Scenario: Удаление native relation убирает её с обеих сторон
    Given X связан с Y и с другой задачей через native Related
    When пользователь просит удалить только связь X с Y
    Then агент получает numeric ID Y через REST
    And агент выполняет DELETE только для TARGET_ID
    And Y отсутствует в relates_to X
    And X отсутствует в relates_to Y
    And другие связи X и body X и body Y не изменяются

  Scenario: Body fallback меняет только раздел Related
    Given body X содержит заголовок ## related и существующую ссылку
    And пользователь явно согласился на body fallback
    When агент удаляет одну ссылку и добавляет другую
    Then агент находит заголовок ## Related без учёта регистра
    And агент сохраняет остальной текст и форматирование X
    And агент изменяет только записи в разделе ## Related
    And агент удаляет временный файл и повторно читает X
    And агент не изменяет body Y и не добавляет обратную body-ссылку
    And агент не использует в ## Related слова closes, fixes или resolves

  Scenario: Body fallback при создании задачи требует согласия
    Given пользователь явно согласился на body-вариант для новой задачи
    When агент создаёт задачу X
    Then агент добавляет согласованный раздел ## Related в body X
    And агент не выдаёт эту body-ссылку за native Related

  Scenario: Метки проверяются до изменения и могут повторяться
    Given пользователь просит добавить bug и priority: high и удалить obsolete
    When агент изменяет метки задачи X
    Then агент сначала выполняет gh label list --repo OWNER/REPO --limit 100 --json name,description,color
    And агент повторяет --add-label и --remove-label в gh issue edit
    And агент повторно читает метки X

  Scenario: Новая метка создаётся только по явному запросу без force
    Given пользователь явно попросил создать метку LABEL
    When агент создаёт метку
    Then агент выполняет gh label create LABEL с description и color
    And агент не передаёт --force без отдельного согласования

  Scenario: Существующие метки не удаляются и не переименовываются без запроса
    Given пользователь просит изменить метки задачи, но не просит изменить сами метки
    When агент выполняет запрос
    Then агент не удаляет и не переименовывает существующие метки

  Scenario: Неконфликтующие изменения объединяются и проверяются
    Given задаче X нужны независимый blocker, blocked task и изменения меток
    When агент выполняет одно изменение
    Then агент объединяет соответствующие флаги в одном gh issue edit
    And агент не объединяет parent с block-флагом для того же родителя или предка
    And агент не объединяет parent с remove-parent или add/remove одной метки
    And агент изменяет native related отдельным REST-вызовом
    And агент проверяет X и все затронутые задачи

  Scenario: Итоговый отчёт содержит результат проверки
    Given изменение задачи успешно применено и проверено
    When агент формирует ответ пользователю
    Then агент сообщает OWNER/REPO
    And агент сообщает номера и URL изменённых задач
    And агент перечисляет изменённые связи и метки
    And агент указывает неявные зависимости через parent/sub-issue
    And агент сообщает результат проверки

  Scenario: Связи issue читаются как connection-объекты
    Given агент читает задачу с parent, subIssues, blockedBy и blocking
    When агент извлекает данные
    Then агент использует встроенные gh --json и --jq
    And агент не считает эти поля обычными массивами

  Scenario: Работа в worktree использует текущий репозиторий без запроса OWNER/REPO
    Given работа выполняется внутри Git-репозитория с worktree
    When агент определяет контекст
    Then агент использует текущий worktree-репозиторий и не запрашивает MANUAL OWNER/REPO

  Scenario: Добавление native related читает relates_to для предотвращения дубликатов
    Given пользователь просит добавить native related из X в Y
    When агент подготавливает связь
    Then агент сначала выполняет GET к repos/OWNER/REPO/issues/X/relates_to
    And агент добавляет связь только если список не содержит уже существующую задачу

  Scenario: Удаление native relation читает relates_to для поиска TARGET_ID с обеих сторон
    Given пользователь просит удалить связь X с Y через REST
    When агент подготавливает удаление
    Then агент получает numeric ID Y через GET к repos/OWNER/REPO/issues/Y --jq .id
    And агент выполняет DELETE к repos/OWNER/REPO/issues/X/relates_to/TARGET_ID
    And агент не использует номер задачи в месте TARGET_PATH

  Scenario: Заголовок ## Related находится без учёта регистра
    Given body X содержит заголовок с вариантом написания ## related
    And пользователь согласился на body fallback
    When агент ищет раздел Related
    Then агент находит раздел по регистронезависимому паттерну ## related

  Scenario: Временный файл удаляется после body-записи
    Given агент использовал BODY_FILE для записи изменённого body
    When агент завершает редактирование задачи
    Then агент удаляет временный BODY_FILE
    And агент повторно читает задачу через gh issue view --json body
    And тело совпадает с ожидаемым результатом

  Scenario: REST numeric ID используется вместо номера в POST payload
    Given получена ссылка на Y и нужен issue_id для добавления связи
    When агент формирует POST-запрос к repos/OWNER/REPO/issues/X/relates_to
    Then агент передаёт issue_id=TARGET_ID полученный из gh api repos/OWNER/REPO/issues/Y --jq .id
    And агент не передаёт номер задачи в issue_id

  Scenario: Кросс-репозиторная проверка использует целевой OWNER/REPO и номер
    Given Y находится в репозитории OTHER_OWNER/OTHER_REPO
    When агент проверяет target для native related
    Then агент выполняет GET к repos/OTHER_OWNER/OTHER_REPO/issues/Y_NUM --jq .id
    And использует этот numeric ID в POST к целевому репозиторию

  Scenario: Работа с телом существующей задачи читает и не перезаписывает тело целиком
    Given пользователь просит обновить related-ссылку для существующей задачи X
    When агент подготавливает обновление
    Then агент сначала выполняет gh issue view X --json body --jq .body
    And сохраняет оригинальный текст перед добавлением новой записи в ## Related

  Scenario: Создание новой задачи получает numeric ID через REST и не использует номер в issue_id
    Given пользователь создал новую связанную задачу для Y
    When агент добавляет связь из новой задачи к Y
    Then агент получает numeric ID Y из gh api repos/OWNER/REPO/issues/Y_NUM --jq .id
    And передаёт этот ID как issue_id=TARGET_ID в POST-запрос

  Scenario: Убедительный итоговый отчёт при ошибке не утверждает об успехе
    Given изменение завершилось ошибкой с сообщением ERROR_MSG
    When агент формирует ответ
    Then агент сообщает OWNER/REPO и номера задач
    And включает сообщение об ошибке, но не сообщает, что изменение применено успешно

