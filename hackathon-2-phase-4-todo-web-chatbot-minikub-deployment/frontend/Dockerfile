# Multi-stage Dockerfile for Next.js Frontend
# Optimized for production deployment with static optimization
# Target image size: < 300MB

# =============================================================================
# Stage 1: Dependencies - Install node_modules
# =============================================================================
FROM node:20-alpine AS deps

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install production dependencies only
# Using npm ci for reproducible builds (faster and more reliable than npm install)
RUN npm ci --only=production

# =============================================================================
# Stage 2: Builder - Build Next.js application
# =============================================================================
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install all dependencies (including devDependencies for build)
RUN npm ci

# Copy application source code
COPY . .

# Set environment variable for production build
ENV NODE_ENV=production

# Build Next.js application
# This creates optimized production build in .next/ directory
RUN npm run build

# =============================================================================
# Stage 3: Runtime - Minimal production image
# =============================================================================
FROM node:20-alpine AS runner

# Set working directory
WORKDIR /app

# Set production environment
ENV NODE_ENV=production

# Create non-root user for security
RUN addgroup -g 1001 appuser && \
    adduser -D -u 1001 -G appuser appuser

# Copy necessary files from previous stages
# Only copy what's needed for production runtime
COPY --from=deps --chown=appuser:appuser /app/node_modules ./node_modules
COPY --from=builder --chown=appuser:appuser /app/.next ./.next
COPY --from=builder --chown=appuser:appuser /app/public* ./public
COPY --from=builder --chown=appuser:appuser /app/package.json ./package.json
COPY --from=builder --chown=appuser:appuser /app/next.config.js* ./

# Ensure all files are owned by appuser
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose Next.js port
EXPOSE 3000

# Environment variable for API backend (can be overridden at runtime)
# This will be set by Kubernetes ConfigMap/Deployment
ENV NEXT_PUBLIC_API_URL=http://localhost:8000

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/', (r) => {if (r.statusCode !== 200) throw new Error(r.statusCode)})"

# Start Next.js production server
CMD ["npm", "start"]
