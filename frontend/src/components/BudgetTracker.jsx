/**
 * BudgetTracker.jsx — Visual budget breakdown with progress bar.
 *
 * Displays the trip's total cost vs. budget with:
 *   - A progress bar showing budget utilization percentage.
 *   - Remaining/over-budget indicator.
 *   - Per-category spending breakdown (food, culture, nature, etc.).
 *
 * Accessibility:
 *   - Progress bar uses role="progressbar" with aria-valuenow.
 *   - Budget region has aria-label for screen readers.
 *   - Over-budget state is visually and semantically distinct.
 *
 * @component
 * @param {Object} props
 * @param {Object} props.itinerary - The generated itinerary with cost data.
 */

import './BudgetTracker.css';

export default function BudgetTracker({ itinerary }) {
  // Guard: don't render without itinerary data
  if (!itinerary) return null;

  const { total_cost, budget, currency, budget_utilization } = itinerary;

  // Calculate budget usage percentage (cap at 100% for progress bar width)
  const percentage = budget_utilization || Math.min((total_cost / budget) * 100, 100);
  const remaining = budget - total_cost;
  const isOverBudget = remaining < 0;

  // EFFICIENCY: Calculate per-category spending in a single pass
  const categories = {};
  for (const day of itinerary.days || []) {
    for (const activity of [...(day.activities || []), ...(day.meals || [])]) {
      const cat = activity.category || 'other';
      categories[cat] = (categories[cat] || 0) + (activity.estimated_cost || 0);
    }
  }

  // Color mapping for spending categories — visually distinct palette
  const categoryColors = {
    culture: '#6366f1',    // Indigo
    food: '#f59e0b',       // Amber
    adventure: '#ef4444',  // Red
    nature: '#10b981',     // Emerald
    shopping: '#ec4899',   // Pink
    relaxation: '#8b5cf6', // Violet
    nightlife: '#f97316',  // Orange
    history: '#38bdf8',    // Sky blue
    other: '#64748b',      // Slate
  };

  return (
    <div className="budget-tracker card animate-fade-in" role="region" aria-label="Budget overview">
      <h3 className="budget-title">💰 Budget Overview</h3>

      {/* Progress Bar — shows budget utilization */}
      <div className="budget-bar-container">
        <div className="budget-bar-track">
          <div
            className={`budget-bar-fill ${isOverBudget ? 'over-budget' : ''}`}
            style={{ width: `${Math.min(percentage, 100)}%` }}
            role="progressbar"
            aria-valuenow={Math.round(percentage)}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label={`Budget used: ${Math.round(percentage)}%`}
          />
        </div>
        {/* Spent vs. total labels */}
        <div className="budget-bar-labels">
          <span className="budget-spent">
            {currency} {total_cost.toLocaleString()}
          </span>
          <span className="budget-total">
            of {currency} {budget.toLocaleString()}
          </span>
        </div>
      </div>

      {/* Remaining / Over Budget indicator */}
      <div className={`budget-remaining ${isOverBudget ? 'over' : ''}`}>
        <span>{isOverBudget ? '⚠️ Over budget by' : '✅ Remaining'}</span>
        <span className="budget-remaining-amount">
          {currency} {Math.abs(remaining).toLocaleString()}
        </span>
      </div>

      {/* Per-Category Spending Breakdown */}
      {Object.keys(categories).length > 0 && (
        <div className="budget-categories">
          <h4>Spending Breakdown</h4>
          <div className="category-bars" role="list" aria-label="Spending by category">
            {Object.entries(categories)
              .sort(([, a], [, b]) => b - a) // Sort by spend (highest first)
              .map(([cat, amount]) => (
                <div key={cat} className="category-row" role="listitem">
                  <span className="category-label">{cat}</span>
                  <div className="category-bar-track">
                    <div
                      className="category-bar-fill"
                      style={{
                        width: `${(amount / total_cost) * 100}%`,
                        background: categoryColors[cat] || categoryColors.other,
                      }}
                      aria-label={`${cat}: ${currency} ${amount.toLocaleString()}`}
                    />
                  </div>
                  <span className="category-amount">
                    {currency} {amount.toLocaleString()}
                  </span>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}
