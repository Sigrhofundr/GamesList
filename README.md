# Personal Game Library Manager

A versatile game collection manager that can be run in two modes:
1.  **Serverless Web Viewer**: A simple, portable HTML file (Legacy).
2.  **Home Server (Reccomended)**: A robust client-server application (React + FastAPI + MongoDB) designed for local network access (e.g. Raspberry Pi).

## 🚀 Home Server Usage (Docker)

The modern way to run GamesList. It provides a full web interface, persistent database, and API.

### Prerequisites
-   **Docker** and **Docker Compose** installed.

### Quick Start (Local PC & Raspberry Pi)

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/your/repo.git
    cd GamesList
    ```

2.  **Start Services**:
    This will build and launch the Frontend (React), Backend (Python FastAPI), Database (MongoDB), and Proxy (Nginx) automatically.
    ```bash
    docker-compose up -d --build
    ```

3.  **Access the App**:
    Open your browser and navigate to:
    -   **http://localhost:8090** (on Local PC)
    -   **http://<RASPBERRY_IP>:8090** (on Network)

### Data Migration
To import your existing `merged_games.json` into the database:
```bash
# Copy the file into the backend container
docker cp merged_games.json gameslist_api:/app/merged_games.json

# Run the migration script
docker exec -it gameslist_api python migrate_to_mongo.py
```
*(You only need to do this once)*

---

## 🛠 Project Structure (Server Mode)
```
/GamesList
├── backend/                # FastAPI Application (Python)
│   ├── main.py             # API Routes & Logic
│   ├── migrate_to_mongo.py # Migration Script
│   └── Dockerfile
├── frontend/               # React Application (Vite)
│   ├── src/                # React Components
│   └── Dockerfile          # Multi-stage build (Node -> Nginx)
├── nginx/                  # Nginx Configuration
├── docker-compose.yml      # Container Orchestration
└── ... (Legacy scripts)
```

---

## 💻 Development (Local PC)
If you want to modify the code:

**Run Frontend in Dev Mode**:
```bash
cd frontend
npm install
npm run dev
# App runs at http://localhost:5173
```

**Run Backend in Dev Mode**:
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 5000
# API runs at http://localhost:5000
```

---

## 📂 Static/Legacy Mode
*For purely local, file-based usage without Docker.*

### Project Structure
```
/GamesList
├── index.html              # Main application (open this in browser)
├── normalize_games.py      # Script to ingest and merge source JSONs
├── enrich_games.py         # Script to fetch missing genres from Steam
├── merged_games.json       # The master database file (generated)
├── sources/                # Directory for your source library files
└── logos/                  # Directory containing platform images (png)
```

### How to Use
1.  **Configure `.env`**: Define paths to your source JSON files (Amazon, Epic, etc.).
2.  **Run Scripts**:
    ```bash
    python3 normalize_games.py  # Merges JSONs
    python3 enrich_games.py     # Fetches genres from Steam
    ```
3.  **View**: Open `index.html` in your browser.

## Credits & API
-   **Steam API**: Used for fetching game usage data and genre information.
-   **Heroic Games Launcher**: Used for exporting libraries from other platforms.
 
