FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_PORT=8501

RUN apt-get update && apt-get install -y --no-install-recommends build-essential curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
COPY requirements-dashboard.txt requirements-dashboard.txt

RUN python -m pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir -r requirements-dashboard.txt

COPY . .

EXPOSE 8501

CMD ["sh", "-c", "python main.py && python -m streamlit run dashboard/app.py --server.address=0.0.0.0 --server.port=8501 --server.headless=true"]
