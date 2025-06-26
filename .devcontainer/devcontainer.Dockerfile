FROM python:3.12-slim

#Set environment variables for rust
# ENV PATH="$HOME/.cargo/bin:${PATH}"
# ENV RUSTUP_HOME="$HOME/.rustup"
# ENV CARGO_HOME="$HOME/.cargo"

# Install system dependencies
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#     curl \
#     git \
#     libssl-dev \
#     pkg-config \
#     && rm -rf /var/lib/apt/lists/*

# RUN apt-get install -y curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to /usr/local/bin \
# && chmod +x /usr/local/bin/just

# # Install Rust using rustup (safe and up-to-date)
# RUN curl https://sh.rustup.rs -sSf | sh -s -- -y

# # Install garak
# RUN pip install --upgrade pip && \
#     pip install garak

#Set environment variables for rust
# ENV PATH="/root/.cargo/bin:${PATH}"
# ENV RUSTUP_HOME="/root/.rustup"
# ENV CARGO_HOME="/root/.cargo"


RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libssl-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*


RUN curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to /usr/local/bin \
&& chmod +x /usr/local/bin/just


RUN useradd -m -s /bin/bash garakuser
USER garakuser
ENV HOME=/home/garakuser
WORKDIR $HOME

#Set environment variables for rust
ENV PATH="$HOME/.cargo/bin:${PATH}"
ENV RUSTUP_HOME="$HOME/.rustup"
ENV CARGO_HOME="$HOME/.cargo"

# Install Rust using rustup (safe and up-to-date)
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y

# Install garak
RUN pip install --upgrade pip && \
    pip install garak