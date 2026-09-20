# 1. Диаграмма архитектуры
## Общая архитектура системы
![Диаграмма архитектуры](docs/1-common-sys-arch.png)

## Детальная диаграмма взаимодействия микросервисов
![Детальная диаграмма взаимодействия микросервисов](docs/2-detailed-interactions-diagram.png)

## Диаграмма компонентов Game Service
![Диаграмма компонентов Game Service](docs/3-components-diagram.png)


# 2. Детальное описание микросервисов
## 2.1 API Gateway
**Назначение:** Единая точка входа для всех клиентов

**Функциональность:**
- Аутентификация и авторизация
- Маршрутизация запросов
- Ограничения пропускной способности
- Балансировка нагрузки
- Логирование и мониторинг

**Endpoints:**
```
/health - Health check
/auth/login - Вход
/auth/register - Регистрация
/auth/refresh - Обновление токена
/api/users/* - Прокси на User Service
/api/tournaments/* - Прокси на Tournament Service
/api/game/* - Прокси на Game Service
/api/rating/* - Прокси на Rating Service
/api/replay/* - Прокси на Replay Service
/ws/game/* - WebSocket прокси на Game Service
```


## 2.2 User Service
**Назначение:** Управление пользователями

**Функциональность:**
- Регистрация и аутентификация
- Управление профилями
- Хранение пользовательских данных
- Кэширование сессий

**Endpoints:**
```
POST /api/users/register - Регистрация
POST /api/users/login - Вход
GET /api/users/{id} - Получение профиля
PUT /api/users/{id} - Обновление профиля
GET /api/users/{id}/rating - Получение рейтинга
GET /api/users/{id}/history - История игр
```


## 2.3 Tournament Service
**Назначение:** Управление турнирами

**Функциональность:**
- Создание турниров
- Управление заявками
- Расписание турниров
- Отслеживание статуса турниров
- Расчет рейтинга турниров

**Endpoints:**
```
GET /api/tournaments - Список турниров
GET /api/tournaments/upcoming - Будущие турниры
GET /api/tournaments/{id} - Информация о турнире
POST /api/tournaments - Создание турнира
POST /api/tournaments/{id}/apply - Подача заявки
PUT /api/tournaments/{id}/status - Изменение статуса
GET /api/tournaments/{id}/results - Результаты
```

**База данных:** PostgreSQL


## 2.4 Game Service
**Назначение:** Основная игровая логика

**Функциональность:**
- Создание и управление игровыми сессиями
- Обработка команд от агентов
- Выполнение игровой физики
- Управление WebSocket соединениями
- Сохранение состояния игры

**Endpoints:**
```
POST /api/game/create - Создание игры
GET /api/game/{id}/state - Получение состояния игры
POST /api/game/{id}/command - Отправка команды (альтернатива WS)
GET /api/game/{id}/status - Статус игры
DELETE /api/game/{id} - Завершение игры
```

**WebSocket:**
```
/ws/game/{gameId} - Подключение к игре
```

**Компоненты:**
- Game Manager: Создание и управление играми
- Command Queue: Очередь команд с приоритетами
- Command Executor: Исполнение команд
- State Manager: Управление состоянием игры
- Physics Engine: Физика движения
- Collision Detector: Обнаружение столкновений

**База данных:** PostgreSQL + Redis (быстрое состояние)

## 2.5 Rating Service
**Назначение:** Управление рейтингами и статистикой

**Функциональность:**
- Расчет рейтингов
- Обновление статистики
- Таблицы лидеров
- Агрегация данных

**Endpoints:**
```
GET /api/rating/leaderboard - Таблица лидеров
GET /api/rating/users/{id} - Рейтинг пользователя
GET /api/rating/tournaments/{id} - Рейтинг турнира
POST /api/rating/calculate - Расчет рейтингов (внутренний)
```

**База данных:** PostgreSQL + Redis (для leaderboard)


## 2.6 Notification Service
**Назначение:** Отправка уведомлений пользователям

