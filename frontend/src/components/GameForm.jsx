import React, { useState, useEffect } from 'react';
import api from '../api';
import { X, Save, Trash2 } from 'lucide-react';

const GameForm = ({ game, onClose, onSave, onDelete }) => {
    const isEditMode = !!game;

    const [formData, setFormData] = useState({
        title: '',
        custom_title: '',
        platforms: ['Microsoft'],
        device: ['PC'],
        genres: '',
        rating: 0,
        notes: '',
        played: false,
        is_dlc: false,
        to_play: false,
        description: '',
        release_date: ''
    });

    useEffect(() => {
        if (game) {
            setFormData({
                title: game.title,
                custom_title: game.custom_title || '',
                platforms: game.platforms.length > 0 ? game.platforms : ['Microsoft'],
                device: game.device && game.device.length > 0 ? game.device : ['PC'],
                genres: game.genres.join(', '),
                rating: game.rating !== null ? game.rating : '',
                notes: game.notes || '',
                played: game.played || false,
                is_dlc: game.is_dlc || false,
                to_play: game.to_play || false,
                description: game.description || '',
                release_date: game.release_date || ''
            });
        }
    }, [game]);

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        const payload = {
            ...formData,
            genres: formData.genres.split(',').map(g => g.trim()).filter(g => g),
            rating: formData.rating === '' ? null : parseInt(formData.rating),
            // Ensure platform is an array
            platforms: Array.isArray(formData.platforms) ? formData.platforms : [formData.platforms],
            device: Array.isArray(formData.device) ? formData.device : [formData.device]
        };

        // If it's a new game, custom_title might not be needed if same as title, but let's keep it simple
        if (!payload.custom_title) delete payload.custom_title;

        await onSave(payload);
    };

    return (
        <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
            <div className="modal-content">
                <button className="close-modal" onClick={onClose}><X /></button>
                <h2 style={{ marginTop: 0, marginBottom: '20px' }}>
                    {isEditMode ? 'Edit Game' : 'Add New Game'}
                </h2>

                <form onSubmit={handleSubmit}>
                    <div className="form-group" style={{ marginBottom: '15px' }}>
                        <label style={{ display: 'block', marginBottom: '5px', color: '#a0a0b0' }}>Title</label>
                        <input
                            name="title"
                            value={formData.title}
                            onChange={handleChange}
                            required
                            style={{ width: '100%' }}
                        />
                    </div>

                    <div className="form-group" style={{ marginBottom: '15px' }}>
                        <label style={{ display: 'block', marginBottom: '5px', color: '#a0a0b0' }}>Platform (Store)</label>
                        <select
                            name="platforms"
                            value={formData.platforms[0] || 'Microsoft'}
                            onChange={(e) => setFormData(prev => ({ ...prev, platforms: [e.target.value] }))}
                            style={{ width: '100%' }}
                        >
                            <option value="Steam">Steam</option>
                            <option value="Epic">Epic</option>
                            <option value="Amazon">Amazon</option>
                            <option value="GOG">GOG</option>
                            <option value="Microsoft">Microsoft</option>
                            <option value="EA">EA</option>
                            <option value="Other">Other</option>
                        </select>
                    </div>

                    <div className="form-group" style={{ marginBottom: '15px' }}>
                        <label style={{ display: 'block', marginBottom: '10px', color: '#a0a0b0' }}>Device (Gaming System)</label>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px', alignItems: 'stretch' }}>
                            {['PC', 'PS3', 'PS4', 'PS5', 'Xbox 360', 'Xbox One', 'Xbox Series X/S', 'Switch'].map(deviceOption => (
                                <label key={deviceOption} style={{ 
                                    display: 'flex', 
                                    alignItems: 'center', 
                                    gap: '8px',
                                    padding: '10px',
                                    background: formData.device.includes(deviceOption) ? 'rgba(100,100,255,0.15)' : 'rgba(255,255,255,0.05)',
                                    borderRadius: '6px',
                                    cursor: 'pointer',
                                    transition: 'all 0.2s',
                                    border: formData.device.includes(deviceOption) ? '1px solid rgba(100,100,255,0.4)' : '1px solid transparent'
                                }}>
                                    <input
                                        type="checkbox"
                                        checked={formData.device.includes(deviceOption)}
                                        onChange={(e) => {
                                            setFormData(prev => ({
                                                ...prev,
                                                device: e.target.checked 
                                                    ? [...prev.device, deviceOption]
                                                    : prev.device.filter(d => d !== deviceOption)
                                            }));
                                        }}
                                        style={{ cursor: 'pointer', margin: 0 }}
                                    />
                                    <span style={{ fontSize: '0.85rem' }}>{deviceOption}</span>
                                </label>
                            ))}
                        </div>
                    </div>

                    <div className="form-group" style={{ marginBottom: '15px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                            <label style={{ color: '#a0a0b0' }}>Rating (0-100)</label>
                            <span style={{ fontWeight: 'bold', color: formData.rating === '' ? '#aaa' : '#fff' }}>
                                {formData.rating === '' ? 'ND' : formData.rating}
                            </span>
                        </div>

                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                            <input
                                type="range"
                                name="rating"
                                min="0"
                                max="100"
                                value={formData.rating === '' ? 0 : formData.rating}
                                onChange={handleChange}
                                style={{ flexGrow: 1, cursor: 'pointer', height: '6px', width: 'auto' }}
                            />

                            <button
                                type="button"
                                onClick={() => setFormData(prev => ({ ...prev, rating: '' }))}
                                title="Reset to ND"
                                style={{
                                    background: 'rgba(255, 71, 87, 0.1)',
                                    border: '1px solid rgba(255, 71, 87, 0.3)',
                                    color: '#ff4757',
                                    borderRadius: '6px',
                                    cursor: 'pointer',
                                    height: '28px',
                                    padding: '0 10px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '4px',
                                    flexShrink: 0,
                                    transition: 'all 0.2s',
                                    fontSize: '0.7rem',
                                    fontWeight: '600',
                                    textTransform: 'uppercase',
                                    width: 'auto'
                                }}
                                onMouseEnter={(e) => { e.currentTarget.style.background = 'rgba(255, 71, 87, 0.2)'; }}
                                onMouseLeave={(e) => { e.currentTarget.style.background = 'rgba(255, 71, 87, 0.1)'; }}
                            >
                                <X size={14} /> Clear
                            </button>
                        </div>
                    </div>

                    <div className="form-group" style={{ marginBottom: '15px' }}>
                        <label style={{ display: 'block', marginBottom: '5px', color: '#a0a0b0' }}>Genres (comma separated)</label>
                        <input
                            name="genres"
                            value={formData.genres}
                            onChange={handleChange}
                            placeholder="Action, RPG, Adventure..."
                            style={{ width: '100%' }}
                        />
                    </div>

                    <div className="form-group" style={{ marginBottom: '15px' }}>
                        <label style={{ display: 'block', marginBottom: '5px', color: '#a0a0b0' }}>Description</label>
                        <textarea
                            name="description"
                            value={formData.description || ''}
                            onChange={handleChange}
                            rows="3"
                            placeholder="Brief description of the game..."
                            style={{ width: '100%', minHeight: '60px', resize: 'vertical' }}
                        />
                    </div>

                    <div className="form-group" style={{ marginBottom: '15px' }}>
                        <label style={{ display: 'block', marginBottom: '5px', color: '#a0a0b0' }}>Release Date</label>
                        <input
                            type="date"
                            name="release_date"
                            value={formData.release_date || ''}
                            onChange={handleChange}
                            style={{ width: '100%' }}
                        />
                    </div>

                    <div className="form-group" style={{ marginBottom: '15px' }}>
                        <label style={{ display: 'block', marginBottom: '5px', color: '#a0a0b0' }}>Notes</label>
                        <textarea
                            name="notes"
                            value={formData.notes || ''}
                            onChange={handleChange}
                            rows="4"
                            style={{ width: '100%', minHeight: '80px', resize: 'vertical' }}
                        />
                    </div>

                    <div className="form-group" style={{ marginBottom: '15px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <label className="switch">
                            <input
                                type="checkbox"
                                name="is_dlc"
                                checked={formData.is_dlc}
                                onChange={handleChange}
                            />
                            <span className="slider"></span>
                        </label>
                        <span style={{ fontSize: '0.9rem', color: '#aaa' }}>Is DLC/Expansion</span>
                    </div>

                    <div className="form-group" style={{ marginBottom: '15px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <label className="switch">
                            <input
                                type="checkbox"
                                name="to_play"
                                checked={formData.to_play}
                                onChange={handleChange}
                            />
                            <span className="slider"></span>
                        </label>
                        <span style={{ fontSize: '0.9rem', color: '#aaa' }}>Add to "To Play" list</span>
                    </div>

                    <div className="form-group" style={{ marginBottom: '25px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <label className="switch">
                            <input
                                type="checkbox"
                                name="played"
                                checked={formData.played}
                                onChange={handleChange}
                            />
                            <span className="slider"></span>
                        </label>
                        <span style={{ color: formData.played ? '#fff' : '#aaa' }}>
                            {formData.played ? 'Played' : 'Not Played'}
                        </span>
                    </div>

                    <div className="modal-actions" style={{ display: 'flex', justifyContent: 'space-between', marginTop: '30px' }}>
                        {isEditMode ? (
                            <button
                                type="button"
                                onClick={() => onDelete(game)}
                                className="btn-action"
                                style={{ background: 'transparent', border: '1px solid #ff4785', color: '#ff4785' }}
                            >
                                <Trash2 size={18} />
                                <span>Delete</span>
                            </button>
                        ) : (
                            <div></div> // Spacer
                        )}

                        <button type="submit" className="btn-action">
                            <Save size={18} />
                            <span>Save Changes</span>
                        </button>
                    </div>

                </form>
            </div>
        </div>
    );
};

export default GameForm;
