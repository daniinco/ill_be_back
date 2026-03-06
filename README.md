Что бы запустить докер контейнеры и потестить через UI:
    mkdir for_avito_2
    cd for_avito_2
    git init
    git pull https://github.com/daniinco/ill_be_back.git
    python -m venv backend_venv
    source backend_venv/bin/activate

    (backend_venv) (base) daklo@MacBook-Pro-Daniil-2 for_avito_2 % python --version
    Python 3.11.7

    pip install -r requirements.txt

    Тут не все устанавливается, потом доставим нужное

    docker-compose up -d
    pip install yandex-pgmigrate
    pgmigrate migrate \
    -c "postgresql://postgres:postgres@localhost:5432/postgres" \
    -d . \
    -t latest

    pip install asyncpg
    pip install numpy
    pip install scikit-learn
    pip install fastapi
    pip install aiokafka

    pip install uvicorn
    hash -r

    uvicorn main:app --reload --host 0.0.0.0 --port 8000

    новый терминал(можно несколько раз):
    python -m workers.moderation_worker

    и дальше команды через UI

После этого можно ещё запустить тесты:

    pip install pytest
    pip install httpx
    pip install pytest-asyncio
    python -m pytest tests/ -v

Тесты также можно как то запустить поверх postgres не из докера, 
но для этого надо создать юзера postgres с паролем postgres.

Запуск тестов(после подключения к окружению)
cd /Users/daklo/for_backend && python -m pytest tests/ -m "not integration" -v
cd /Users/daklo/for_backend && python -m pytest tests/ -m integration --collect-only