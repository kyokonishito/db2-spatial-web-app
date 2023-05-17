FROM node:18.16.0-bullseye-slim AS builder

WORKDIR /frontend
COPY frontend .
RUN npm install 
RUN npm run build

#Stage 2
FROM python:3.11-slim-bullseye
RUN apt-get update && apt-get install -y \
    gcc \
    libxml2-dev 
WORKDIR /flaskapp
COPY flaskapp .
RUN pip install -r requirements.txt
COPY --from=builder /frontend/dist ./static

CMD ["python", "app.py"]