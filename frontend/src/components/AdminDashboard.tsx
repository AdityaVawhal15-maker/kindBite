import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  Users, 
  Building2, 
  HeartHandshake, 
  Bike, 
  FileText, 
  CheckCircle2, 
  XCircle, 
  RefreshCw,
  Search,
  Scale
} from 'lucide-react';
import confetti from 'canvas-confetti';
import { api, AdminAnalytics } from '../api';

interface AdminDashboardProps {
  analytics: AdminAnalytics | null;
  onRefreshStats: () => void;
}

export const AdminDashboard: React.FC<AdminDashboardProps> = ({ analytics, onRefreshStats }) => {
  const [verifications, setVerifications] = useState<any[]>([]);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'verifications' | 'audit'>('verifications');

  const loadData = async () => {
    try {
      setLoading(true);
      const [vList, aLogs] = await Promise.all([
        api.listVerifications().catch(() => []),
        api.listAuditLogs().catch(() => []),
      ]);
      setVerifications(vList);
      setAuditLogs(aLogs);
    } catch (err: any) {
      console.error('Failed to load admin data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleVerify = async (entityType: string, entityId: string, status: string) => {
    try {
      await api.updateVerification(entityType, entityId, status, `Verified by admin at ${new Date().toISOString()}`);
      confetti({
        particleCount: 40,
        spread: 50,
        origin: { y: 0.6 },
      });
      await loadData();
      onRefreshStats();
    } catch (err: any) {
      alert(`Verification action failed: ${err.message}`);
    }
  };

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* ── Top Bar ── */}
      <div className="glass-panel" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          <div style={{ width: '48px', height: '48px', borderRadius: 'var(--radius-md)', background: 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white' }}>
            <ShieldCheck size={26} />
          </div>
          <div>
            <h2 style={{ fontSize: '1.5rem', marginBottom: '0.2rem' }}>Aarav Mehta • Platform Administrator</h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
              System Governance, Verification Authority & Immutable Audit Trails
            </p>
          </div>
        </div>

        <button className="btn btn-secondary" onClick={loadData}>
          <RefreshCw size={16} />
          <span>Refresh Data</span>
        </button>
      </div>

      {/* ── Platform Summary Cards ── */}
      <div className="stats-grid">
        <div className="stat-card" style={{ '--accent-color': '#0284c7' } as React.CSSProperties}>
          <div className="stat-icon-wrapper">
            <Users size={22} />
          </div>
          <div>
            <div className="stat-title">Registered Accounts</div>
            <div className="stat-value">{analytics?.users.total || 11}</div>
            <div className="stat-subtext">Active verified community members</div>
          </div>
        </div>

        <div className="stat-card" style={{ '--accent-color': '#10b981' } as React.CSSProperties}>
          <div className="stat-icon-wrapper">
            <Building2 size={22} />
          </div>
          <div>
            <div className="stat-title">Commercial Kitchens</div>
            <div className="stat-value">{analytics?.users.restaurants || 4}</div>
            <div className="stat-subtext">FSSAI certified food providers</div>
          </div>
        </div>

        <div className="stat-card" style={{ '--accent-color': '#f59e0b' } as React.CSSProperties}>
          <div className="stat-icon-wrapper">
            <HeartHandshake size={22} />
          </div>
          <div>
            <div className="stat-title">Verified NGO Shelters</div>
            <div className="stat-value">{analytics?.users.ngos || 3}</div>
            <div className="stat-subtext">780 kg combined daily intake</div>
          </div>
        </div>

        <div className="stat-card" style={{ '--accent-color': '#818cf8' } as React.CSSProperties}>
          <div className="stat-icon-wrapper">
            <Bike size={22} />
          </div>
          <div>
            <div className="stat-title">Active Volunteer Couriers</div>
            <div className="stat-value">{analytics?.users.volunteers || 3}</div>
            <div className="stat-subtext">Two-wheelers & cargo cars</div>
          </div>
        </div>
      </div>

      {/* ── Tab Selector ── */}
      <div style={{ display: 'flex', gap: '1rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.5rem' }}>
        <button 
          className={`btn ${activeTab === 'verifications' ? 'btn-primary' : 'btn-secondary'} btn-sm`}
          onClick={() => setActiveTab('verifications')}
        >
          <Scale size={16} />
          <span>Partner Verification Queue ({verifications.length})</span>
        </button>

        <button 
          className={`btn ${activeTab === 'audit' ? 'btn-primary' : 'btn-secondary'} btn-sm`}
          onClick={() => setActiveTab('audit')}
        >
          <FileText size={16} />
          <span>Audit Log Trail ({auditLogs.length})</span>
        </button>
      </div>

      {/* ── Content View ── */}
      {activeTab === 'verifications' ? (
        <div className="glass-panel">
          <h3 style={{ fontSize: '1.25rem', marginBottom: '1rem' }}>Commercial Kitchen & NGO Verification Registry</h3>
          {verifications.length === 0 ? (
            <div style={{ padding: '2.5rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
              <CheckCircle2 size={36} color="#10b981" style={{ margin: '0 auto 0.75rem' }} />
              <p>All restaurants, NGOs, and volunteers in the Mumbai pilot cluster are verified.</p>
            </div>
          ) : (
            <div className="data-table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Entity</th>
                    <th>Type</th>
                    <th>Location</th>
                    <th>Licensing / Registration</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {verifications.map((v) => (
                    <tr key={v.id}>
                      <td><strong>{v.name}</strong></td>
                      <td>{v.entity_type}</td>
                      <td>{v.city || 'Mumbai'} ({v.pincode})</td>
                      <td>
                        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                          {v.fssai_number || v.registration_number || 'Under review'}
                        </span>
                      </td>
                      <td>
                        <span className={`badge ${v.verification_status === 'VERIFIED' ? 'badge-delivered' : 'badge-matched'}`}>
                          {v.verification_status}
                        </span>
                      </td>
                      <td>
                        {v.verification_status !== 'VERIFIED' ? (
                          <div style={{ display: 'flex', gap: '0.5rem' }}>
                            <button 
                              className="btn btn-primary btn-sm"
                              onClick={() => handleVerify(v.entity_type, v.id, 'VERIFIED')}
                            >
                              <CheckCircle2 size={14} /> Approve
                            </button>
                            <button 
                              className="btn btn-secondary btn-sm"
                              onClick={() => handleVerify(v.entity_type, v.id, 'REJECTED')}
                            >
                              <XCircle size={14} /> Reject
                            </button>
                          </div>
                        ) : (
                          <span style={{ color: '#34d399', fontSize: '0.82rem', fontWeight: 600 }}>Active License</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      ) : (
        <div className="glass-panel">
          <h3 style={{ fontSize: '1.25rem', marginBottom: '1rem' }}>Immutable Audit Log Trail</h3>
          <div className="data-table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Action</th>
                  <th>Resource</th>
                  <th>Actor / Origin</th>
                  <th>Event Details</th>
                </tr>
              </thead>
              <tbody>
                {auditLogs.slice(0, 15).map((log) => (
                  <tr key={log.id}>
                    <td>
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        {new Date(log.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </td>
                    <td><strong style={{ color: 'var(--text-main)' }}>{log.action}</strong></td>
                    <td>{log.resource_type}</td>
                    <td>{log.ip_address || 'System Internal'}</td>
                    <td>
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        {JSON.stringify(log.details || {})}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
