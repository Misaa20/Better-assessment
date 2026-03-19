import type { SimplifiedDebt } from "../types";

interface Props {
  debts: SimplifiedDebt[];
  onSettle: (debt: SimplifiedDebt) => void;
}

export function DebtSummary({ debts, onSettle }: Props) {
  if (debts.length === 0) {
    return (
      <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-center text-sm text-emerald-700">
        All settled up
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-gray-200 bg-white">
      <div className="border-b border-gray-100 px-4 py-2.5">
        <h3 className="text-xs font-medium uppercase tracking-wide text-gray-500">
          Settle up
        </h3>
      </div>
      <div className="divide-y divide-gray-50 px-4">
        {debts.map((d, i) => (
          <div key={i} className="flex items-center justify-between gap-2 py-2.5">
            <p className="min-w-0 text-sm text-gray-600">
              <span className="font-medium text-gray-900">
                {d.from_member_name}
              </span>
              {" \u2192 "}
              <span className="font-medium text-gray-900">
                {d.to_member_name}
              </span>
            </p>
            <div className="flex shrink-0 items-center gap-2">
              <span className="font-mono text-sm tabular-nums text-gray-900">
                ${d.amount.toFixed(2)}
              </span>
              <button
                onClick={() => onSettle(d)}
                className="rounded-md border border-gray-300 px-2 py-1 text-xs font-medium text-gray-700 hover:bg-gray-50"
              >
                Settle
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
