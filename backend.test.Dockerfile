FROM python:3.12-alpine

LABEL version="1.0"
LABEL description="Test-Image für pytest und coverage"

WORKDIR /app

COPY . .

RUN apk update && \
    apk add --no-cache --upgrade bash postgresql-client ffmpeg && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del .build-deps && \
    chmod +x backend.entrypoint.sh

# Wait-for-it Script ins Image kopieren
COPY /scripts/wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Test Entrypoint
COPY backend.test.entrypoint.sh /backend.test.entrypoint.sh
RUN chmod +x /backend.test.entrypoint.sh

ENTRYPOINT ["/backend.test.entrypoint.sh"]