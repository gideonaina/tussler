FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    pkg-config \
    supervisor \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app

COPY ./tussler_pyrit/ .
COPY ./pyrit.supervisord.conf /etc/supervisor/supervisord.conf
RUN rm -rf src/*.egg-info

RUN pip install --upgrade pip
RUN pip install .

RUN mkdir -p /var/log/supervisor \
 && chown -R nobody:nogroup /var/log/supervisor

RUN useradd -m -s /bin/bash pyrituser
USER pyrituser

EXPOSE 8080 8888

# Use supervisord to manage the application (jupyter and uvicorn API server)
CMD ["supervisord", "-n"]