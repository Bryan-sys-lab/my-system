FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
COPY requirements.in .
COPY infra/migrations ./infra/migrations
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENTRYPOINT ["/entrypoint.sh"]
# Use the full module path used by render.yaml and the code
CMD ["celery", "-A", "apps.workers.tasks", "worker", "--loglevel=info"]
