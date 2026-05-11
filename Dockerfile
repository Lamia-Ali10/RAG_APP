FROM python:3.11-slim
WORKDIR /app

COPY req.txt .
RUN pip install --no-cache-dir -r req.txt

COPY connecting_api.py .
COPY secret.env .
COPY Data/ ./Data/
COPY chroma_db/ ./chroma_db/

EXPOSE 5000
CMD ["python","connecting_api.py"]