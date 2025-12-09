import React, { useEffect, useState } from 'react';
import api from '../api';
import { X, Dice5, Calendar, Gamepad2, Star } from 'lucide-react';
import GameCard from './GameCard';

const RandomGameModal = ({ onClose, filters }) => {
    const [game, setGame] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchRandom = async () => {
        setLoading(true);
        setError(null);
        try {
            const params = {};
            if (filters.search) params.search = filters.search;
            if (filters.platform !== 'all') params.platform = filters.platform;
            if (filters.genre !== 'all') params.genre = filters.genre;
            if (filters.played !== 'all') params.played = filters.played === 'true';

            const res = await api.get('/games/random', { params });
            setGame(res.data);
        } catch (err) {
            console.error("Failed to fetch random game", err);
            setError("No games found matching your current filters.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchRandom();
    }, []);

    return (
        <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
            <div className="modal-content" style={{ maxWidth: '500px', textAlign: 'center' }}>
                <button className="close-modal" onClick={onClose}><X /></button>

                <h2 style={{ marginTop: 0, marginBottom: '20px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px' }}>
                    <Dice5 /> Random Pick
                </h2>

                {loading && <div className="loading-spinner">Picking a game...</div>}

                {error && <p className="error-msg">{error}</p>}

                {game && !loading && (
                    <div className="random-result">

                        <div style={{ marginBottom: '20px', textAlign: 'left' }}>
                            <GameCard game={game} onEdit={() => { }} onTogglePlayed={() => { }} readonly={true} />
                        </div>

                        <p style={{ fontSize: '1.2rem', marginBottom: '20px' }}>
                            How about playing <strong>{game.title}</strong>?
                        </p>

                        <div className="modal-actions" style={{ justifyContent: 'center', gap: '15px' }}>
                            <button className="btn-action" onClick={fetchRandom} style={{ background: 'transparent', border: '1px solid #fff' }}>
                                <Dice5 size={18} />
                                <span>Spin Again</span>
                            </button>

                            <button className="btn-action" onClick={onClose} style={{ background: '#ff4785' }}>
                                <Gamepad2 size={18} />
                                <span>Let's Play!</span>
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default RandomGameModal;