**Функциональность:**
- Email уведомления
- WebSocket уведомления
- Push уведомления
- Очередь уведомлений

**Endpoints:**
```
POST /api/notifications/send - Отправка уведомления
GET /api/notifications/user/{id} - Получение уведомлений
PUT /api/notifications/{id}/read - Отметка как прочитанное
```

**Типы уведомлений:**
- Приглашение на турнир
- Решение по заявке
- Начало боя (за 15 минут)
- Завершение боя
- Обновление рейтинга


# 3. Взаимодействие между микросервисами

## Синхронное взаимодействие (REST)
![Синхронное взаимодействие (REST)](docs/4-rest.png)

## Асинхронное взаимодействие (Message Queue)
![Асинхронное взаимодействие (Message Queue)](docs/5-message-queue.png)


# 4. Сценарии использования

## 4.1 Регистрация и вход пользователя
![Регистрация и вход пользователя](docs/6-register-user.png)

## 4.2 Создание и проведение турнира
![Создание и проведение турнира](docs/7-run-tournament.png)

## 4.3 Игровой процесс (Агент ↔ Game Service)
![Игровой процесс (Агент ↔ Game Service)](docs/8-game-process.png)


# 5. Узкие места и решения

| Компонент	| Проблема | Решение |
|--|--|
| Game Service |	Поддержка тысяч одновременных WebSocket соединений от агентов. Каждое соединение требует памяти и ресурсов CPU. | Connection Pool и балансировка |
| Game Service |	Обработка сотен игр одновременно, каждая с приемлемым FPS, множеством объектов и расчетами физики. | Многопоточность и асинхронность |
| Game Service |	Очередь команд может стать узким местом при высоких нагрузках | Батчинг |


# 6. Компоненты с часто меняющимися требованиями
| Компонент	| Частота изменений |Типичные изменения	| Стратегия OCP |
|--|--|
| Game Service |	Очень высокая |	Физика, столкновения, поведение |	Strategy Pattern |
| Tournament Service |	Высокая |	Форматы, правила расчета |	Strategy Pattern |
| Rating Service |	Средняя |	Алгоритмы расчета	| Strategy Pattern |
| Notification Service |	Высокая |	Типы, каналы доставки |	Factory Pattern |
| API	| Средняя |	Версионирование, форматы |	Versioning |


# 7. Конфигурация

Настройки приложения вынесены в переменные окружения с префиксом `SPACE_BATTLE_`
и/или файл `.env` в корне проекта (см. `.env.example`). Смена конфигурации не
требует правки исходного кода.

| Переменная | Описание | По умолчанию |
|--|--|--|
| `SPACE_BATTLE_SECRET_KEY` | Секретный ключ подписи JWT (одинаковый для обоих сервисов) | дефолтный из кода |
| `SPACE_BATTLE_ALGORITHM` | Алгоритм подписи JWT | `HS256` |
| `SPACE_BATTLE_GAME_SERVICE_HOST` | Хост Game Service | `0.0.0.0` |
| `SPACE_BATTLE_GAME_SERVICE_PORT` | Порт Game Service | `8001` |
| `SPACE_BATTLE_AUTH_SERVICE_HOST` | Хост Auth Service | `0.0.0.0` |
| `SPACE_BATTLE_AUTH_SERVICE_PORT` | Порт Auth Service | `8002` |
| `SPACE_BATTLE_AUTH_SERVICE_URL` | URL Auth Service для исходящих вызовов Game Service | `http://localhost:8002` |
| `SPACE_BATTLE_TOKEN_EXPIRATION_SECONDS` | Срок жизни JWT-токена, секунды | `3600` |
| `SPACE_BATTLE_GAME_TICK_SECONDS` | Длительность тика игры, секунды | `0.05` |

> **ВАЖНО:** в продакшене всегда задавайте свой `SPACE_BATTLE_SECRET_KEY`.

Объект настроек доступен командам движка через IoC-зависимость `"Config"`,
зарегистрированную в прикладном скоупе (`InitializeApplicationScopeAction().execute()`
в `src/space_battle/core/scopes/init_app_scope_action.py`): `Ioc.resolve("Config", Settings)`.


