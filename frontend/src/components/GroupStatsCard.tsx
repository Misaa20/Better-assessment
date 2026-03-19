import type { GroupStats } from "../types";
import { colorForName, initials } from "../utils/memberColor";

interface Props {
  stats: GroupStats;
}

export function GroupStatsCard({ stats }: Props) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <h3 className="text-xs font-medium uppercase tracking-wider text-gray-500 mb-3">
        Overview
      </h3>

      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="rounded-md bg-gray-50 p-3">
          <p className="text-[11px] uppercase tracking-wider text-gray-400">
            Total spent
          </p>
          <p className="text-lg font-semibold text-gray-900">
            ${stats.total_spent.toFixed(2)}
          </p>
        </div>
        <div className="rounded-md bg-gray-50 p-3">
          <p className="text-[11px] uppercase tracking-wider text-gray-400">
            Expenses
          </p>
          <p className="text-lg font-semibold text-gray-900">
            {stats.expense_count}
          </p>
        </div>
      </div>

      {stats.member_spending.length > 0 && (
        <div>
          <p className="text-[11px] uppercase tracking-wider text-gray-400 mb-2">
            Per-member share
          </p>
          <div className="space-y-1.5">
            {stats.member_spending.map((ms) => {
              const c = colorForName(ms.member_name);
              const pct =
                stats.total_spent > 0
                  ? (ms.total_owed / stats.total_spent) * 100
                  : 0;
              return (
                <div key={ms.member_id} className="flex items-center gap-2">
                  <span
                    className={`inline-flex h-5 w-5 items-center justify-center rounded-full text-[9px] font-medium ${c.bg} ${c.text}`}
                  >
                    {initials(ms.member_name)}
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-600 truncate">
                        {ms.member_name}
                      </span>
                      <span className="text-gray-900 font-medium ml-2">
                        ${ms.total_owed.toFixed(2)}
                      </span>
                    </div>
                    <div className="mt-0.5 h-1 rounded-full bg-gray-100 overflow-hidden">
                      <div
                        className="h-full rounded-full bg-indigo-400"
                        style={{ width: `${Math.min(pct, 100)}%` }}
                      />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
