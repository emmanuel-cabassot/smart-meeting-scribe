# === ÉTAPE 1 : DÉPENDANCES ===
FROM node:22-alpine AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Copie intelligente pour le cache Docker
COPY package.json package-lock.json ./ 
RUN npm ci

# === ÉTAPE 2 : BUILDER ===
FROM node:22-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# On désactive la télémétrie Next.js
ENV NEXT_TELEMETRY_DISABLED 1

# Génération du build de production
RUN npm run build

# === ÉTAPE 3 : RUNNER (PROD) ===
FROM node:22-alpine AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1
ENV PORT 3000

# Création user non-root (Sécurité)
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copie des assets statiques
COPY --from=builder /app/public ./public
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Copie du mode STANDALONE (Le secret de la légèreté)
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
