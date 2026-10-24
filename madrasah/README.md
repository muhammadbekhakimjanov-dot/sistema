# Имам Аль-Бухорий медресеси — башкаруу системасы (1–3 этаптар)

Django + PostgreSQL. Бул версияда: логин, 8 роль, колдонуучуларды башкаруу
(кошуу, өзгөртүү, жабуу/ачуу, сырсөз калыбына келтирүү), аракеттер тарыхы
(аудит), responsive интерфейс.

## Орнотуу

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # .env файлын өзүңүздүн маалыматтар менен толтуруңуз
```

## PostgreSQL

```sql
CREATE DATABASE madrasah_db;
CREATE USER madrasah_user WITH PASSWORD 'КүчтүүСырсөз123';
ALTER DATABASE madrasah_db OWNER TO madrasah_user;
```

## Иштетүү

```bash
python manage.py makemigrations accounts core
python manage.py migrate
python manage.py createsuperuser    # башкы администратор
python manage.py runserver
```

Ачуу: http://127.0.0.1:8000/

## Структура

- `config/` — Django жөндөөлөрү (settings.py, urls.py)
- `accounts/` — колдонуучу модели, ролдор, колдонуучуларды башкаруу
- `core/` — аудит журналы, системанын жөндөөлөрү, башкы панель, меню
- `templates/`, `static/` — интерфейс

## Кийинки этаптар

4–5: окуучулар, тайпалар, мугалимдер, кабыл алуу, архив.
