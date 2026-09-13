FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/

ENV PYTHONPATH=/app/src

EXPOSE 8001 8002

CMD ["python", "-m", "src.space_battle.auth_service.app"]
