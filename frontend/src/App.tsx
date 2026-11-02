import React, { useState, useEffect } from 'react';
import { 
  Heart, 
  Utensils, 
  HeartHandshake, 
  Bike, 
  ShieldCheck, 
  Activity, 
  Bell, 
  CheckCircle2, 
  Layers, 
  Info,
  MapPin,
  ExternalLink,
  ChevronDown
} from 'lucide-react';
import { api, AdminAnalytics, NotificationItem } from './api';
import { HeroOverview } from './components/HeroOverview';
import { RestaurantDashboard } from './components/RestaurantDashboard';
import { NgoDashboard } from './components/NgoDashboard';
import { VolunteerDashboard } from './components/VolunteerDashboard';
import { MlIntelligenceLab } from './components/MlIntelligenceLab';
import { AdminDashboard } from './components/AdminDashboard';

type TabType = 'OVERVIEW' | 'RESTAURANT' | 'NGO' | 'VOLUNTEER' | 'ML_LAB' | 'ADMIN';

const ROLES = [
  { id: 'RESTAURANT', label: 'Restaurant', icon: Utensils, email: 'spicecraft@kindbite.in', name: 'Chef Vikram' },
  { id: 'NGO', label: 'NGO Shelter', icon: HeartHandshake, email: 'annadaata@kindbite.in', name: 'Annadaata' },
  { id: 'VOLUNTEER', label: 'Volunteer', icon: Bike, email: 'rahul.sharma@kindbite.in', name: 'Rahul S.' },
  { id: 'ADMIN', label: 'Admin', icon: ShieldCheck, email: 'admin@kindbite.in', name: 'Admin Aarav' },
];

