FROM python:3.13.7-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm

COPY src/ ./src/
COPY data/ ./data/

EXPOSE 8080

CMD ["python", "src/web_app/app.py"]