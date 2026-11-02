import React, { useState, useEffect } from 'react';
import { 
  Bike, 
  MapPin, 
  Navigation, 
  CheckCircle2, 
  Clock, 
  PhoneCall, 
  PackageCheck,
  RefreshCw,
  Award
} from 'lucide-react';
import confetti from 'canvas-confetti';
import { api, Donation } from '../api';

interface VolunteerDashboardProps {
  onRefreshStats: () => void;
}

export const VolunteerDashboard: React.FC<VolunteerDashboardProps> = ({ onRefreshStats }) => {
  const [deliveries, setDeliveries] = useState<Donation[]>([]);
  const [loading, setLoading] = useState(true);
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  const loadDeliveries = async () => {
    try {
      setLoading(true);
      const all = await api.listDonations();
      // Filter deliveries assigned to volunteer or in active delivery statuses
      const active = all.filter(d => ['ASSIGNED', 'IN_TRANSIT', 'DELIVERED'].includes(d.status));
      setDeliveries(active);
    } catch (err: any) {
      console.error('Failed to load volunteer deliveries:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDeliveries();
  }, []);

  const handleAdvanceStatus = async (donationId: string, currentStatus: string) => {
    try {
      setUpdatingId(donationId);
      let nextStatus = 'IN_TRANSIT';
      if (currentStatus === 'IN_TRANSIT') {
        nextStatus = 'DELIVERED';
      }

      // Simulated status progression
      confetti({
        particleCount: 50,
        spread: 60,
        origin: { y: 0.7 },
      });

      // Reload
      await loadDeliveries();
      onRefreshStats();
    } catch (err: any) {
      console.error('Failed status update:', err);
    } finally {
      setUpdatingId(null);
    }
  };

  const completedCount = deliveries.filter(d => d.status === 'DELIVERED').length;
  const activeCount = deliveries.filter(d => d.status !== 'DELIVERED').length;

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* ── Volunteer Header ── */}
      <div className="glass-panel" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          <div style={{ width: '48px', height: '48px', borderRadius: 'var(--radius-md)', background: 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white' }}>
            <Bike size={24} />
          </div>
          <div>
            <h2 style={{ fontSize: '1.5rem', marginBottom: '0.2rem' }}>Rahul Sharma • Active Volunteer Courier</h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
              Vehicle: 150cc Motorcycle • Bandra / Andheri Sector • Verified & Active
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(99, 102, 241, 0.12)', border: '1px solid rgba(99, 102, 241, 0.25)', padding: '0.4rem 0.85rem', borderRadius: 'var(--radius-full)', color: '#818cf8', fontSize: '0.82rem', fontWeight: 700 }}>
            <Award size={16} />
            <span>{completedCount} Missions Completed</span>
          </div>

          <button className="btn btn-secondary" onClick={loadDeliveries}>
            <RefreshCw size={16} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* ── Active Assigned Mission ── */}
      <div>
        <h3 style={{ fontSize: '1.35rem', marginBottom: '1.25rem' }}>Active Delivery Mission</h3>

        {loading ? (
          <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
            Loading assigned deliveries...
          </div>
        ) : activeCount === 0 ? (
          <div className="glass-panel" style={{ textAlign: 'center', padding: '3rem' }}>
            <CheckCircle2 size={40} color="#10b981" style={{ margin: '0 auto 1rem' }} />
            <h4 style={{ fontSize: '1.1rem', marginBottom: '0.4rem' }}>No pending deliveries in your queue!</h4>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
              You're currently idle and available for instant dispatch in Bandra / Suburban Mumbai.
            </p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            {deliveries.filter(d => d.status !== 'DELIVERED').map((del) => (
              <div key={del.id} className="glass-panel highlighted" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span className="badge badge-intransit">MISSION IN PROGRESS</span>
                    <strong style={{ fontSize: '1.2rem' }}>{del.food_name}</strong>
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>({del.quantity_kg} kg)</span>
                  </div>

                  <span className="status-badge-live">
                    <span className="pulse-dot" />
                    <span>GPS Tracking Active</span>
                  </span>
                </div>

                {/* Route Steps */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr auto 1fr', gap: '1rem', alignItems: 'center', background: 'rgba(255, 255, 255, 0.02)', padding: '1.25rem', borderRadius: 'var(--radius-md)' }}>
                  <div>
                    <div style={{ fontSize: '0.75rem', color: '#38bdf8', fontWeight: 700, textTransform: 'uppercase', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                      <MapPin size={14} /> PICKUP LOCATION
                    </div>
                    <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>The Spice Craft Kitchen</div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Plot 42, Hill Road, Bandra West</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--color-primary-light)', marginTop: '0.2rem' }}>Hot holding container verified</div>
                  </div>

                  <div style={{ textAlign: 'center', padding: '0 1rem' }}>
                    <Navigation size={22} color="#818cf8" />
                    <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#818cf8', marginTop: '0.25rem' }}>6.4 km • 24m</div>
                  </div>

                  <div>
                    <div style={{ fontSize: '0.75rem', color: '#f59e0b', fontWeight: 700, textTransform: 'uppercase', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                      <MapPin size={14} /> DROPOFF SHELTER
                    </div>
                    <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>Annadaata Food Foundation</div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Behind Sion Hospital, Sion East</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>Contact: Sr. Teresa Fernandes</div>
                  </div>
                </div>

                {/* Courier Actions */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderTop: '1px solid var(--border-subtle)', paddingTop: '1rem', flexWrap: 'wrap', gap: '1rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <a href="tel:+919820000002" className="btn btn-secondary btn-sm" style={{ textDecoration: 'none' }}>
                      <PhoneCall size={14} />
                      <span>Call Kitchen Dispatch</span>
                    </a>
                  </div>

                  <div style={{ display: 'flex', gap: '0.75rem' }}>
                    <button 
                      className="btn btn-primary"
                      onClick={() => handleAdvanceStatus(del.id, del.status)}
                      disabled={updatingId === del.id}
                    >
                      <PackageCheck size={16} />
                      <span>{del.status === 'ASSIGNED' ? 'Confirm Parcel Picked Up' : 'Confirm Delivered to Shelter'}</span>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ── Mission History ── */}
      <div className="glass-panel">
        <h3 style={{ fontSize: '1.25rem', marginBottom: '1rem' }}>Completed Redistribution Log</h3>
        <div className="data-table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Food Item</th>
                <th>Quantity</th>
                <th>From Kitchen</th>
                <th>To Food Bank</th>
                <th>Delivery Verified</th>
              </tr>
            </thead>
            <tbody>
              {deliveries.filter(d => d.status === 'DELIVERED').map((d) => (
                <tr key={d.id}>
                  <td><strong>{d.food_name}</strong></td>
                  <td>{d.quantity_kg} kg</td>
                  <td>The Spice Craft (Bandra)</td>
                  <td>Annadaata Shelter (Sion)</td>
                  <td>
                    <span style={{ color: '#34d399', display: 'inline-flex', alignItems: 'center', gap: '0.3rem', fontSize: '0.82rem', fontWeight: 600 }}>
                      <CheckCircle2 size={16} /> Verified Handoff
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
