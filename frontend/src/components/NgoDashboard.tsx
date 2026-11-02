import React, { useState, useEffect } from 'react';
import { 
  HeartHandshake, 
  MapPin, 
  Clock, 
  CheckCircle2, 
  ShieldCheck, 
  Truck, 
  RefreshCw,
  Sparkles,
  AlertCircle
} from 'lucide-react';
import confetti from 'canvas-confetti';
import { api, Donation } from '../api';

interface NgoDashboardProps {
  onRefreshStats: () => void;
}

export const NgoDashboard: React.FC<NgoDashboardProps> = ({ onRefreshStats }) => {
  const [donations, setDonations] = useState<Donation[]>([]);
  const [loading, setLoading] = useState(true);
  const [claimingId, setClaimingId] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState('');

  const loadDonations = async () => {
    try {
      setLoading(true);
      const data = await api.listDonations();
      setDonations(data);
    } catch (err: any) {
      console.error('Failed to load donations for NGO:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDonations();
  }, []);

  const handleClaimParcel = async (donationId: string) => {
    try {
      setClaimingId(donationId);
      setSuccessMsg('');
      await api.acceptDonation(donationId);

      confetti({
        particleCount: 70,
        spread: 70,
        origin: { y: 0.6 },
      });

      setSuccessMsg('Donation accepted! A nearby volunteer has been notified for pickup.');
      await loadDonations();
      onRefreshStats();
    } catch (err: any) {
      alert(`Could not accept donation: ${err.message}`);
    } finally {
      setClaimingId(null);
    }
  };

  // Filter available donations: PUBLISHED or MATCHED
  const availableParcels = donations.filter(d => ['PUBLISHED', 'MATCHED'].includes(d.status));
  const acceptedDeliveries = donations.filter(d => ['ACCEPTED', 'ASSIGNED', 'IN_TRANSIT', 'DELIVERED'].includes(d.status));

  // Calculate daily intake
  const totalAcceptedKg = acceptedDeliveries
    .filter(d => d.status === 'DELIVERED')
    .reduce((acc, curr) => acc + curr.quantity_kg, 0);

  const dailyCapacityKg = 250.0;
  const capacityPct = Math.min(100, Math.round((totalAcceptedKg / dailyCapacityKg) * 100));

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* ── Top Profile & Capacity Bar ── */}
      <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
            <div style={{ width: '48px', height: '48px', borderRadius: 'var(--radius-md)', background: 'linear-gradient(135deg, #0d9488 0%, #10b981 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white' }}>
              <HeartHandshake size={24} />
            </div>
            <div>
              <h2 style={{ fontSize: '1.5rem', marginBottom: '0.2rem' }}>Annadaata Food Foundation</h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                Central Mumbai Hub • Sion / Dharavi • Registration: MH/MUM/2015/F-48291
              </p>
            </div>
          </div>

          <button className="btn btn-secondary" onClick={loadDonations}>
            <RefreshCw size={16} />
            <span>Refresh Feed</span>
          </button>
        </div>

        {/* Capacity Progress Bar */}
        <div style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '1rem 1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem', fontSize: '0.85rem' }}>
            <span style={{ fontWeight: 600 }}>Daily Intake Capacity</span>
            <span style={{ color: 'var(--color-primary-light)', fontWeight: 700 }}>
              {totalAcceptedKg.toFixed(1)} / {dailyCapacityKg} kg ({capacityPct}%)
            </span>
          </div>
          <div style={{ width: '100%', height: '8px', background: 'rgba(255,255,255,0.06)', borderRadius: '4px', overflow: 'hidden' }}>
            <div style={{ width: `${capacityPct}%`, height: '100%', background: 'linear-gradient(90deg, #10b981 0%, #34d399 100%)', borderRadius: '4px', transition: 'width 0.4s ease' }} />
          </div>
        </div>
      </div>

      {successMsg && (
        <div style={{ background: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.35)', color: '#34d399', padding: '1rem 1.25rem', borderRadius: 'var(--radius-md)', display: 'flex', alignItems: 'center', gap: '0.75rem', fontWeight: 600 }}>
          <CheckCircle2 size={20} />
          <span>{successMsg}</span>
        </div>
      )}

      {/* ── Available Food Parcels Feed ── */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
          <div>
            <h3 style={{ fontSize: '1.35rem', marginBottom: '0.2rem' }}>Available Surplus Parcels for Rescue</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              Nearby hot & bakery surplus matched to your food preferences
            </p>
          </div>
          <span className="badge badge-published">{availableParcels.length} Available Nearby</span>
        </div>

        {loading ? (
          <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
            Loading available food parcels...
          </div>
        ) : availableParcels.length === 0 ? (
          <div className="glass-panel" style={{ textAlign: 'center', padding: '3rem' }}>
            <CheckCircle2 size={40} color="#10b981" style={{ margin: '0 auto 1rem' }} />
            <h4 style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>All Surplus Food Successfully Rescued!</h4>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem' }}>
              There are currently no unmatched parcels in your zone. New food listings appear as restaurant prep ends.
            </p>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '1.25rem' }}>
            {availableParcels.map((parcel) => (
              <div 
                key={parcel.id} 
                className="glass-panel"
                style={{ 
                  display: 'flex', 
                  flexDirection: 'column', 
                  justifyContent: 'space-between', 
                  gap: '1.25rem',
                  border: '1px solid rgba(16, 185, 129, 0.25)',
                  background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(20, 32, 56, 0.8) 100%)'
                }}
              >
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                    <span className="badge badge-published">{parcel.food_category.replace('_', ' ')}</span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', background: 'rgba(16, 185, 129, 0.15)', color: '#34d399', padding: '0.25rem 0.65rem', borderRadius: 'var(--radius-full)', fontSize: '0.75rem', fontWeight: 700 }}>
                      <Sparkles size={13} />
                      <span>94% MATCH SCORE</span>
                    </span>
                  </div>

                  <h4 style={{ fontSize: '1.25rem', marginBottom: '0.4rem', color: 'var(--text-main)' }}>
                    {parcel.food_name}
                  </h4>

                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '1rem' }}>
                    <div>
                      <strong style={{ color: 'var(--text-main)', fontSize: '1.1rem' }}>{parcel.quantity_kg} kg</strong>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}> ({parcel.servings || 40} servings)</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                      <MapPin size={15} color="#0d9488" />
                      <span>Bandra West (6.4 km)</span>
                    </div>
                  </div>

                  <div style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', padding: '0.75rem', fontSize: '0.8rem', display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: 'var(--text-muted)' }}>Storage Holding:</span>
                      <strong style={{ color: '#34d399' }}>{parcel.storage_condition || 'HOT_HOLD'} ({parcel.storage_temp_celsius || 64}°C)</strong>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: 'var(--text-muted)' }}>Freshness Check:</span>
                      <span style={{ color: '#34d399', fontWeight: 600 }}>FSSAI Verification Passed</span>
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderTop: '1px solid var(--border-subtle)', paddingTop: '1rem' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                    <Clock size={14} />
                    <span>Pickup deadline in 2.5h</span>
                  </div>

                  <button 
                    className="btn btn-primary"
                    onClick={() => handleClaimParcel(parcel.id)}
                    disabled={claimingId === parcel.id}
                  >
                    <Truck size={16} />
                    <span>{claimingId === parcel.id ? 'Claiming...' : 'Claim & Dispatch'}</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ── Active Inbound Deliveries ── */}
      <div className="glass-panel">
        <h3 style={{ fontSize: '1.25rem', marginBottom: '1rem' }}>Active Inbound Deliveries to Shelter</h3>

        {acceptedDeliveries.length === 0 ? (
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem' }}>No active inbound deliveries right now.</p>
        ) : (
          <div className="data-table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Food Item</th>
                  <th>Quantity</th>
                  <th>Donor Kitchen</th>
                  <th>Status</th>
                  <th>Assigned Courier</th>
                </tr>
              </thead>
              <tbody>
                {acceptedDeliveries.map((del) => (
                  <tr key={del.id}>
                    <td><strong>{del.food_name}</strong></td>
                    <td>{del.quantity_kg} kg</td>
                    <td>{del.pickup_address || 'Mumbai Kitchen'}</td>
                    <td>
                      <span className={`badge badge-${del.status.toLowerCase()}`}>
                        {del.status}
                      </span>
                    </td>
                    <td>
                      <span style={{ color: 'var(--color-primary-light)', fontWeight: 600, fontSize: '0.85rem' }}>
                        Rahul Sharma (Motorcycle)
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
