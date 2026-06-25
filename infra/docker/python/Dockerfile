# ------------------------
# 1. builder stage
# ------------------------
FROM python:3.11.9-slim-bullseye as builder

ARG PROJECT_DIR
ARG PKG="libopencv-dev curl"

WORKDIR /app

# middleware
RUN apt-get update -q && \
    apt-get -y install --no-install-recommends ${PKG} && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Poetry & pip upgrade
RUN pip install --upgrade pip
RUN pip install poetry --no-cache-dir
# virtualenvは無効化
RUN poetry config virtualenvs.create false

# コピーして依存関係だけインストール
COPY ${PROJECT_DIR}/pyproject.toml ./
RUN if [ -f pyproject.toml ]; then poetry install --no-root; fi

# ------------------------
# 2. final stage
# ------------------------
FROM python:3.11.9-slim-bullseye as dev

ARG USER_NAME
ARG GROUP_NAME
ARG UID
ARG GID
ARG WORKDIR

RUN mkdir -p ${WORKDIR}
WORKDIR ${WORKDIR}

ENV TZ=${TZ}
ENV PATH=/home/${USER_NAME}/.local/bin:$PATH

# 任意: ユーザー作成
RUN groupadd -g ${GID} ${GROUP_NAME} && \
    useradd -lm -s /bin/bash -u ${UID} -g ${GID} -G sudo ${USER_NAME} && \
    echo "${USER_NAME}:password" | chpasswd && \
    echo "${USER_NAME} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

COPY --chown=${UID}:${GID} ./infra/docker/python/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod 755 /docker-entrypoint.sh

# copy site-packages only
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

USER ${USER_NAME}

# If you want to just run one command, use below
# ENTRYPOINT [ "/docker-entrypoint.sh" ]_
