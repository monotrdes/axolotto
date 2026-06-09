FROM python:3.12-slim

WORKDIR /app

# Copy taskboard files (modular structure)
COPY server.py routes.py db.py agent_runner.py task_lifecycle.py /app/
COPY ai_router.py rate_limiter.py /app/
COPY index.html styles.css app.js favicon.svg /app/
COPY modules/ /app/modules/
COPY agent_logs /app/agent_logs

# No pip dependencies — taskboard uses stdlib only
# Expose port
EXPOSE 8181

# The server runs from /repo context, so we mount the repo at /repo
# and expect to find tasks.db there
WORKDIR /repo

CMD ["python3", "-B", "/app/server.py"]
