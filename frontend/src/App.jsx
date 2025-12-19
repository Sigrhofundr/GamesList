import React, { useState, useEffect } from 'react';
import api from './api';
import GameGrid from './components/GameGrid';
import GameForm from './components/GameForm';
import GameDetailModal from './components/GameDetailModal';
import StatsModal from './components/StatsModal';
import RandomGameModal from './components/RandomGameModal';
import ToPlayList from './components/ToPlayList';
import { Pencil, Plus, Dice5, Download, BarChart2, ListTodo } from 'lucide-react';
import './index.css';

function App() {
    const [games, setGames] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filters, setFilters] = useState({
        search: '',
        platform: 'all',
        genre: 'all',
        played: 'all',
        includeDLC: false  // Hide DLC by default
    });
    const [genres, setGenres] = useState([]);
    const [statsOpen, setStatsOpen] = useState(false);
    const [randomOpen, setRandomOpen] = useState(false);
    const [toPlayOpen, setToPlayOpen] = useState(false);
    const [editingGame, setEditingGame] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [detailGame, setDetailGame] = useState(null);
    const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
    const [totalGames, setTotalGames] = useState(0);

    // Load Games
    const fetchGames = async (isLoadMore = false) => {
        setLoading(true);
        try {
            const params = {
                limit: 100,
                skip: isLoadMore ? games.length : 0
            };

            if (filters.search) params.search = filters.search;
            if (filters.platform !== 'all') params.platform = filters.platform;
            if (filters.genre !== 'all') params.genre = filters.genre;
            if (filters.played !== 'all') params.played = filters.played === 'true';
            params.include_dlc = filters.includeDLC;  // Pass DLC filter to backend

            const response = await api.get('/games', { params });

            // Response structure: { items: [], total: 1000, skip: 0, limit: 100 }
            const newGames = response.data.items;
            
            setTotalGames(response.data.total);

            if (isLoadMore) {
                setGames(prev => [...prev, ...newGames]);
            } else {
                setGames(newGames);
            }

            // Update genres
            const allGenres = new Set();
            if (!isLoadMore) {
                newGames.forEach(g => g.genres.forEach(gen => allGenres.add(gen)));
                setGenres(Array.from(allGenres).sort());
            } else {
                const currentGenres = new Set(genres);
                newGames.forEach(g => g.genres.forEach(gen => currentGenres.add(gen)));
                setGenres(Array.from(currentGenres).sort());
            }

        } catch (error) {
            console.error("Error fetching games:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchGames(false);
    }, [filters]);

    const handleFilterChange = (key, value) => {
        setFilters(prev => ({ ...prev, [key]: value }));
    };

    const togglePlayed = async (game, checked) => {
        try {
            setGames(prev => prev.map(g => g._id === game._id ? { ...g, played: checked } : g));
            await api.put(`/games/${game._id}`, { played: checked });
        } catch (error) {
            console.error("Failed to update status", error);
            fetchGames();
        }
    };

    const openGameForm = (game) => {
        setEditingGame(game);
        setIsModalOpen(true);
    };

    const closeGameForm = () => {
        setEditingGame(null);
        setIsModalOpen(false);
    };

    const openDetailModal = (game) => {
        setDetailGame(game);
        setIsDetailModalOpen(true);
    };

    const closeDetailModal = () => {
        setDetailGame(null);
        setIsDetailModalOpen(false);
    };

    const openEditFromDetail = (game) => {
        closeDetailModal();
        openGameForm(game);
    };

    const handleSaveGame = async (gameData) => {
        try {
            if (editingGame) {
                await api.put(`/games/${editingGame._id}`, gameData);
            } else {
                await api.post('/games', gameData);
            }
            closeGameForm();
            fetchGames(false); // Reload all
        } catch (error) {
            console.error("Failed to save game", error);
            alert("Error saving game");
        }
    };

    const handleDeleteGame = async (game) => {
        if (!window.confirm(`Are you sure you want to delete "${game.title}"?`)) return;

        try {
            await api.delete(`/games/${game._id}`);
            closeGameForm();
            fetchGames(false); // Reload all
        } catch (error) {
            console.error("Failed to delete game", error);
            alert("Error deleting game");
        }
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
                        <option value="EA">EA</option>
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

                    <label style={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        gap: '8px',
                        padding: '8px 12px',
                        background: 'rgba(255,255,255,0.05)',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        transition: 'all 0.2s',
                        border: filters.includeDLC ? '1px solid rgba(100,100,255,0.4)' : '1px solid transparent'
                    }}>
                        <input
                            type="checkbox"
                            checked={filters.includeDLC}
                            onChange={(e) => handleFilterChange('includeDLC', e.target.checked)}
                            style={{ cursor: 'pointer' }}
                        />
                        <span style={{ fontSize: '0.9rem', whiteSpace: 'nowrap' }}>Show DLC</span>
                    </label>

                    <button className="btn-action" onClick={() => setToPlayOpen(true)}>
                        <ListTodo size={18} />
                        <span>To Play</span>
                    </button>

                    <button className="btn-action" onClick={() => setRandomOpen(true)}>
                        <Dice5 size={18} />
                        <span>Random</span>
                    </button>

                    <button className="btn-export">
                        <Download size={18} />
                        <span>Export</span>
                    </button>
                </div>

                <button
                    className="btn-action"
                    onClick={() => setStatsOpen(true)}
                    style={{ background: 'transparent', border: '1px solid rgba(255,255,255,0.2)', width: '100%', maxWidth: '900px', marginTop: '10px' }}
                >
                    <BarChart2 size={18} />
                    <span>Statistics</span>
                </button>

                <div className="stats-bar">
                    <span>Showing {games.length} of {totalGames} games</span>
                    <span style={{ fontSize: '0.8rem', opacity: 0.7 }}>Click "Edit" on a card to modify details.</span>
                </div>
            </header>

            <GameGrid
                games={games}
                loading={loading && games.length === 0}
                onEdit={openGameForm}
                onTogglePlayed={togglePlayed}
                onViewDetails={openDetailModal}
            />

            {games.length < totalGames && (
                <div style={{ display: 'flex', justifyContent: 'center', margin: '30px 0 80px 0' }}>
                    <button
                        className="btn-action"
                        onClick={() => fetchGames(true)}
                        disabled={loading}
                        style={{ minWidth: '200px' }}
                    >
                        {loading ? 'Loading...' : `Load More (${totalGames - games.length} remaining)`}
                    </button>
                </div>
            )}

            <button className="fab-btn" title="Add Game" onClick={() => openGameForm(null)}>
                <Plus size={32} />
            </button>

            {isModalOpen && (
                <GameForm
                    game={editingGame}
                    onClose={closeGameForm}
                    onSave={handleSaveGame}
                    onDelete={handleDeleteGame}
                />
            )}

            {statsOpen && <StatsModal onClose={() => setStatsOpen(false)} />}

            {randomOpen && (
                <RandomGameModal
                    filters={filters}
                    onClose={() => setRandomOpen(false)}
                />
            )}

            {toPlayOpen && (
                <ToPlayList
                    isOpen={toPlayOpen}
                    onClose={() => setToPlayOpen(false)}
                    onUpdate={() => fetchGames(false)}
                />
            )}

            {isDetailModalOpen && (
                <GameDetailModal
                    game={detailGame}
                    onClose={closeDetailModal}
                    onEdit={openEditFromDetail}
                />
            )}
        </div>
    );
}

export default App;
