FROM node:24-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends ripgrep \
    && rm -rf /var/lib/apt/lists/* \
    && npm install --global @openai/codex@0.167.0 pnpm@11.0.1
ENV COREPACK_ENABLE_PROJECT_SPEC=0
WORKDIR /project
# Frontend pilot runtime. This image does not validate Go/server/database tests.
