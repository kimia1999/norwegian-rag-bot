
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt


COPY . .


EXPOSE 8000


# use "0.0.0.0" to allow outside access to the container
CMD ["uvicorn", "src.main_api:app", "--host", "0.0.0.0", "--port", "8000"]

