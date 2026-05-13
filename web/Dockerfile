FROM node:20-alpine AS base

# ---- Install deps ----
FROM base AS deps
WORKDIR /app
COPY package.json ./
RUN npm install

# ---- Build ----
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# ---- Run ----
FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/public ./public 2>/dev/null || true
COPY --from=builder /app/next.config.js ./next.config.js
EXPOSE 3000
CMD ["npm", "start"]
