# Stage 1: Builder
# Uses Node 22 LTS alpine to build the Astro static site
FROM node:22-alpine AS builder

WORKDIR /app

# Copy package manifest files
COPY package*.json ./

# Clean install dependencies
RUN npm ci

# Copy entire source code including src/pages directory
COPY src ./src
COPY astro.config.mjs .
COPY tsconfig.json .
COPY components.json .
COPY public ./public

# Accept PUBLIC_API_URL as build argument
# This allows Dokploy to inject the API URL at build time
ARG PUBLIC_API_URL=http://localhost:8000
ENV PUBLIC_API_URL=${PUBLIC_API_URL}

# Build the static Astro site
# This creates the dist/ directory with static HTML/CSS/JS
RUN npm run build

# Stage 2: Runtime
# Uses nginx alpine to serve the static site
FROM nginx:alpine

# Copy built static files from builder stage to nginx serving directory
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 80 for HTTP traffic
EXPOSE 80

# Use default nginx configuration
# Files in /usr/share/nginx/html are automatically served as a static site
CMD ["nginx", "-g", "daemon off;"]
