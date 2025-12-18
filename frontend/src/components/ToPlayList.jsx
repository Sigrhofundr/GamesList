import React, { useState, useEffect } from 'react';
import api from '../api';
import { X, GripVertical, Trash2 } from 'lucide-react';

const ToPlayList = ({ isOpen, onClose, onUpdate }) => {
    const [games, setGames] = useState([]);
    const [loading, setLoading] = useState(true);
    const [draggedIndex, setDraggedIndex] = useState(null);

    useEffect(() => {
        if (isOpen) {
            fetchToPlayGames();
        }
    }, [isOpen]);

    const fetchToPlayGames = async () => {
        setLoading(true);
        try {
            const response = await api.get('/games/to-play');
            setGames(response.data);
        } catch (error) {
            console.error("Error fetching to-play games:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleDragStart = (e, index) => {
        setDraggedIndex(index);
        e.dataTransfer.effectAllowed = 'move';
    };

    const handleDragOver = (e, index) => {
        e.preventDefault();
        if (draggedIndex === null || draggedIndex === index) return;

        const newGames = [...games];
        const draggedGame = newGames[draggedIndex];
        
        newGames.splice(draggedIndex, 1);
        newGames.splice(index, 0, draggedGame);
        
        setGames(newGames);
        setDraggedIndex(index);
    };

    const handleDragEnd = async () => {
        if (draggedIndex === null) return;
        
        // Save new order to backend
        const gameIds = games.map(g => g._id);
        try {
            await api.put('/games/to-play/reorder', gameIds);
            onUpdate && onUpdate();
        } catch (error) {
            console.error("Error reordering games:", error);
            fetchToPlayGames(); // Reload on error
        }
        
        setDraggedIndex(null);
    };

    const handleRemoveFromList = async (game) => {
        try {
            await api.put(`/games/${game._id}/to-play`, false);
            setGames(prev => prev.filter(g => g._id !== game._id));
            onUpdate && onUpdate();
        } catch (error) {
            console.error("Error removing game from to-play list:", error);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content to-play-modal" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>Games To Play</h2>
                    <button className="close-btn" onClick={onClose}>
                        <X size={24} />
                    </button>
                </div>

                <div className="modal-body">
                    {loading ? (
                        <p style={{ textAlign: 'center', padding: '20px' }}>Loading...</p>
                    ) : games.length === 0 ? (
                        <p style={{ textAlign: 'center', padding: '20px', color: '#888' }}>
                            No games in your "to play" list yet.<br />
                            Add games from your library!
                        </p>
                    ) : (
                        <div className="to-play-list">
                            {games.map((game, index) => (
                                <div
                                    key={game._id}
                                    className={`to-play-item ${draggedIndex === index ? 'dragging' : ''}`}
                                    draggable
                                    onDragStart={(e) => handleDragStart(e, index)}
                                    onDragOver={(e) => handleDragOver(e, index)}
                                    onDragEnd={handleDragEnd}
                                >
                                    <div className="drag-handle">
                                        <GripVertical size={20} />
                                    </div>
                                    <div className="to-play-rank">#{index + 1}</div>
                                    <div className="to-play-info">
                                        <div className="to-play-title">{game.custom_title || game.title}</div>
                                        <div className="to-play-platforms">
                                            {game.platforms.map((p, i) => (
                                                <span key={i} className="platform-badge-small">{p}</span>
                                            ))}
                                        </div>
                                    </div>
                                    <button
                                        className="remove-btn"
                                        onClick={() => handleRemoveFromList(game)}
                                        title="Remove from list"
                                    >
                                        <Trash2 size={18} />
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                <div className="modal-footer">
                    <p style={{ fontSize: '0.9rem', color: '#888', margin: 0 }}>
                        Drag and drop games to reorder your list
                    </p>
                </div>
            </div>
        </div>
    );
};

export default ToPlayList;
