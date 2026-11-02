import React, { useState, useEffect } from 'react';
import { 
  PlusCircle, 
  Sparkles, 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle2, 
  X, 
  Clock, 
  Thermometer, 
  Box, 
  Layers, 
  Calendar,
  RefreshCw,
  Utensils
} from 'lucide-react';
import confetti from 'canvas-confetti';
import { api, Donation, SurplusPredictionResult } from '../api';

interface RestaurantDashboardProps {
  onRefreshStats: () => void;
}

export const RestaurantDashboard: React.FC<RestaurantDashboardProps> = ({ onRefreshStats }) => {
  const [donations, setDonations] = useState<Donation[]>([]);
  const [loading, setLoading] = useState(true);
  const [showWizard, setShowWizard] = useState(false);
  const [forecastLoading, setForecastLoading] = useState(false);
  const [forecastResult, setForecastResult] = useState<SurplusPredictionResult | null>(null);

  // Form State
  const [foodName, setFoodName] = useState('Dum Pukht Veg Biryani');
  const [foodCategory, setFoodCategory] = useState('COOKED_MEALS');
  const [quantityKg, setQuantityKg] = useState('15.0');
  const [servings, setServings] = useState('40');
  const [storageCondition, setStorageCondition] = useState('HOT_HOLD');
  const [storageTemp, setStorageTemp] = useState('65.0');
  const [hoursAgo, setHoursAgo] = useState('1.5');
  const [handlerDeclaration, setHandlerDeclaration] = useState(true);
  const [allergens, setAllergens] = useState('dairy');
  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  // Forecast simulator state
  const [simPrepKg, setSimPrepKg] = useState('28.0');
  const [simDate, setSimDate] = useState('2026-11-03');

  const loadDonations = async () => {
    try {
      setLoading(true);
      const data = await api.listDonations();
      setDonations(data);
    } catch (err: any) {
      console.error('Failed to load donations:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDonations();
  }, []);

  // Compute live safety check in client
  const tempNum = parseFloat(storageTemp) || 0;
  const hoursNum = parseFloat(hoursAgo) || 0;
  const isHotHold = storageCondition === 'HOT_HOLD';
  const isRefrig = storageCondition === 'REFRIGERATED';

  const timeOk = hoursNum <= (foodCategory === 'COOKED_MEALS' ? 4 : 12);
  const tempOk = isHotHold ? tempNum >= 60.0 : isRefrig ? tempNum <= 5.0 : true;
  const isEligible = timeOk && tempOk && handlerDeclaration;

  const handleRunForecast = async () => {
    try {
      setForecastLoading(true);
      const result = await api.predictSurplus({
        prediction_date: `${simDate}T12:00:00Z`,
        prepared_quantity_kg: parseFloat(simPrepKg) || 25.0,
      });
      setForecastResult(result);
    } catch (err: any) {
      console.error('Forecast error:', err);
    } finally {
      setForecastLoading(false);
    }
  };

  const handleCreateDonation = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isEligible) {
      setErrorMsg('Cannot publish: food safety requirements are not met according to FSSAI protocols.');
      return;
    }

    try {
      setSubmitting(true);
      setErrorMsg('');

      const prepDt = new Date(Date.now() - hoursNum * 3600 * 1000).toISOString();
      const deadline = new Date(Date.now() + 3.5 * 3600 * 1000).toISOString();

      await api.createDonation({
        food_name: foodName,
        food_category: foodCategory as any,
        quantity_kg: parseFloat(quantityKg),
        servings: parseInt(servings, 10),
        storage_condition: storageCondition as any,
        storage_temp_celsius: tempNum,
        preparation_datetime: prepDt,
        collection_deadline: deadline,
        pickup_address: 'Plot 42, Hill Road, Bandra West, Mumbai',
        pickup_city: 'Mumbai',
        pickup_pincode: '400050',
        safety_confirmed: true,
        handler_declaration: handlerDeclaration,
        allergens: allergens ? allergens.split(',').map(s => s.trim()) : [],
      });

      confetti({
        particleCount: 60,
        spread: 60,
        origin: { y: 0.7 },
      });

      setShowWizard(false);
      loadDonations();
      onRefreshStats();
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to publish donation');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* ── Top Bar ── */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.75rem', marginBottom: '0.25rem' }}>Restaurant Kitchen Operations</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Active kitchen: <strong>The Spice Craft (Bandra West)</strong> • FSSAI License: 11521012000456
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button className="btn btn-secondary" onClick={loadDonations}>
            <RefreshCw size={16} />
            <span>Refresh</span>
          </button>
          <button className="btn btn-primary" onClick={() => setShowWizard(true)}>
            <PlusCircle size={18} />
            <span>List Surplus for Rescue</span>
          </button>
        </div>
      </div>

      {/* ── AI Demand & Surplus Forecaster Card ── */}
      <div className="glass-panel highlighted">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{ width: '40px', height: '40px', borderRadius: 'var(--radius-md)', background: 'rgba(16, 185, 129, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#10b981' }}>
              <Sparkles size={20} />
            </div>
            <div>
              <h3 style={{ fontSize: '1.2rem', marginBottom: '0.15rem' }}>AI Kitchen Demand & Surplus Predictor</h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Powered by trained Random Forest & Gradient Boosting models with Mumbai weather data
              </p>
            </div>
          </div>
          <span className="badge badge-published">Model: v1.0.0 Active</span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', alignItems: 'flex-end', marginBottom: '1.5rem' }}>
          <div>
            <label className="form-label">Simulation Date</label>
            <input 
              type="date" 
              className="form-input" 
              value={simDate}
              onChange={(e) => setSimDate(e.target.value)}
            />
          </div>
          <div>
            <label className="form-label">Planned Kitchen Prep (kg)</label>
            <input 
              type="number" 
              className="form-input" 
              value={simPrepKg}
              onChange={(e) => setSimPrepKg(e.target.value)}
              step="0.5"
            />
          </div>
          <div>
            <button 
              className="btn btn-primary" 
              onClick={handleRunForecast} 
              disabled={forecastLoading}
              style={{ width: '100%' }}
            >
              {forecastLoading ? <RefreshCw size={16} className="spin" /> : <Sparkles size={16} />}
              <span>Generate Forecast</span>
            </button>
          </div>
        </div>

        {forecastResult && (
          <div style={{ background: 'rgba(255, 255, 255, 0.03)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '1.25rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem' }}>
            <div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>Predicted Customer Demand</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-primary-light)' }}>
                {forecastResult.predicted_demand_kg.toFixed(1)} kg
              </div>
            </div>

            <div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>Estimated Surplus Buffer</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 700, color: forecastResult.predicted_surplus_kg > 5 ? '#f59e0b' : '#34d399' }}>
                {forecastResult.predicted_surplus_kg.toFixed(1)} kg
              </div>
            </div>

            <div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>Predicted Spoilage Risk</div>
              <div>
                <span className={`badge badge-risk-${forecastResult.waste_risk.toLowerCase()}`}>
                  {forecastResult.waste_risk} RISK
                </span>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center' }}>
              {forecastResult.waste_risk === 'HIGH' ? (
                <div style={{ fontSize: '0.78rem', color: '#fb7185', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <AlertTriangle size={16} />
                  <span>High surplus likelihood. Reduce batch size or pre-schedule NGO pickup!</span>
                </div>
              ) : (
                <div style={{ fontSize: '0.78rem', color: '#34d399', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <CheckCircle2 size={16} />
                  <span>Optimal batch size. Expected waste is within safe margins.</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* ── Active Listings Table ── */}
      <div className="glass-panel">
        <h3 style={{ fontSize: '1.25rem', marginBottom: '1rem' }}>Recent Food Redistribution Listings</h3>

        {loading ? (
          <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
            Loading active kitchen donations...
          </div>
        ) : donations.length === 0 ? (
          <div style={{ padding: '2.5rem', textAlign: 'center' }}>
            <Utensils size={36} color="var(--text-muted)" style={{ margin: '0 auto 1rem' }} />
            <p style={{ color: 'var(--text-secondary)' }}>No active surplus listings. Click "List Surplus for Rescue" above to publish.</p>
          </div>
        ) : (
          <div className="data-table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Food Item</th>
                  <th>Category</th>
                  <th>Quantity</th>
                  <th>Temp / Storage</th>
                  <th>Safety Verified</th>
                  <th>Status</th>
                  <th>Assigned Volunteer</th>
                </tr>
              </thead>
              <tbody>
                {donations.map((d) => (
                  <tr key={d.id}>
                    <td>
                      <strong style={{ color: 'var(--text-main)' }}>{d.food_name}</strong>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {d.servings ? `${d.servings} portions` : 'Commercial batch'}
                      </div>
                    </td>
                    <td>{d.food_category.replace('_', ' ')}</td>
                    <td><strong>{d.quantity_kg} kg</strong></td>
                    <td>
                      <span style={{ fontSize: '0.82rem' }}>
                        {d.storage_temp_celsius ? `${d.storage_temp_celsius}°C` : 'N/A'} • {d.storage_condition || 'Standard'}
                      </span>
                    </td>
                    <td>
                      {d.is_eligible !== false ? (
                        <span style={{ color: '#34d399', display: 'inline-flex', alignItems: 'center', gap: '0.3rem', fontSize: '0.8rem', fontWeight: 600 }}>
                          <ShieldCheck size={16} /> FSSAI Pass
                        </span>
                      ) : (
                        <span style={{ color: '#fb7185', display: 'inline-flex', alignItems: 'center', gap: '0.3rem', fontSize: '0.8rem', fontWeight: 600 }}>
                          <AlertTriangle size={16} /> Failed Check
                        </span>
                      )}
                    </td>
                    <td>
                      <span className={`badge badge-${d.status.toLowerCase()}`}>
                        {d.status}
                      </span>
                    </td>
                    <td>
                      {d.delivery?.volunteer_id ? (
                        <span style={{ color: 'var(--color-primary-light)', fontSize: '0.82rem', fontWeight: 600 }}>
                          Rahul Sharma ({d.delivery.status})
                        </span>
                      ) : (
                        <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>Pending NGO claim</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* ── Modal: Rescue Surplus Food Wizard ── */}
      {showWizard && (
        <div className="modal-overlay">
          <div className="modal-card">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <ShieldCheck size={24} color="#10b981" />
                <h3 style={{ fontSize: '1.35rem' }}>Publish Surplus Food Parcel</h3>
              </div>
              <button 
                onClick={() => setShowWizard(false)}
                style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
              >
                <X size={20} />
              </button>
            </div>

            {errorMsg && (
              <div style={{ background: 'rgba(244, 63, 94, 0.15)', border: '1px solid rgba(244, 63, 94, 0.3)', padding: '0.85rem', borderRadius: 'var(--radius-md)', color: '#fb7185', fontSize: '0.85rem', marginBottom: '1.25rem' }}>
                {errorMsg}
              </div>
            )}

            <form onSubmit={handleCreateDonation}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                <div>
                  <label className="form-label">Food Dish Name *</label>
                  <input 
                    type="text" 
                    className="form-input" 
                    value={foodName} 
                    onChange={e => setFoodName(e.target.value)} 
                    required 
                  />
                </div>
                <div>
                  <label className="form-label">Food Category *</label>
                  <select 
                    className="form-select" 
                    value={foodCategory} 
                    onChange={e => setFoodCategory(e.target.value)}
                  >
                    <option value="COOKED_MEALS">Cooked Meals (Rice/Curry/Pasta)</option>
                    <option value="BAKERY">Bakery & Breads</option>
                    <option value="RAW_PRODUCE">Raw Produce / Vegetables</option>
                    <option value="DESSERTS">Desserts & Confectionery</option>
                    <option value="PACKAGED_FOOD">Packaged Goods</option>
                  </select>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                <div>
                  <label className="form-label">Quantity (kg) *</label>
                  <input 
                    type="number" 
                    className="form-input" 
                    value={quantityKg} 
                    onChange={e => setQuantityKg(e.target.value)} 
                    step="0.5" 
                    required 
                  />
                </div>
                <div>
                  <label className="form-label">Estimated Servings</label>
                  <input 
                    type="number" 
                    className="form-input" 
                    value={servings} 
                    onChange={e => setServings(e.target.value)} 
                  />
                </div>
              </div>

              {/* Food Safety Section */}
              <div style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '1.25rem', marginBottom: '1.25rem' }}>
                <h4 style={{ fontSize: '0.95rem', marginBottom: '1rem', color: 'var(--color-primary-light)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <ShieldCheck size={18} />
                  <span>Mandatory Food Safety Checks (FSSAI Criteria)</span>
                </h4>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                  <div>
                    <label className="form-label">Storage Holding Condition</label>
                    <select 
                      className="form-select" 
                      value={storageCondition} 
                      onChange={e => setStorageCondition(e.target.value)}
                    >
                      <option value="HOT_HOLD">Hot Holding (≥ 60°C)</option>
                      <option value="REFRIGERATED">Refrigerated (≤ 5°C)</option>
                      <option value="ROOM_TEMPERATURE">Ambient / Room Temperature</option>
                    </select>
                  </div>
                  <div>
                    <label className="form-label">Measured Temperature (°C)</label>
                    <input 
                      type="number" 
                      className="form-input" 
                      value={storageTemp} 
                      onChange={e => setStorageTemp(e.target.value)} 
                      step="0.1" 
                    />
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                  <div>
                    <label className="form-label">Hours Since Cooked/Baked</label>
                    <input 
                      type="number" 
                      className="form-input" 
                      value={hoursAgo} 
                      onChange={e => setHoursAgo(e.target.value)} 
                      step="0.5" 
                    />
                  </div>
                  <div>
                    <label className="form-label">Allergens Declared</label>
                    <input 
                      type="text" 
                      className="form-input" 
                      value={allergens} 
                      onChange={e => setAllergens(e.target.value)} 
                      placeholder="e.g. dairy, gluten, nuts"
                    />
                  </div>
                </div>

                <label style={{ display: 'flex', alignItems: 'flex-start', gap: '0.6rem', cursor: 'pointer', fontSize: '0.85rem' }}>
                  <input 
                    type="checkbox" 
                    checked={handlerDeclaration} 
                    onChange={e => setHandlerDeclaration(e.target.checked)} 
                    style={{ marginTop: '0.2rem' }}
                  />
                  <span>
                    I certify that food handlers wore clean hairnets and food-grade gloves, food is packed in food-grade sealed containers, and holding temperatures were maintained continuously.
                  </span>
                </label>
              </div>

              {/* Safety Feedback Badge */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', background: isEligible ? 'rgba(16, 185, 129, 0.1)' : 'rgba(244, 63, 94, 0.1)', padding: '0.75rem 1rem', borderRadius: 'var(--radius-md)' }}>
                <span style={{ fontSize: '0.85rem', color: isEligible ? '#34d399' : '#fb7185', fontWeight: 600 }}>
                  {isEligible ? '✓ All safety checks passed. Parcel is eligible for immediate NGO rescue.' : '⚠️ Safety criteria not met. Correct holding temperature or preparation window.'}
                </span>
                <span className={`badge ${isEligible ? 'badge-delivered' : 'badge-risk-high'}`}>
                  {isEligible ? 'FSSAI APPROVED' : 'HOLD FAILED'}
                </span>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowWizard(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary" disabled={submitting || !isEligible}>
                  {submitting ? 'Publishing...' : 'Publish to NGO Network'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
