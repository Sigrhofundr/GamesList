# Deployment Guide - Raspberry Pi

This guide provides step-by-step instructions for deploying updates to your Raspberry Pi production environment.

## Prerequisites

- Raspberry Pi 5 running Raspbian with Docker and Docker Compose installed
- SSH access to the Raspberry Pi
- Git configured on both development PC and Raspberry Pi
- Project repository on GitHub with main branch

## Overview

The deployment process involves:
1. Committing and pushing code changes from your development PC
2. Transferring the updated `merged_games.json` file
3. Pulling code changes on the Raspberry Pi
4. Updating the Docker containers
5. Migrating the database with new data

## Step-by-Step Deployment Process

### 1. On Your Development PC

#### Commit and Push Code Changes
```bash
# Navigate to your project directory
cd D:\dev\gameslist\GamesList

# Check current status
git status

# Add all changes
git add .

# Commit with a descriptive message
git commit -m "Add new features: to-play list, descriptions, release dates"

# Push to main branch
git push origin main
```

#### Transfer merged_games.json to Raspberry Pi
```bash
# Use SCP to transfer the file
# Replace <raspberry-pi-ip> with your actual Raspberry Pi IP address
scp merged_games.json pi@<raspberry-pi-ip>:~/GamesList/
```

**Example:**
```bash
scp merged_games.json pi@192.168.1.100:~/GamesList/
```

### 2. On the Raspberry Pi

#### Connect via SSH
```bash
ssh pi@<raspberry-pi-ip>
```

#### Navigate to Project Directory
```bash
cd ~/GamesList
```

#### Update Code from GitHub
```bash
# Ensure you're on the main branch
git branch

# If not on main, switch to it
git checkout main

# Pull latest changes
git pull origin main
```

**Troubleshooting - Branch Divergence:**
If you see errors about divergent branches or local changes:
```bash
# Reset to match remote main branch exactly
git reset --hard origin/main

# Then pull again
git pull origin main
```

#### Copy merged_games.json into Docker Container
The backend container needs access to `merged_games.json` for database migration:

```bash
# Copy file into the running container
docker cp merged_games.json gameslist_api:/merged_games.json

# Create a symlink so the script can find it
docker exec gameslist_api ln -sf /merged_games.json /app/merged_games.json
```

**Note:** The container name is `gameslist_api` (with underscore), not `gameslist-api`.

#### Rebuild and Restart Docker Containers
```bash
# Stop all containers
docker compose down

# Rebuild containers with no cache (ensures fresh build)
docker compose build --no-cache

# Start containers in detached mode
docker compose up -d
```

**Alternative (if only frontend changed):**
```bash
# Rebuild only frontend
docker compose build --no-cache gameslist_frontend
docker compose up -d
```

#### Migrate Database
After containers are running, migrate the JSON data to MongoDB:

```bash
# Run migration script inside the container
docker exec -it gameslist_api python migrate_to_mongo.py
```

**Expected output:**
```
Connected to MongoDB successfully!
Dropped existing collection: games
Migration complete: Inserted XXXX games
```

#### Verify Deployment
```bash
# Check container status
docker ps

# Check backend logs
docker logs gameslist_api

# Check frontend logs
docker logs gameslist_frontend

# Test API endpoint
curl http://localhost:5000/games | head -20

# Test frontend
curl http://localhost:8090 | head -10
```

All containers should be "Up" and the API should return JSON data.

## Common Issues and Solutions

### Issue: "fatal: refusing to merge unrelated histories"
**Cause:** Local branch has diverged from remote main  
**Solution:**
```bash
git reset --hard origin/main
git pull origin main
```

### Issue: "No such file or directory: '../merged_games.json'"
**Cause:** The migration script looks for the file in the parent directory, but the container only mounts `./backend`  
**Solution:**
```bash
docker cp merged_games.json gameslist_api:/merged_games.json
docker exec gameslist_api ln -sf /merged_games.json /app/merged_games.json
```

### Issue: Frontend doesn't show new features
**Cause:** Frontend container wasn't rebuilt after code changes  
**Solution:**
```bash
docker compose build --no-cache gameslist_frontend
docker compose up -d
```

### Issue: Cannot connect to container "gameslist-api"
**Cause:** Docker Compose uses underscores in container names, not hyphens  
**Solution:** Use `gameslist_api` instead of `gameslist-api`

