import type { Expense } from "../types";

interface Props {
  expenses: Expense[];
  onVoid: (id: number) => void;
}

export function ExpenseList({ expenses, onVoid }: Props) {
  if (expenses.length === 0) {
    return (
      <p className="py-8 text-center text-sm text-gray-400">
        No expenses yet
      </p>
    );
  }

  return (
    <div className="rounded-lg border border-gray-200 bg-white">
      <div className="border-b border-gray-100 px-4 py-2.5">
        <h3 className="text-xs font-medium uppercase tracking-wide text-gray-500">
          Expenses
        </h3>
      </div>
      <div className="divide-y divide-gray-100">
        {expenses.map((expense) => (
          <div
            key={expense.id}
            className={`px-4 py-3 ${expense.status === "voided" ? "opacity-50" : ""}`}
          >
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <div className="flex items-center gap-1.5">
                  <span className="text-sm font-medium text-gray-900 truncate">
                    {expense.description}
                  </span>
                  {expense.status === "voided" && (
                    <span className="rounded bg-red-50 px-1 py-0.5 text-[10px] font-medium uppercase text-red-500">
                      Void
                    </span>
                  )}
                </div>
                <p className="mt-0.5 text-xs text-gray-500">
                  {expense.paid_by_name} paid &middot;{" "}
                  <span className="capitalize">{expense.split_type}</span> split
                </p>
              </div>
              <div className="flex shrink-0 items-center gap-2">
                <span className="font-mono text-sm tabular-nums text-gray-900">
                  ${expense.amount.toFixed(2)}
                </span>
                {expense.status === "active" && (
                  <button
                    onClick={() => onVoid(expense.id)}
                    className="rounded border border-gray-200 px-1.5 py-0.5 text-[11px] text-gray-400 hover:border-red-200 hover:text-red-500"
                  >
                    void
                  </button>
                )}
              </div>
            </div>
            <div className="mt-2 flex flex-wrap gap-x-3 gap-y-0.5">
              {expense.splits.map((s) => (
                <span key={s.id} className="text-xs text-gray-400">
                  {s.member_name}{" "}
                  <span className="font-mono tabular-nums">${s.amount.toFixed(2)}</span>
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
