import React from 'react';
import { X, Pencil, Calendar, AlignLeft, Star, Gamepad2, ListChecks } from 'lucide-react';

const GameDetailModal = ({ game, onClose, onEdit }) => {
    if (!game) return null;

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
        else if (p.includes('ea')) iconSrc = '/logos/ea.png';

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

    const formatDate = (dateString) => {
        if (!dateString) return 'Unknown';
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', { 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
            });
        } catch {
            return dateString;
        }
    };

    const displayTitle = game.custom_title || game.title;
    const ratingBg = getRatingColor(game.rating);
    const ratingDisplay = game.rating !== null && game.rating !== undefined ? game.rating : "N/A";

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="detail-modal-content" onClick={(e) => e.stopPropagation()}>
                {/* Header with title and actions */}
                <div className="detail-modal-header">
                    <div className="detail-title-section">
                        <h2 className="detail-game-title">{displayTitle}</h2>
                        {game.custom_title && game.custom_title !== game.title && (
                            <span className="detail-original-title">Original: {game.title}</span>
                        )}
                    </div>
                    <div className="detail-header-actions">
                        <button 
                            className="detail-edit-btn" 
                            onClick={() => onEdit(game)}
                            title="Edit Game"
                        >
                            <Pencil size={18} />
                            Edit
                        </button>
                        <button className="close-btn" onClick={onClose} title="Close">
                            <X size={24} />
                        </button>
                    </div>
                </div>

                {/* Main content */}
                <div className="detail-modal-body">
                    {/* Rating Badge */}
                    <div className="detail-rating-section">
                        <div 
                            className="detail-rating-badge" 
                            style={{ background: ratingBg }}
                        >
                            <Star size={24} className="detail-rating-icon" />
                            <span className="detail-rating-value">{ratingDisplay}</span>
                        </div>
                        <div className="detail-status-badges">
                            {game.played && (
                                <span className="detail-badge detail-badge-played">
                                    <ListChecks size={16} />
                                    Played
                                </span>
                            )}
                            {game.to_play && (
                                <span className="detail-badge detail-badge-toplay">
                                    <Gamepad2 size={16} />
                                    To Play
                                </span>
                            )}
                        </div>
                    </div>

                    {/* Description */}
                    {game.description && (
                        <div className="detail-section">
                            <div className="detail-section-header">
                                <AlignLeft size={18} />
                                <h3>Description</h3>
                            </div>
                            <p className="detail-description">{game.description}</p>
                        </div>
                    )}

                    {/* Release Date */}
                    {game.release_date && (
                        <div className="detail-section">
                            <div className="detail-section-header">
                                <Calendar size={18} />
                                <h3>Release Date</h3>
                            </div>
                            <p className="detail-text">{formatDate(game.release_date)}</p>
                        </div>
                    )}

                    {/* Platforms */}
                    <div className="detail-section">
                        <div className="detail-section-header">
                            <Gamepad2 size={18} />
                            <h3>Platforms</h3>
                        </div>
                        <div className="detail-platforms">
                            {game.platforms.map(p => getPlatformIcon(p))}
                        </div>
                    </div>

                    {/* Devices */}
                    {game.device && game.device.length > 0 && (
                        <div className="detail-section">
                            <div className="detail-section-header">
                                <Gamepad2 size={18} />
                                <h3>Devices</h3>
                            </div>
                            <div className="detail-devices">
                                {game.device.map(d => (
                                    <span key={d} className="detail-device-tag">
                                        {d}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Genres */}
                    <div className="detail-section">
                        <div className="detail-section-header">
                            <ListChecks size={18} />
                            <h3>Genres</h3>
                        </div>
                        <div className="detail-genres">
                            {game.genres.map(g => (
                                <span 
                                    key={g} 
                                    className={`genre-tag ${g === 'Sconosciuto' ? 'sconosciuto' : ''}`}
                                >
                                    {g}
                                </span>
                            ))}
                        </div>
                    </div>

                    {/* Notes */}
                    {game.notes && (
                        <div className="detail-section">
                            <div className="detail-section-header">
                                <AlignLeft size={18} />
                                <h3>Notes</h3>
                            </div>
                            <p className="detail-notes">{game.notes}</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default GameDetailModal;
