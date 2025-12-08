import React from 'react';
import { Pencil } from 'lucide-react';

const GameCard = ({ game, onEdit, onTogglePlayed }) => {
    const getRatingColor = (value) => {
        if (value === null || value === undefined) return "#333";
        const hue = Math.floor((value / 100) * 120);
        return `hsl(${hue}, 70%, 45%)`;
    };

    const getPlatformIcon = (platform) => {
        const p = platform.toLowerCase();
        let iconSrc = '';

        if (p.includes('steam')) iconSrc = '/logos/steam.png';
        else if (p.includes('epic')) iconSrc = '/logos/epic.png';
        else if (p.includes('gog')) iconSrc = '/logos/gog.png';
        else if (p.includes('amazon')) iconSrc = '/logos/amazon.png';
        else if (p.includes('microsoft')) iconSrc = '/logos/microsoft_logo.png';

        if (iconSrc) {
            return (
                <div key={platform} className="platform-pill">
                    <img src={iconSrc} className="platform-icon" alt={platform} />
                    <span className="platform-name">{platform.toUpperCase()}</span>
                </div>
            );
        }
        return <span key={platform} className="genre-tag">{platform}</span>;
    };

    const displayTitle = game.custom_title || game.title;
    const ratingBg = getRatingColor(game.rating);
    const ratingDisplay = game.rating !== null ? game.rating : "ND";

    return (
        <div className={`game-card ${game.played ? 'played-true' : ''}`}>
            <div
                className="rating-badge"
                style={{ background: ratingBg }}
                onClick={() => onEdit(game)}
            >
                {ratingDisplay}
            </div>

            <div className="game-header">
                <div className="game-title" title={displayTitle}>
                    {displayTitle}
                </div>
            </div>

            <div className="card-meta">
                <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', marginBottom: '10px' }}>
                    {game.platforms.map(p => getPlatformIcon(p))}
                </div>
                <div className="genres-list">
                    {game.genres.slice(0, 3).map(g => (
                        <span key={g} className={`genre-tag ${g === 'Sconosciuto' ? 'sconosciuto' : ''}`}>
                            {g}
                        </span>
                    ))}
                    {game.genres.length > 3 && (
                        <span className="genre-tag">+{game.genres.length - 3}</span>
                    )}
                </div>
            </div>

            <div className="card-footer">
                <div className="played-toggle-wrapper" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <label className="switch">
                        <input
                            type="checkbox"
                            checked={game.played || false}
                            onChange={(e) => onTogglePlayed(game, e.target.checked)}
                        />
                        <span className="slider"></span>
                    </label>
                    <span style={{ fontSize: '0.8rem', color: '#aaa' }}>Played</span>
                </div>

                <button
                    className="action-btn-icon"
                    title="Edit Details"
                    onClick={() => onEdit(game)}
                >
                    <Pencil size={20} />
                </button>
            </div>
        </div>
    );
};

export default GameCard;
