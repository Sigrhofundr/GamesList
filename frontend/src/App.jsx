import React, { useState, useEffect } from 'react';
import api from './api';
import GameGrid from './components/GameGrid';
import { Pencil, Plus, Dice5, Download, BarChart2 } from 'lucide-react';
import './index.css';

function App() {
    const [games, setGames] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filters, setFilters] = useState({
        search: '',
        platform: 'all',
        genre: 'all',
        played: 'all'
    });
    const [genres, setGenres] = useState([]);
    const [statsOpen, setStatsOpen] = useState(false);

    // Load Games
    const fetchGames = async () => {
        setLoading(true);
        try {
            const params = {};
            if (filters.search) params.search = filters.search;
            if (filters.platform !== 'all') params.platform = filters.platform;
            if (filters.genre !== 'all') params.genre = filters.genre;
            if (filters.played !== 'all') params.played = filters.played === 'true';

            const response = await api.get('/games', { params });
            setGames(response.data);

            // Update genres list from data if needed (or fetch distinct genres from backend)
            // For now, let's derive from current list or a separate endpoint if we implement one.
            // Optimally backend should provide /genres endpoint. 
            // We'll derive locally for simplicity matching old logic.
            const allGenres = new Set();
            response.data.forEach(g => g.genres.forEach(gen => allGenres.add(gen)));
            setGenres(Array.from(allGenres).sort());

        } catch (error) {
            console.error("Error fetching games:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchGames();
    }, [filters]);

    const handleFilterChange = (key, value) => {
        setFilters(prev => ({ ...prev, [key]: value }));
    };

    const togglePlayed = async (game, checked) => {
        try {
            // Optimistic update
            setGames(prev => prev.map(g => g._id === game._id ? { ...g, played: checked } : g));

            await api.put(`/games/${game._id}`, { played: checked });
        } catch (error) {
            console.error("Failed to update status", error);
            fetchGames(); // Revert on error
        }
    };

    const openGameForm = (game) => {
        alert("Edit Modal to be implemented in next step: " + (game ? game.title : "New Game"));
    };

    const pickRandomGame = () => {
        if (games.length === 0) return;
        const random = games[Math.floor(Math.random() * games.length)];
        alert(`You should play: ${random.title}`);
    };

    return (
        <div className="container">
            <header>
                <h1>Game Library</h1>
                <div className="controls">
                    <div className="input-group">
                        <input
                            type="text"
                            placeholder="Search your collection..."
                            value={filters.search}
                            onChange={(e) => handleFilterChange('search', e.target.value)}
                        />
                    </div>

                    <select
                        style={{ flexGrow: 0.5 }}
                        value={filters.platform}
                        onChange={(e) => handleFilterChange('platform', e.target.value)}
                    >
                        <option value="all">All Platforms</option>
                        <option value="Steam">Steam</option>
                        <option value="Amazon">Amazon</option>
                        <option value="Epic">Epic</option>
                        <option value="GOG">GOG</option>
                        <option value="Microsoft">Microsoft</option>
                    </select>

                    <select
                        style={{ flexGrow: 0.5 }}
                        value={filters.genre}
                        onChange={(e) => handleFilterChange('genre', e.target.value)}
                    >
                        <option value="all">All Genres</option>
                        {genres.map(g => <option key={g} value={g}>{g}</option>)}
                    </select>

                    <select
                        style={{ flexGrow: 0.5 }}
                        value={filters.played}
                        onChange={(e) => handleFilterChange('played', e.target.value)}
                    >
                        <option value="all">All Status</option>
                        <option value="true">Played</option>
                        <option value="false">Not Played</option>
                    </select>

                    <button className="btn-action" onClick={pickRandomGame}>
                        <Dice5 size={18} />
                        <span>Random</span>
                    </button>

                    <button className="btn-export">
                        <Download size={18} />
                        <span>Export</span>
                    </button>
                </div>

                <button className="btn-action" style={{ background: 'transparent', border: '1px solid rgba(255,255,255,0.2)', width: '100%', maxWidth: '900px', marginTop: '10px' }}>
                    <BarChart2 size={18} />
                    <span>Statistics</span>
                </button>

                <div className="stats-bar">
                    <span>{games.length} games found</span>
                    <span style={{ fontSize: '0.8rem', opacity: 0.7 }}>Click "Edit" on a card to modify details.</span>
                </div>
            </header>

            <GameGrid
                games={games}
                loading={loading}
                onEdit={openGameForm}
                onTogglePlayed={togglePlayed}
            />

            <button className="fab-btn" title="Add Game" onClick={() => openGameForm(null)}>
                <Plus size={32} />
            </button>
        </div>
    );
}

export default App;
