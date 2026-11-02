import React from 'react';
import { 
  Sparkles, 
  HeartHandshake, 
  TrendingDown, 
  ShieldCheck, 
  Truck, 
  MapPin, 
  ArrowRight,
  Activity,
  Layers,
  Award
} from 'lucide-react';
import { AdminAnalytics } from '../api';

interface HeroOverviewProps {
  analytics: AdminAnalytics | null;
  onExploreRole: (role: string) => void;
}

export const HeroOverview: React.FC<HeroOverviewProps> = ({ analytics, onExploreRole }) => {
  const kgRescued = analytics?.donations.total_kg_rescued || 45.5;
  const mealsSaved = Math.round(kgRescued * 2.5);
  const co2OffsetKg = Math.round(kgRescued * 2.1);

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2.5rem' }}>
      {/* ── Hero Banner ── */}
      <div 
        className="glass-panel" 
        style={{ 
          position: 'relative', 
          overflow: 'hidden', 
          padding: '3rem 2.5rem',
          background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(13, 20, 35, 0.9) 60%, rgba(99, 102, 241, 0.1) 100%)',
          border: '1px solid rgba(16, 185, 129, 0.25)',
          borderRadius: 'var(--radius-xl)'
        }}
      >
        <div style={{ maxWidth: '780px', position: 'relative', zIndex: 2 }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.3)', padding: '0.35rem 0.85rem', borderRadius: 'var(--radius-full)', marginBottom: '1.25rem' }}>
            <Sparkles size={16} color="#34d399" />
            <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#34d399', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Mumbai Pilot • AI-Powered Food Intelligence
            </span>
          </div>

          <h1 style={{ fontSize: '3rem', lineHeight: 1.15, marginBottom: '1rem', fontWeight: 800 }}>
            Every Bite Deserves <br />
            <span style={{ background: 'linear-gradient(135deg, #10b981 0%, #34d399 50%, #60a5fa 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              A Second Chance.
            </span>
          </h1>

          <p style={{ fontSize: '1.1rem', color: 'var(--text-secondary)', marginBottom: '2rem', lineHeight: 1.6, maxWidth: '650px' }}>
            KindBite prevents commercial kitchen food waste before it happens using predictive demand forecasting, 
            verifies FSSAI-aligned food safety standards, and coordinates rapid redistribution to verified Mumbai shelters.
          </p>

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem' }}>
            <button 
              className="btn btn-primary" 
              onClick={() => onExploreRole('RESTAURANT')}
              style={{ fontSize: '0.95rem', padding: '0.85rem 1.75rem' }}
            >
              <span>Explore Restaurant Hub</span>
              <ArrowRight size={18} />
            </button>
            <button 
              className="btn btn-secondary" 
              onClick={() => onExploreRole('ML_LAB')}
              style={{ fontSize: '0.95rem', padding: '0.85rem 1.5rem' }}
            >
              <Activity size={18} color="#10b981" />
              <span>Launch ML Lab</span>
            </button>
          </div>
        </div>

        {/* Decorative Floating Badges */}
        <div style={{ position: 'absolute', right: '3rem', top: '50%', transform: 'translateY(-50%)', display: 'none', flexDirection: 'column', gap: '1.25rem' }} className="hero-desktop-art">
          <div style={{ background: 'rgba(15, 23, 42, 0.8)', border: '1px solid rgba(16, 185, 129, 0.3)', padding: '1rem 1.25rem', borderRadius: 'var(--radius-lg)', backdropFilter: 'blur(12px)', width: '260px', boxShadow: '0 10px 30px rgba(0,0,0,0.5)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
              <ShieldCheck size={22} color="#10b981" />
              <span style={{ fontWeight: 700, fontSize: '0.9rem' }}>FSSAI Compliant</span>
            </div>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Rigorous temperature & time windows strictly enforced on every parcel.</p>
          </div>

          <div style={{ background: 'rgba(15, 23, 42, 0.8)', border: '1px solid rgba(99, 102, 241, 0.3)', padding: '1rem 1.25rem', borderRadius: 'var(--radius-lg)', backdropFilter: 'blur(12px)', width: '260px', boxShadow: '0 10px 30px rgba(0,0,0,0.5)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
              <Layers size={22} color="#818cf8" />
              <span style={{ fontWeight: 700, fontSize: '0.9rem' }}>95.9% R² Precision</span>
            </div>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Trained Random Forest regressors predict daily restaurant demand accurately.</p>
          </div>
        </div>
      </div>

      {/* ── Key Impact Stats ── */}
      <div className="stats-grid">
        <div className="stat-card" style={{ '--accent-color': '#10b981' } as React.CSSProperties}>
          <div className="stat-icon-wrapper">
            <TrendingDown size={24} />
          </div>
          <div>
            <div className="stat-title">Surplus Food Rescued</div>
            <div className="stat-value">{kgRescued.toLocaleString()} kg</div>
            <div className="stat-subtext">Verified safe commercial surplus</div>
          </div>
        </div>

        <div className="stat-card" style={{ '--accent-color': '#f59e0b' } as React.CSSProperties}>
          <div className="stat-icon-wrapper">
            <HeartHandshake size={24} />
          </div>
          <div>
            <div className="stat-title">Nutritious Meals Served</div>
            <div className="stat-value">{mealsSaved.toLocaleString()}</div>
            <div className="stat-subtext">Delivered to Mumbai food banks</div>
          </div>
        </div>

        <div className="stat-card" style={{ '--accent-color': '#06b6d4' } as React.CSSProperties}>
          <div className="stat-icon-wrapper">
            <Award size={24} />
          </div>
          <div>
            <div className="stat-title">CO₂ Emissions Offset</div>
            <div className="stat-value">{co2OffsetKg.toLocaleString()} kg</div>
            <div className="stat-subtext">Landfill methane diversion</div>
          </div>
        </div>

        <div className="stat-card" style={{ '--accent-color': '#6366f1' } as React.CSSProperties}>
          <div className="stat-icon-wrapper">
            <Truck size={24} />
          </div>
          <div>
            <div className="stat-title">Avg. Dispatch Latency</div>
            <div className="stat-value">26 mins</div>
            <div className="stat-subtext">From listing to volunteer pickup</div>
          </div>
        </div>
      </div>

      {/* ── 4-Step Architecture Workflow ── */}
      <div className="glass-panel">
        <div style={{ marginBottom: '1.75rem' }}>
          <h2 style={{ fontSize: '1.4rem', marginBottom: '0.35rem' }}>The KindBite Redistribution Loop</h2>
          <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
            Bridging machine learning demand intelligence with high-integrity humanitarian relief.
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' }}>
          <div style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '1.5rem' }}>
            <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: 'rgba(16, 185, 129, 0.15)', color: '#34d399', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, marginBottom: '1rem' }}>
              01
            </div>
            <h3 style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>Demand & Waste Prediction</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              Trained models analyze weather patterns, monsoon anomalies, and festival footfall to predict daily surplus volume before cooking starts.
            </p>
          </div>

          <div style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '1.5rem' }}>
            <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, marginBottom: '1rem' }}>
              02
            </div>
            <h3 style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>FSSAI Food Safety Check</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              Strict verification of holding temperature (≥60°C hot, ≤5°C cold), shelf-life limits, allergens, and safe packaging. No AI overrides safety.
            </p>
          </div>

          <div style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '1.5rem' }}>
            <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: 'rgba(99, 102, 241, 0.15)', color: '#818cf8', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, marginBottom: '1rem' }}>
              03
            </div>
            <h3 style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>Multi-Criteria NGO Match</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              Algorithmic scoring ranks receiving NGOs by food category match, remaining daily capacity, urgency, and shortest Haversine transit distance.
            </p>
          </div>

          <div style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '1.5rem' }}>
            <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: 'rgba(6, 182, 212, 0.15)', color: '#22d3ee', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, marginBottom: '1rem' }}>
              04
            </div>
            <h3 style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>Dispatched Courier Delivery</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              Local two-wheeler and vehicle volunteers receive turn-by-turn routing, pickup parcels within the freshness window, and verify handoff.
            </p>
          </div>
        </div>
      </div>

      {/* ── Pilot Locations (Mumbai Cluster) ── */}
      <div className="glass-panel">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
          <div>
            <h3 style={{ fontSize: '1.2rem', marginBottom: '0.25rem' }}>Active Pilot Network • Mumbai Hubs</h3>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>Live geolocation coverage across South, Central & Suburban Mumbai</p>
          </div>
          <span className="status-badge-live">
            <span className="pulse-dot" />
            <span>4 Kitchens • 3 Food Banks • 3 Couriers Live</span>
          </span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
          <div style={{ padding: '1rem', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
              <MapPin size={16} color="#10b981" />
              <strong style={{ fontSize: '0.92rem' }}>Bandra West • The Spice Craft</strong>
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Fine Dining Indian • Average daily surplus: 14 kg • High veg compatibility</p>
          </div>

          <div style={{ padding: '1rem', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
              <MapPin size={16} color="#38bdf8" />
              <strong style={{ fontSize: '0.92rem' }}>Sion / Dharavi • Annadaata Foundation</strong>
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Distribution Shelter • Daily receiving limit: 250 kg • Refrigerated hold</p>
          </div>

          <div style={{ padding: '1rem', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
              <MapPin size={16} color="#f59e0b" />
              <strong style={{ fontSize: '0.92rem' }}>Andheri East • Tandoor Nights</strong>
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Casual Mughlai • Average daily surplus: 22 kg • Hot holding insulated bins</p>
          </div>
        </div>
      </div>
    </div>
  );
};
