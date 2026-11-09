FROM memos-ab-pilot:20261108
WORKDIR /project/web
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY patches ./patches
RUN pnpm install --frozen-lockfile
WORKDIR /project
