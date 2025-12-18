# 🚀 Guida Rapida per l'Avvio del Progetto

## Prerequisiti
- Docker e Docker Compose installati
- Porte libere: 5000, 8090, 27019

## Avvio Rapido

### 1. Configurazione Iniziale
```bash
# Copia il file di configurazione di esempio
cp .env.example .env
```

### 2. Avvio con Docker
```bash
# Build e avvio di tutti i servizi
docker-compose up --build

# Per eseguire in background:
docker-compose up -d --build
```

### 3. Accesso all'Applicazione
- **Frontend (UI)**: http://localhost:8090
- **Backend API**: http://localhost:5000
- **MongoDB**: localhost:27019
- **API Docs**: http://localhost:5000/docs

### 4. Comandi Utili
```bash
# Visualizzare i log
docker-compose logs -f

# Fermare i servizi
docker-compose down

# Rimuovere anche i volumi (ATTENZIONE: cancella il database!)
docker-compose down -v

# Riavviare un singolo servizio
docker-compose restart api
```

## Configurazione Porte

### Porte Utilizzate
- **MongoDB**: 27019 (modificata per evitare conflitti con istanze locali)
- **Backend API**: 5000
- **Frontend**: 8090

### Modifica delle Porte
Se necessario modificare le porte, edita il file `docker-compose.yml`:

```yaml
services:
  mongodb:
    ports:
      - "PORTA_ESTERNA:27017"  # Cambia PORTA_ESTERNA
  
  api:
    ports:
      - "PORTA_ESTERNA:5000"   # Cambia PORTA_ESTERNA
  
  frontend:
    ports:
      - "PORTA_ESTERNA:80"     # Cambia PORTA_ESTERNA
```

## File Sensibili e Sicurezza

### ⚠️ File da NON Condividere (già in .gitignore)
1. **Librerie Personali**: `sources/*.json` - contengono i tuoi giochi
2. **Database**: `merged_games.json`, `merged_games.js`
3. **Variabili d'Ambiente**: `.env`, `.env.local`
4. **Volumi Docker**: `mongo_data/`
5. **API Keys**: Se presenti in `.env`

### ✅ File Sicuri da Condividere
- `sources/example_library.json` - file di esempio
- `.env.example` - template senza dati sensibili
- Tutto il codice sorgente (backend, frontend)
- Dockerfile e docker-compose.yml
- README.md e documentazione

## Migrazione Dati

Se hai già un database MongoDB locale, puoi migrarlo:

```bash
# Esporta dal database locale
mongodump --host localhost:27017 --db games_library --out ./backup

# Importa nel container Docker
docker exec -i gameslist_db mongorestore --host localhost:27017 --db games_library /backup/games_library
```

## Troubleshooting

### Errore: Porta già in uso
Se ricevi errori tipo "port already in use":
1. Verifica le porte occupate: `netstat -ano | findstr :PORTA`
2. Modifica le porte in `docker-compose.yml`
3. Riavvia i servizi

### Container non si avvia
```bash
# Pulisci tutto e riprova
docker-compose down -v
docker system prune -a
docker-compose up --build
```

### Problemi di permessi con i volumi
Su Windows, assicurati che Docker Desktop abbia accesso alla cartella del progetto.

## Sviluppo

### Backend (FastAPI)
```bash
# Accedi al container
docker exec -it gameslist_api bash

# Logs in tempo reale
docker-compose logs -f api
```

### Frontend (React + Vite)
```bash
# Accedi al container
docker exec -it gameslist_frontend sh

# Logs in tempo reale
docker-compose logs -f frontend
```

### Database
```bash
# Accedi a MongoDB shell
docker exec -it gameslist_db mongosh

# Dentro mongosh:
use games_library
db.games.find().limit(5)
```

## Backup e Restore

### Backup del Database
```bash
docker exec gameslist_db mongodump --archive=/backup.archive --db games_library
docker cp gameslist_db:/backup.archive ./backup_$(date +%Y%m%d).archive
```

### Restore del Database
```bash
docker cp ./backup.archive gameslist_db:/backup.archive
docker exec gameslist_db mongorestore --archive=/backup.archive --db games_library
```

## Aggiornamento Libreria Giochi

Vedi la sezione "How to Update Your Library" nel [README.md](README.md) per i dettagli completi.