# 8. Запуск в Docker

Оба сервиса (`auth_service` и `game_server`) запускаются через Docker Compose.
Образ собирается из корня проекта с учётом основных пакетов (`src/`).

Требования:
- установленный Docker Engine и Docker Compose v2;
- файл `.env` (скопируйте из `.env.example`).

```bash
# подготовка конфигурации
cp .env.example .env

# собрать и запустить оба сервиса
docker compose up --build

# только auth_service (порт 8002) или только game_server (порт 8001)
docker compose up --build auth_service
docker compose up --build game_server

# остановить сервисы
docker compose down
```

После запуска:
- Auth Service: `POST http://localhost:8002/game`, `POST http://localhost:8002/auth/token`;
- Game Service: `POST http://localhost:8001/api/message`.


# 9. Структурные проблемы сложности проекта и способы их решения

| Компонент | Проблема сложности | Способ решения (паттерн) | Носитель в коде |
|--|--|--|--|
| Ядро (все подсистемы) | Жёсткая связность: компоненты напрямую зависят от конкретных фабрик и команд; добавление новой зависимости задевает много мест и ломает тесты | **Inversion of Control** — все зависимости резолвятся по имени через контейнер; стратегию разрешения можно переопределять и расширять | `src/space_battle/core/ioc.py` |
| Ядро (все подсистемы) | Глобальное состояние и гонки при многопоточности: у каждого потока (сервера, игр) свои регистрируемые зависимости, которые конфликтуют между собой | **Scope + ThreadScope**: зависимые переменные привязаны к скоупу, родительская цепочка скоупов (Scope.Parent), поиск по цепочке | `src/space_battle/core/scopes/dependency_resolver.py`, `src/space_battle/core/scopes/locking.py`, `src/space_battle/core/scopes/thread_scope_context.py` |
| Способности объектов (Movable/Rotatable/Fuelable/Destroyable) |Рост числа статических адаптеров: для каждой новой способности и каждого свойства необходимо писать адаптер + фабрику вручную | **Adapter + динамическая генерация адаптеров**: адаптер и фабрика создаются из ABC-интерфейса на лету через метаклассы и `type()` | `src/space_battle/core/adapters/dynamic_adapter_factory.py` |
| Способности объектов | Объект может «потерять» способность в рантайме; обращение к потерянной способности даёт невнятную ошибку | **Capability guard**: проверка способностей перед каждым обращением через адаптер, понятное исключение | `src/space_battle/core/adapters/dynamic_adapter_factory.py` (`_assert_capability`), `src/space_battle/core/exceptions/exceptions.py` |
| Обработка команд / исключения | Одинаковая логика «повторить», «повторить после логирования» рассредоточена по коду и дублируется | **Strategy + Exception Handler**: обработчик исключений регистрируется в IoC, стратегия «повторить N раз и залогировать» переключается без изменения команд | `src/space_battle/core/exceptions/exception_handler_strategy.py` |
| Цикл обработки команд (Actions Loop) | Разное поведение цикла в разные моменты: в движении к цели, в обычном режиме, при остановке; смешение логики → «if/elif» | **State**: поведение цикла вынесено в конечный автомат состояний (NormalState/MoveToState), команды переключения состояний | `src/space_battle/core/actions/states/*`, `src/space_battle/core/actions/actions_loop.py` |
| Серверный поток (Server Thread) | Тяжёлый по требованиям компонент: мягкая/жёсткая остановка, баланс между внешними сообщениями и существующими играми | **Command + Behaviour/стратегии**: поведение цикла (`behaviour`/`before`/`after`) подменяется динамически (SoftStop/UseScheduler), команды как данные | `src/space_battle/core/server/server_thread.py`, `src/space_battle/core/server/actions.py` |
| Приём действий от агентов | Каждое новое действие агента требует отдельной ветки «найди объект → проверь права → сформируй команду» | **Command + Interpreter + IoC**: единая команда-интерпретатор, которая по `action_id` через IoC резолвит команду и оборачивает её в GuardAction (проверка прав). DSL - не сделано. | `src/space_battle/core/server/interpret_action.py`, `src/space_battle/core/server/game_router.py` |
| Инициализация игры | Ручная инициализация из JSON-конфига непрозрачна: парсинг значений, регистрация фабрик, разбор типов размазаны по коду | **Interpreter + IoC-фабрики**: value-парсер + интерпретирующая команда инициализации + регистрация фабрик объектов через контейнер. DSL - не сделано. | `src/space_battle/core/init/game_init_loader.py`, `src/space_battle/core/init/game_init_value_parser.py`, `src/space_battle/core/init/game_init_interpreter_action.py`, `src/space_battle/core/init/init_object_factories.py` |
| Игровой объект | Единый объект сочетает разные «способности» с разным жизненным циклом; прямое наследование раздувает иерархию классов | **Interfaces + Composition**: базовый объект хранит свойства в едином хранилище, способности — отдельные интерфейсы, поведение подключается адаптерами | `src/space_battle/core/objects/game_object_base.py`, `src/space_battle/core/objects/capabilities/*` |


