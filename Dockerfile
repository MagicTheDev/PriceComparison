# ---------- deps ----------
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

# ---------- builder ----------
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# Ensure production build
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# ---------- runner ----------
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1

# Only prod deps
COPY --from=deps /app/node_modules ./node_modules
COPY package*.json ./

# App artifacts
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.js ./next.config.js

COPY --from=builder /app/app ./app
COPY --from=builder /app/components ./components

EXPOSE 3000

# Next will read FASTAPI_URL from compose env
CMD ["npx", "next", "start", "-p", "3000"]