### Issue: Database migration fails with connection error
**Cause:** MongoDB container isn't running or isn't ready  
**Solution:**
```bash
# Check MongoDB container
docker ps | grep mongo

# Check MongoDB logs
docker logs gameslist-mongo-1

# Wait a few seconds for MongoDB to be ready, then try again
docker exec -it gameslist_api python migrate_to_mongo.py
```

## Quick Reference

### Essential Commands
```bash
# On PC - Push changes
git add . && git commit -m "Update" && git push origin main
scp merged_games.json pi@<ip>:~/GamesList/

# On Raspberry Pi - Deploy
cd ~/GamesList
git pull origin main
docker cp merged_games.json gameslist_api:/merged_games.json
docker exec gameslist_api ln -sf /merged_games.json /app/merged_games.json
docker compose down && docker compose build --no-cache && docker compose up -d
docker exec -it gameslist_api python migrate_to_mongo.py

# Verify
docker ps
curl http://localhost:5000/games | head -20
```

### Container Names
- MongoDB: `gameslist-mongo-1`
- Backend (FastAPI): `gameslist_api`
- Frontend (Nginx): `gameslist_frontend`

### Ports
- MongoDB: `27019`
- Backend API: `5000`
- Frontend: `8090`

## Backup Before Deployment

It's recommended to backup your database before major updates:

```bash
# Export current database to JSON
docker exec -it gameslist_api python -c "
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import json

async def export():
    client = AsyncIOMotorClient('mongodb://mongo:27017')
    db = client['games_db']
    games = await db.games.find().to_list(length=None)
    for game in games:
        game['_id'] = str(game['_id'])
    with open('/backup.json', 'w', encoding='utf-8') as f:
        json.dump(games, f, indent=2, ensure_ascii=False)
    print('Backup complete')

asyncio.run(export())
"

# Copy backup from container to host
docker cp gameslist_api:/backup.json ./backup_$(date +%Y%m%d).json
```

## Rolling Back

If something goes wrong and you need to rollback:

```bash
# Revert to previous git commit
git log --oneline  # Find the commit hash
git reset --hard <previous-commit-hash>

# Rebuild containers with previous code
docker compose down
docker compose build --no-cache
docker compose up -d

# Restore database from backup (if needed)
docker cp backup_YYYYMMDD.json gameslist_api:/backup.json
docker exec -it gameslist_api python migrate_to_mongo.py  # Modify to read from backup.json
```

## Monitoring

### View Live Logs
```bash
# All containers
docker compose logs -f

# Specific container
docker logs -f gameslist_api
docker logs -f gameslist_frontend
```

### Check Resource Usage
```bash
docker stats
```

### Access Container Shell
```bash
# Backend container
docker exec -it gameslist_api bash

# MongoDB shell
docker exec -it gameslist-mongo-1 mongosh
```

## Updating Dependencies

### Backend Dependencies
```bash
# Edit backend/requirements.txt on PC
# Then on Raspberry Pi:
docker compose build --no-cache gameslist_api
docker compose up -d
```

### Frontend Dependencies
```bash
# Edit frontend/package.json on PC
# Then on Raspberry Pi:
docker compose build --no-cache gameslist_frontend
docker compose up -d
```

## Performance Tips

- Use `--no-cache` only when dependencies change; otherwise omit for faster builds
- Keep `merged_games.json` under 10MB for faster transfers
- Run enrichment scripts on PC, not on Raspberry Pi (Steam API calls are slow)
- Consider using `docker system prune` occasionally to free disk space:
  ```bash
  docker system prune -a
  ```

## Security Notes

- Ensure your Raspberry Pi firewall only exposes necessary ports
- Keep SSH keys secure; don't use password authentication
- Regularly update Raspbian and Docker: `sudo apt update && sudo apt upgrade`
- Don't commit sensitive data (API keys, passwords) to the repository
- Use environment variables for configuration (see `docker-compose.yml`)

## Next Steps

After successful deployment, you may want to:
- Set up automated backups (cron job)
- Configure a reverse proxy (Caddy or Traefik) for HTTPS
- Set up monitoring (Portainer, Grafana)
- Create systemd service for auto-start on reboot

For questions or issues, check the main [README.md](README.md) or container logs.
