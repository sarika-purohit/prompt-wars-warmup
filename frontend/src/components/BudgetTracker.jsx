/**
 * BudgetTracker — Visual budget breakdown with progress bar.
 */

import './BudgetTracker.css';

export default function BudgetTracker({ itinerary }) {
  if (!itinerary) return null;

  const { total_cost, budget, currency, budget_utilization } = itinerary;
  const percentage = budget_utilization || Math.min((total_cost / budget) * 100, 100);
  const remaining = budget - total_cost;
  const isOverBudget = remaining < 0;

  // Calculate per-category spend
  const categories = {};
  for (const day of itinerary.days || []) {
    for (const activity of [...(day.activities || []), ...(day.meals || [])]) {
      const cat = activity.category || 'other';
      categories[cat] = (categories[cat] || 0) + (activity.estimated_cost || 0);
    }
  }

  const categoryColors = {
    culture: '#6366f1',
    food: '#f59e0b',
    adventure: '#ef4444',
    nature: '#10b981',
    shopping: '#ec4899',
    relaxation: '#8b5cf6',
    nightlife: '#f97316',
    history: '#38bdf8',
    other: '#64748b',
  };

  return (
    <div className="budget-tracker card animate-fade-in" role="region" aria-label="Budget overview">
      <h3 className="budget-title">💰 Budget Overview</h3>

      {/* Progress bar */}
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
        <div className="budget-bar-labels">
          <span className="budget-spent">
            {currency} {total_cost.toLocaleString()}
          </span>
          <span className="budget-total">
            of {currency} {budget.toLocaleString()}
          </span>
        </div>
      </div>

      {/* Remaining */}
      <div className={`budget-remaining ${isOverBudget ? 'over' : ''}`}>
        <span>{isOverBudget ? '⚠️ Over budget by' : '✅ Remaining'}</span>
        <span className="budget-remaining-amount">
          {currency} {Math.abs(remaining).toLocaleString()}
        </span>
      </div>

      {/* Category breakdown */}
      {Object.keys(categories).length > 0 && (
        <div className="budget-categories">
          <h4>Spending Breakdown</h4>
          <div className="category-bars">
            {Object.entries(categories)
              .sort(([, a], [, b]) => b - a)
              .map(([cat, amount]) => (
                <div key={cat} className="category-row">
                  <span className="category-label">{cat}</span>
                  <div className="category-bar-track">
                    <div
                      className="category-bar-fill"
                      style={{
                        width: `${(amount / total_cost) * 100}%`,
                        background: categoryColors[cat] || categoryColors.other,
                      }}
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
