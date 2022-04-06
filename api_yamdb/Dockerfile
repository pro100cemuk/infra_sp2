FROM python:3.7-slim
WORKDIR /api_yamdb
COPY . .
RUN pip3 install -r api_yamdb/requirements.txt --no-cache-dir
CMD ["gunicorn", "api_yamdb.wsgi:application", "--bind", "0:8000"]
