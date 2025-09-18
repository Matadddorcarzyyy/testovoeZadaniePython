# testovoeZadaniePython
тестовое задание пайтон
README.md


Сервис «WB Bad-Reviews Collector»  
Собирает «плохие» отзывы с Wildberries и сохраняет их в PostgreSQL без дублей.


 1. Что умеет
- По артикулу WB забирает **все** отзывы (автоматическая пагинация)  
- Оставляет только те, у которых `rating < заданного` (по умолчанию 3) и возраст не старше `N` дней (по умолчанию 3)  
- Записывает в БД **только новые** отзывы (UPSERT по полю `id`)  
- Разбит на классы: клиент WB, репозиторий, бизнес-сервис  
- Логирует всё на `stdout`, корректно ловит исключения

 2. Быстрый старт (Windows / macOS / Linux)

 2.1. Установить PostgreSQL и Python 3.9+
- PostgreSQL: [https://www.postgresql.org/download/](https://www.postgresql.org/download/)  
- Python: [https://www.python.org/downloads/](https://www.python.org/downloads/)  
- Проверить версии:
  ```bash
  psql --version
  python --version   # ≥ 3.9
  ```

 2.2. Склонировать / распаковать проект
```bash
git clone <url-репо> wb_badreviews   # или просто создайте папку вручную
cd wb_badreviews
```

 2.3. Создать и активировать виртуальное окружение
Windows PowerShell:
```powershell
python -m venv venv
.\venv\Scripts\activate
```
macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```
> Подсказка: в приглашении появится `(venv)`

 2.4. Установить зависимости
```bash
pip install -r requirements.txt
```

 2.5. Создать БД и пользователя PostgreSQL
Зайдите в консоль postgres (пароль спросит сам):
```bash
psql -U postgres
```
Выполнить:
```sql
CREATE DATABASE wb_reviews;
CREATE USER wb WITH PASSWORD 'wb';
GRANT ALL PRIVILEGES ON DATABASE wb_reviews TO wb;
\q
```

 2.6. Настроить переменные окружения
В корне проекта создайте файл `.env` (точка впереди обязательна):
```
DB_DSN=postgresql+psycopg2://wb:wb@localhost:5432/wb_reviews
WB_BASE_URL=https://feedbacks1.wb.ru/feedbacks/v1
LOG_LEVEL=INFO
```
> Если у вас другой пароль/порт – измените строку `DB_DSN`.

 2.7. Первичное создание таблиц
```bash
python -c "from wb_reviews.db import engine, Base; Base.metadata.create_all(engine); print('Таблицы созданы')"
```
> Ошибок быть не должно. Если «FATAL: password» – проверьте `.env`.

 2.8. Запустить сбор
Возьмите любой **артикул** WB (число в URL карточки).  
Пример: зонт с артикулом `138965700`.  
```bash
python -m wb_reviews.main 138965700 --min-rating 3 --days 3
```
Через несколько секунд увидите:
```
2025-09-19 ... | INFO | Articul 138965700: inserted 7 new bad reviews
```
7 отзывов сохранено в таблицу `reviews`.

 2.9. Посмотреть данные
Любым GUI (pgAdmin, DBeaver) подключитесь к `localhost:5432/wb_reviews` – таблица `reviews` уже заполнена.

---

 3. Полный список параметров CLI
```bash
python -m wb_reviews.main <артикул> [--min-rating N] [--days N]
```
- `артикул` – обязательный, целое число > 0  
- `--min-rating` – **максимальный** рейтинг, который считаем плохим (по умолчанию 3)  
- `--days` – глубина просмотра, дней назад (по умолчанию 3)

Примеры:
```bash
# собрать все ≤2 звезды за неделю
python -m wb_reviews.main 123456 --min-rating 2 --days 7
```

---

 4. Структура папок
```
wb_badreviews/
├── wb_reviews/          # Python-пакет
│   ├── __init__.py
│   ├── settings.py      # читает .env
│   ├── models.py        # SQLAlchemy-модели
│   ├── db.py            # engine + SessionLocal
│   ├── clients.py       # WildberriesClient (httpx)
│   ├── repository.py    # ReviewRepository (UPSERT)
│   ├── services.py      # ReviewsCollector (бизнес-логика)
│   └── main.py          # точка входа (argparse)
├── requirements.txt
├── .env                 # ваши локальные настройки
└── README.md            # этот файл
```
 5. Разработчику
 5.1. Логирование
Уровень задаётся переменной `LOG_LEVEL=DEBUG / INFO / WARNING`.  
Всё пишется в `stdout` с метками времени.

 5.2. Смена БД
Достаточно изменить `DB_DSN` – сервис работает с **любой СУБД**, поддерживаемой SQLAlchemy.  
Пример для SQLite (без PostgreSQL):
```bash
DB_DSN=sqlite+aiosqlite:///wb_reviews.db
```

 5.3. Тесты
(опционально) Установите `pytest` и `respx`, далее:
```bash
pytest tests/
```
Тесты мокают Wildberries и проверяют, что только «плохие» отзывы попадают в БД.

 5.4. Асинхронная версия
Замените `create_engine` на `create_async_engine` и используйте `async_sessionmaker` – код уже готов к этому (остаётся лишь добавить `async/await` в `main.py`).

6. Лицензия
Скрипт выдан как тестовое задание – свободно используйте и модифицируйте.