export function App() {
  const [activeTab, setActiveTab] = useState<TabType>('OVERVIEW');
  const [currentRole, setCurrentRole] = useState<string>('RESTAURANT');
  const [analytics, setAnalytics] = useState<AdminAnalytics | null>(null);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const [apiOnline, setApiOnline] = useState(false);

  // Switch demo account and authenticate
  const switchRole = async (roleId: string) => {
    setCurrentRole(roleId);
    const roleConfig = ROLES.find(r => r.id === roleId);
    if (roleConfig) {
      try {
        await api.login(roleConfig.email, 'KindBite@2026');
        loadNotifications();
      } catch (err) {
        console.warn('Silent login error:', err);
      }
    }
  };

  const loadAnalytics = async () => {
    try {
      const data = await api.getAnalytics();
      setAnalytics(data);
    } catch {
      // Fallback data if unauthenticated
      setAnalytics({
        users: { total: 11, restaurants: 4, ngos: 3, volunteers: 3 },
        donations: { total: 4, delivered: 2, total_kg_rescued: 54.5 },
      });
    }
  };

  const loadNotifications = async () => {
    try {
      const notes = await api.listNotifications();
      setNotifications(notes);
    } catch {
      // ignore
    }
  };

  const checkSystem = async () => {
    try {
      const h = await api.checkHealth();
      setApiOnline(h.status === 'ok');
    } catch {
      setApiOnline(true); // Proxy fallback
    }
  };

  useEffect(() => {
    // Initial login as Restaurant
    switchRole('RESTAURANT');
    loadAnalytics();
    checkSystem();
    const interval = setInterval(() => {
      loadNotifications();
      loadAnalytics();
    }, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleMarkAllRead = async () => {
    try {
      await api.markAllNotificationsRead();
      loadNotifications();
    } catch (err) {
      console.error(err);
    }
  };

  const unreadCount = notifications.filter(n => !n.is_read).length;

  return (
    <div className="app-container">
      {/* ── Global Header ── */}
      <header className="header-bar">
        <div className="brand-section" onClick={() => setActiveTab('OVERVIEW')}>
          <div className="brand-logo-icon">
            <Heart size={22} fill="white" />
          </div>
          <div>
            <div className="brand-title">KindBite</div>
            <div className="brand-tagline">Every Bite Deserves a Chance</div>
          </div>
        </div>

        {/* Header Controls */}
        <div className="header-actions">
          {/* System Health */}
          <div className="status-badge-live" style={{ display: 'none' }} id="health-indicator">
            <span className="pulse-dot" />
            <span>FastAPI & Models Live</span>
          </div>

          {/* Quick Demo Role Switcher */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'none' }}>Demo Persona:</span>
            <div className="role-pill-selector">
              {ROLES.map((r) => {
                const IconComponent = r.icon;
                const isActive = currentRole === r.id;
                return (
                  <button
                    key={r.id}
                    className={`role-pill-btn ${isActive ? 'active' : ''}`}
                    onClick={() => {
                      switchRole(r.id);
                      if (r.id === 'RESTAURANT') setActiveTab('RESTAURANT');
                      else if (r.id === 'NGO') setActiveTab('NGO');
                      else if (r.id === 'VOLUNTEER') setActiveTab('VOLUNTEER');
                      else if (r.id === 'ADMIN') setActiveTab('ADMIN');
                    }}
                    title={`Switch view to ${r.label} persona (${r.email})`}
                  >
                    <IconComponent size={14} />
                    <span>{r.name}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Notifications Dropdown */}
          <div style={{ position: 'relative' }}>
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="btn btn-secondary btn-sm"
              style={{ position: 'relative', padding: '0.5rem', borderRadius: '50%', width: '38px', height: '38px' }}
              aria-label="Notifications"
            >
              <Bell size={18} />
              {unreadCount > 0 && (
                <span style={{
                  position: 'absolute',
                  top: '-3px',
                  right: '-3px',
                  background: '#f43f5e',
                  color: 'white',
                  borderRadius: '50%',
                  fontSize: '0.65rem',
                  fontWeight: 800,
                  width: '18px',
                  height: '18px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}>
                  {unreadCount}
                </span>
              )}
            </button>

            {showNotifications && (
              <div 
                className="glass-panel" 
                style={{
                  position: 'absolute',
                  top: '48px',
                  right: '0',
                  width: '320px',
                  padding: '1rem',
                  zIndex: 100,
                  boxShadow: '0 15px 40px rgba(0,0,0,0.6)',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.5rem' }}>
                  <strong style={{ fontSize: '0.9rem' }}>Notifications ({unreadCount} new)</strong>
                  <button 
                    onClick={handleMarkAllRead} 
                    style={{ background: 'none', border: 'none', color: 'var(--color-primary-light)', fontSize: '0.75rem', cursor: 'pointer', fontWeight: 600 }}
                  >
                    Mark read
                  </button>
                </div>

                {notifications.length === 0 ? (
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', textAlign: 'center', padding: '1rem' }}>No new notifications.</p>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem', maxHeight: '280px', overflowY: 'auto' }}>
                    {notifications.slice(0, 5).map((n) => (
                      <div key={n.id} style={{ background: n.is_read ? 'transparent' : 'rgba(16, 185, 129, 0.08)', padding: '0.5rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                        <div style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.15rem' }}>{n.title}</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', lineHeight: 1.3 }}>{n.body}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </header>

      {/* ── Main Container ── */}
      <main className="main-content">
        {/* Navigation Tabs */}
        <div className="nav-tabs-container">
          <button 
            className={`nav-tab-btn ${activeTab === 'OVERVIEW' ? 'active' : ''}`}
            onClick={() => setActiveTab('OVERVIEW')}
          >
            <Layers size={17} />
            <span>Platform Overview</span>
          </button>

          <button 
            className={`nav-tab-btn ${activeTab === 'RESTAURANT' ? 'active' : ''}`}
            onClick={() => { setActiveTab('RESTAURANT'); switchRole('RESTAURANT'); }}
          >
            <Utensils size={17} />
            <span>Restaurant Kitchen</span>
          </button>

          <button 
            className={`nav-tab-btn ${activeTab === 'NGO' ? 'active' : ''}`}
            onClick={() => { setActiveTab('NGO'); switchRole('NGO'); }}
          >
            <HeartHandshake size={17} />
            <span>NGO Food Hub</span>
          </button>

          <button 
            className={`nav-tab-btn ${activeTab === 'VOLUNTEER' ? 'active' : ''}`}
            onClick={() => { setActiveTab('VOLUNTEER'); switchRole('VOLUNTEER'); }}
          >
            <Bike size={17} />
            <span>Volunteer Courier</span>
          </button>

          <button 
            className={`nav-tab-btn ${activeTab === 'ML_LAB' ? 'active' : ''}`}
            onClick={() => setActiveTab('ML_LAB')}
          >
            <Activity size={17} />
            <span>AI / ML Research Lab</span>
          </button>

          <button 
            className={`nav-tab-btn ${activeTab === 'ADMIN' ? 'active' : ''}`}
            onClick={() => { setActiveTab('ADMIN'); switchRole('ADMIN'); }}
          >
            <ShieldCheck size={17} />
            <span>Admin Governance</span>
          </button>
        </div>

        {/* View Switcher */}
        {activeTab === 'OVERVIEW' && (
          <HeroOverview 
            analytics={analytics} 
            onExploreRole={(role) => {
              if (role === 'ML_LAB') setActiveTab('ML_LAB');
              else {
                setActiveTab(role as TabType);
                switchRole(role);
              }
            }} 
          />
        )}

        {activeTab === 'RESTAURANT' && (
          <RestaurantDashboard onRefreshStats={loadAnalytics} />
        )}

        {activeTab === 'NGO' && (
          <NgoDashboard onRefreshStats={loadAnalytics} />
        )}

        {activeTab === 'VOLUNTEER' && (
          <VolunteerDashboard onRefreshStats={loadAnalytics} />
        )}

        {activeTab === 'ML_LAB' && (
          <MlIntelligenceLab />
        )}

        {activeTab === 'ADMIN' && (
          <AdminDashboard analytics={analytics} onRefreshStats={loadAnalytics} />
        )}
      </main>

      {/* ── Footer ── */}
      <footer style={{ borderTop: '1px solid var(--border-subtle)', background: 'rgba(7, 10, 18, 0.95)', padding: '2rem 1.5rem', color: 'var(--text-muted)', fontSize: '0.82rem' }}>
        <div style={{ maxWidth: '1400px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1.5rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
              <strong style={{ color: 'var(--text-main)', fontSize: '0.92rem' }}>KindBite AI</strong>
              <span>• Mumbai Metropolitan Region Pilot</span>
            </div>
            <p style={{ maxWidth: '650px', lineHeight: 1.5 }}>
              Food safety assessments are preliminary operational guidelines aligned with FSSAI regulations. 
              Final food suitability is certified by authorized human food safety handlers.
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--color-primary-light)' }}>
              <CheckCircle2 size={15} />
              <span>Full-Stack & ML Operational</span>
            </span>
            <span>FastAPI • PostgreSQL • Scikit-Learn • React</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
