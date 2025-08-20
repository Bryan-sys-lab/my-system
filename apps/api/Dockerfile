FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
COPY requirements.in .
COPY infra/migrations ./infra/migrations
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Expose the port the app runs on in render.yaml (10000) and local default
EXPOSE 10000
ENTRYPOINT ["/entrypoint.sh"]
# Use the full python module path so the container and Render startCommand match
CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "10000"]
