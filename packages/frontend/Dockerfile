# ── Stage 1: build the React app ───────────────────────────────────────────
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
COPY packages/backend/package.json    ./packages/backend/
COPY packages/frontend/package.json   ./packages/frontend/
COPY packages/mcp-server/package.json ./packages/mcp-server/
RUN npm ci -w packages/frontend --include-workspace-root
COPY packages/frontend ./packages/frontend
RUN npm run build -w packages/frontend

# ── Stage 2: serve with nginx-unprivileged (port 8080, no root required) ───
FROM ghcr.io/nginxinc/nginx-unprivileged:1.27-alpine

COPY packages/frontend/nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=builder /app/packages/frontend/dist /usr/share/nginx/html

ENV BACKEND_HOST=tableschnappi-backend
ENV NGINX_ENVSUBST_TEMPLATE_VARS=BACKEND_HOST

EXPOSE 8080
