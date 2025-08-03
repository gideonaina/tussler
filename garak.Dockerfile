FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libssl-dev \
    pkg-config \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# make supervisor’s log dir and hand it off to the unprivileged user
RUN mkdir -p /var/log/supervisor \
 && chown -R nobody:nogroup /var/log/supervisor

RUN useradd -m -s /bin/bash garakuser
ENV HOME=/home/garakuser
ENV PATH="$PATH:/home/garakuser/.local/bin"
WORKDIR $HOME

#Set environment variables for rust
ENV PATH="$HOME/.cargo/bin:${PATH}"
ENV RUSTUP_HOME="$HOME/.rustup"
ENV CARGO_HOME="$HOME/.cargo"

# Install Rust using rustup (safe and up-to-date)
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y


WORKDIR /app

COPY ./tussler_garak/ .
RUN rm -rf src/*.egg-info

RUN pip install --upgrade pip
RUN pip install uv
RUN uv build


# ========================
# Final Stage
# ========================

FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    supervisor \
    && rm -rf /var/lib/apt/lists/*


RUN useradd -m -s /bin/bash garakuser
ENV HOME=/home/garakuser
ENV PATH="$PATH:/home/garakuser/.local/bin"
WORKDIR $HOME

#Set environment variables for rust
ENV PATH="$HOME/.cargo/bin:${PATH}"
ENV RUSTUP_HOME="$HOME/.rustup"
ENV CARGO_HOME="$HOME/.cargo"

# # Install Rust using rustup (safe and up-to-date)
# RUN curl https://sh.rustup.rs -sSf | sh -s -- -y

WORKDIR /app
COPY --from=builder /home/garakuser/.cargo $HOME/.cargo
COPY --from=builder /home/garakuser/.rustup $HOME/.rustup

COPY --from=builder /app/dist /app/dist
RUN chown -R garakuser:garakuser /app/
RUN pip install --upgrade pip
RUN pip install /app/dist/*.whl && rm -Rf /app/dist

RUN mkdir -p /var/log/supervisor \
 && chown -R garakuser:garakuser /var/log/supervisor
COPY ./garak.supervisord.conf /etc/supervisor/supervisord.conf

USER garakuser
EXPOSE 8080 8888

# Use supervisord to manage the application (jupyter and uvicorn API server)
CMD ["supervisord", "-n"]

#=======================================================

# FROM python:3.12-slim

# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#     curl \
#     git \
#     libssl-dev \
#     pkg-config \
#     supervisor \
#     && rm -rf /var/lib/apt/lists/*

# # make supervisor’s log dir and hand it off to the unprivileged user
# RUN mkdir -p /var/log/supervisor \
#  && chown -R nobody:nogroup /var/log/supervisor

# RUN useradd -m -s /bin/bash garakuser
# ENV HOME=/home/garakuser
# ENV PATH="$PATH:/home/garakuser/.local/bin"
# WORKDIR $HOME

# #Set environment variables for rust
# ENV PATH="$HOME/.cargo/bin:${PATH}"
# ENV RUSTUP_HOME="$HOME/.rustup"
# ENV CARGO_HOME="$HOME/.cargo"

# # Install Rust using rustup (safe and up-to-date)
# RUN curl https://sh.rustup.rs -sSf | sh -s -- -y


# WORKDIR /tussler_garak

# COPY ./tussler_garak/ .
# COPY ./garak.supervisord.conf /etc/supervisor/supervisord.conf
# RUN rm -rf src/*.egg-info

# RUN pip install --upgrade pip
# RUN pip install .

# RUN mkdir -p /var/log/supervisor \
#  && chown -R nobody:nogroup /var/log/supervisor

# USER garakuser
# EXPOSE 8080 8888

# # Use supervisord to manage the application (jupyter and uvicorn API server)
# CMD ["supervisord", "-n"]