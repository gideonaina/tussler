FROM python:3.10-bullseye

# Install dependencies
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     libffi-dev \
#     libssl-dev \
#     python3-dev \
#     python3-pip \
#     git \
#     && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    curl \
    make \
    && rm -rf /var/lib/apt/lists/*

# Install pip
RUN RUN pip install --upgrade pip && pip install garak
