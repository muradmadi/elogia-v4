# Dokploy Deployment Instructions for Elogia v4

## Overview
Your Elogia v4 application consists of three main services:
1. **Frontend** (Astro static site) - served at `elogia.muradmadi.com`
2. **Backend** (FastAPI) - served at `api.muradmadi.com`
3. **PostgreSQL** - database for the backend
4. **Traefik** - reverse proxy and SSL termination

## Current Issue Analysis
From your logs, the frontend is showing the nginx welcome page because:
- The Docker container is running but the static files may not be properly built/copied
- The nginx configuration is serving the default welcome page instead of your built Astro site

## Updated Docker Configuration
I've updated `docker-compose.yml` to include:

### Key Changes:
1. **Added Traefik service** for routing and SSL
2. **Removed direct port mappings** for frontend/backend (now routed through Traefik)
3. **Updated CORS origins** to use proper internal hostnames
4. **Added SSL/TLS configuration** with Let's Encrypt

## Deployment Steps for Dokploy

### 1. Prepare Your Repository
Ensure your repository contains:
- `docker-compose.yml` (updated version)
- `frontend/Dockerfile` (unchanged)
- `backend/Dockerfile` (unchanged)
- `letsencrypt/` directory (will be created automatically)

### 2. Configure Dokploy
In Dokploy, create a new project with these settings:

#### Environment Variables
Set these environment variables in Dokploy:

| Variable | Value | Description |
|----------|-------|-------------|
| `PUBLIC_API_URL` | `https://api.muradmadi.com` | Frontend API endpoint |
| `DATABASE_URL` | `postgresql+asyncpg://elogia_user:elogia_password@postgres:5432/elogia_db` | Database connection |
| `APP_ENV` | `production` | Application environment |
| `CORS_ORIGINS` | `["https://elogia.muradmadi.com","https://api.muradmadi.com"]` | CORS allowed origins |

#### Domain Configuration
Configure two domains in Dokploy:

1. **Frontend Domain:**
   - Domain: `elogia.muradmadi.com`
   - Service: `frontend`
   - Port: `80`

2. **Backend Domain:**
   - Domain: `api.muradmadi.com`
   - Service: `backend`
   - Port: `8000`

### 3. DNS Configuration
Ensure your DNS records point to Dokploy's server IP:

```
elogia.muradmadi.com  A  →  [Dokploy Server IP]
api.muradmadi.com     A  →  [Dokploy Server IP]
```

### 4. SSL/TLS Setup
Traefik will automatically handle SSL certificates via Let's Encrypt. Ensure:
- Ports 80 and 443 are open on your Dokploy server
- The `letsencrypt` volume is properly mounted
- Email in Traefik configuration is set to your email (`murad@muradmadi.com`)

### 5. Build and Deploy
In Dokploy:
1. Connect your repository
2. Use the updated `docker-compose.yml`
3. Build and deploy all services

## Verification Steps

After deployment, verify:

1. **Frontend is accessible:**
   ```bash
   curl -I https://elogia.muradmadi.com
   ```
   Should return HTTP 200 with your Astro site content.

2. **Backend API is accessible:**
   ```bash
   curl -I https://api.muradmadi.com/health/status
   ```
   Should return HTTP 200.

3. **Check container logs in Dokploy:**
   - Frontend logs should show nginx serving static files
   - Backend logs should show FastAPI startup
   - Traefik logs should show routing configuration

## Troubleshooting

### If frontend still shows nginx welcome page:
1. **Check frontend build:** Ensure the Astro build completed successfully
2. **Verify static files:** Check if files exist in `/usr/share/nginx/html` inside the container
3. **Nginx configuration:** The default nginx config should serve files from that directory

### To debug frontend container:
```bash
# Get into the container
docker exec -it elogia-frontend sh

# Check directory contents
ls -la /usr/share/nginx/html/

# Check nginx config
cat /etc/nginx/nginx.conf
```

### If Traefik shows Docker errors:
The error "Failed to retrieve information of the docker client" indicates Docker socket permission issues. In Dokploy, ensure:
- Traefik has proper access to Docker socket
- The volume mount `/var/run/docker.sock:/var/run/docker.sock:ro` is correctly configured

## Alternative: Simplified Deployment (Without Traefik)

If you prefer Dokploy's built-in routing instead of Traefik:

1. **Revert to original docker-compose.yml** (without Traefik service)
2. **Expose ports directly:**
   - Frontend: port 8080 → 80
   - Backend: port 8000 → 8000
3. **Use Dokploy's reverse proxy** to route domains to these ports

## Support
If issues persist, provide:
1. Updated Dokploy logs
2. Container logs from each service
3. Response from `curl -v https://elogia.muradmadi.com`

The updated configuration should resolve the nginx welcome page issue by ensuring proper routing through Traefik and correct static file serving.