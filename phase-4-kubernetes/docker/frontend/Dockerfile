# [Task]: T010
# [From]: specs/004-phase-iv-kubernetes/spec.md §REQ-001 (Frontend Containerization)
#         specs/004-phase-iv-kubernetes/plan.md §4.1.1 (Frontend Dockerfile Design)

# Multi-Stage Build for Next.js Frontend (Production)
# Target Size: < 200MB
# Base: Node.js 22 Alpine
# Features: Standalone output, non-root user, optimized layers

# ==========================================
# Stage 1: Dependencies
# ==========================================
FROM node:22-alpine AS deps

# Install dependencies only when needed
RUN apk add --no-cache libc6-compat

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install ALL dependencies (including devDependencies needed for build)
RUN npm ci

# ==========================================
# Stage 2: Builder
# ==========================================
FROM node:22-alpine AS builder

WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy application source
COPY . .

# Accept build argument for API URL (for port-forward use http://localhost:8000, for ingress use empty string)
ARG NEXT_PUBLIC_API_URL=http://localhost:8000

# Set environment variables for build
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Build Next.js application with standalone output
# This creates a minimal standalone build in .next/standalone
RUN npm run build

# ==========================================
# Stage 3: Runner (Production)
# ==========================================
FROM node:22-alpine AS runner

WORKDIR /app

# Set to production environment
ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

# Create non-root user for security
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy only necessary files from builder
# Copy standalone output (includes minimal node_modules)
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
# Copy static files
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
# Note: No public directory in this app

# Switch to non-root user
USER nextjs

# Expose port 3000
EXPOSE 3000

# Set hostname to accept connections from any source
ENV HOSTNAME "0.0.0.0"

# Health check (Next.js will serve /api/health endpoint)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/api/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Start Next.js standalone server
CMD ["node", "server.js"]
