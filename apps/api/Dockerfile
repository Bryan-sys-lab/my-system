FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
COPY requirements.in .
COPY infra/migrations ./infra/migrations
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
