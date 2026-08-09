FROM python:3.14.6-slim-trixie

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN addgroup --system app \
    && adduser --system --ingroup app app

COPY requirements.lock.txt .

RUN python -m pip install \
    --no-cache-dir \
    -r requirements.lock.txt

COPY --chown=app:app \
    main.py \
    config.py \
    database.py \
    handlers.py \
    slack_helper.py \
    ./

USER app

CMD ["python", "main.py"]