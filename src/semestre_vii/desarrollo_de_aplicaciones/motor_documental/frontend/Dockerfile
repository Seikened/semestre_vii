FROM node:24-bookworm-slim AS construir
RUN npm install -g pnpm@11.22.0
WORKDIR /app
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile --ignore-scripts
COPY . .
RUN pnpm rebuild && pnpm exec nuxt prepare && pnpm build

FROM node:24-bookworm-slim
WORKDIR /app
COPY --from=construir /app/.output ./.output
USER node
EXPOSE 3000
CMD ["node", ".output/server/index.mjs"]
