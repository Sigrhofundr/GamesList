import React from 'react';
import GameCard from './GameCard';

const GameGrid = ({ games, onEdit, onTogglePlayed, onViewDetails, loading }) => {
    if (loading) {
        return <div id="loading">Loading library...</div>;
    }

    if (games.length === 0) {
        return (
            <div className="no-results">
                No games found matching your filters.
            </div>
        );
    }

    return (
        <div className="game-grid">
            {games.map((game) => (
                <GameCard
                    key={game._id || game.id}
                    game={game}
                    onEdit={onEdit}
                    onTogglePlayed={onTogglePlayed}
                    onViewDetails={onViewDetails}
                />
            ))}
        </div>
    );
};

export default GameGrid;
