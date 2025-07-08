import { Plan } from '../../types/plan';
import { Button } from '../ui/button';
import { Trash2 } from 'lucide-react';

interface PlanListProps {
  plans: Plan[];
  loading: boolean;
  error: string | null;
  onSelectPlan: (plan: Plan) => void;
  onDeletePlan: (id: string) => void;
  selectedPlan: Plan | null;
}

export function PlanList({ 
  plans, 
  loading, 
  error, 
  onSelectPlan, 
  onDeletePlan,
  selectedPlan 
}: PlanListProps) {
  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-gray-500">Loading plans...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
        <div className="text-red-800">Error: {error}</div>
      </div>
    );
  }

  if (plans.length === 0) {
    return (
      <div className="p-8 text-center">
        <div className="text-gray-500 mb-2">No plans</div>
        <div className="text-sm text-gray-400">
          Plans will appear here when created through MCP tools.
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">
          Plans ({plans.length})
        </h2>
      </div>
      
      <div className="space-y-3">
        {plans.map((plan) => (
          <div
            key={plan.id}
            className={`bg-white border rounded-lg p-4 transition-colors cursor-pointer hover:bg-gray-50 ${
              selectedPlan?.id === plan.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
            }`}
            onClick={() => onSelectPlan(plan)}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-900">{plan.title}</span>
              <div className="flex items-center gap-2">
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                  plan.status === 'active' ? 'bg-green-100 text-green-800' :
                  plan.status === 'completed' ? 'bg-blue-100 text-blue-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {plan.status}
                </span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeletePlan(plan.id);
                  }}
                  className="h-6 w-6 p-0 text-red-500 hover:text-red-700 hover:bg-red-50"
                >
                  <Trash2 className="h-3 w-3" />
                </Button>
              </div>
            </div>
            
            {plan.description && (
              <p className="text-sm text-gray-600 mb-2">{plan.description}</p>
            )}
            
            <div className="text-xs text-gray-500">
              Created: {new Date(plan.created_at).toLocaleString()}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
