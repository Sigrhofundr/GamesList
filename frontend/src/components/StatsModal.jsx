import React, { useEffect, useState } from 'react';
import api from '../api';
import { X, PieChart, Layers, Monitor, CheckCircle } from 'lucide-react';

const StatsModal = ({ onClose }) => {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const res = await api.get('/stats');
                setStats(res.data);
            } catch (err) {
                console.error("Failed to load stats", err);
            } finally {
                setLoading(false);
            }
        };
        fetchStats();
    }, []);

    if (!stats && !loading) return null;

    return (
        <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
            <div className="modal-content" style={{ maxWidth: '800px' }}>
                <button className="close-modal" onClick={onClose}><X /></button>
                <h2 style={{ marginTop: 0, marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <PieChart /> Library Statistics
                </h2>

                {loading ? (
                    <p>Loading statistics...</p>
                ) : (
                    <div className="stats-grid">
                        <div className="stat-card">
                            <h3><Monitor size={18} /> Platforms</h3>
                            <div className="stat-list">
                                {Object.entries(stats.platforms).map(([name, count]) => (
                                    <div key={name} className="stat-row">
                                        <span className="stat-label">{name}</span>
                                        <div className="stat-bar-container">
                                            <div className="stat-bar" style={{ width: `${(count / stats.total) * 100}%` }}></div>
                                        </div>
                                        <span className="stat-value">{count}</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="stat-card">
                            <h3><Layers size={18} /> Top Genres</h3>
                            <div className="stat-list">
                                {Object.entries(stats.genres).slice(0, 10).map(([name, count]) => (
                                    <div key={name} className="stat-row">
                                        <span className="stat-label">{name}</span>
                                        <div className="stat-bar-container">
                                            <div className="stat-bar" style={{ width: `${(count / stats.total) * 100}%`, background: '#ff4785' }}></div>
                                        </div>
                                        <span className="stat-value">{count}</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="stat-card full-width">
                            <h3><CheckCircle size={18} /> Completion Status</h3>
                            <div className="completion-bar">
                                <div className="played-segment" style={{ width: `${(stats.played_count / stats.total) * 100}%` }}>
                                    {stats.played_count} Played
                                </div>
                                <div className="unplayed-segment" style={{ width: `${((stats.total - stats.played_count) / stats.total) * 100}%` }}>
                                    {stats.total - stats.played_count} Unplayed
                                </div>
                            </div>
                            <p style={{ textAlign: 'center', marginTop: '10px', opacity: 0.7 }}>
                                Total Games: <strong>{stats.total}</strong>
                            </p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default StatsModal;