# 10. Вычислительные проблемы сложности и способы их решения

| Компонент | Вычислительная проблема | Алгоритмическая сложность | Способ решения | Носитель в коде |
|--|--|--|--|--|
| Игровой тик (Game Loop) | Покадровый цикл `while (current_time + tick > perf_counter())` — busy-wait: CPU тратится даже при пустой очереди команд; планировщик выполняет игры строго по одному тику за раз | O(G × N) за цикл планировщика: G — число игр, N — команд в очереди игры | Бюджет времени на тик; `sleep` до следующего тика вместо занятого ожидания; обработка по событиям; батчинг команд за тик | `src/space_battle/core/actions/game_actions.py` |
| IoC-контейнер в "горячем цикле" | Каждый вызов команды и каждое обращение к свойству через адаптер резолвит зависимость по имени: обход родительской цепочки скоупов под блокировкой | O(D) на резолв: D — глубина цепочки скоупов; плюс накладные расходы на лок | Кэширование резолва на скоуп/тик; «прямые» ссылки на горячие зависимости | `src/space_battle/core/ioc.py`, `src/space_battle/core/scopes/dependency_resolver.py` |
| Динамические адаптеры | Генерация класса адаптера через `type()` и обход MRO (Method Resolution Order) выполняется при каждом создании фабрики | O(M × P) на генерацию: M — длина MRO, P — число методов/свойств интерфейса | Кэшировать сгенерированные адаптеры и фабрики по типу интерфейса (один раз на тип) | `src/space_battle/core/adapters/dynamic_adapter_factory.py` |
| Очередь команд / планировщик | Thread-safe `Queue` блокируется на каждой операции; один игровой поток сериализует обработку всех игр | O(1) на операцию очереди, но деградация от конкуренции: много потоков агентов пишут в один поток игр | Батчинг; приоритизация команд; шардинг игр по потокам; лёгкие (неблокирующие) очереди внутри скоупа игры | `src/space_battle/core/actions/game_actions.py`, `src/space_battle/core/server/server_thread.py` |
| Состояние игры (endpoint `/api/game/state`) | Каждый запрос обходит все объекты и для каждого резолвит адаптеры всех способностей | O(n × C × D): n — объектов, C — способностей, D — глубина скоупа на каждый резолв | Инкрементальные снапшоты; отдавать только изменившиеся объекты; push по WebSocket вместо опроса | `src/space_battle/utils/game_state_reporter.py` |
| Приём действий агентов (REST → очередь) | Каждое сообщение проходит JWT-проверку, парсинг Pydantic, интерпретатор, резолв команды, GuardAction с проверкой прав | O(1) на сообщение, суммарно O(M) при M сообщений/с | Батчинг сообщений; прямая постановка команды в очередь игры в обход REST; приоритетная обработка в тике | `src/space_battle/game_server/routes.py`, `src/space_battle/core/server/interpret_action.py` |
