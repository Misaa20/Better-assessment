import type { Settlement } from "../types";
import { colorForName, initials } from "../utils/memberColor";

interface Props {
  settlements: Settlement[];
}

export function SettlementHistory({ settlements }: Props) {
  if (settlements.length === 0) return null;

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <h3 className="text-xs font-medium uppercase tracking-wider text-gray-500 mb-3">
        Settlements
      </h3>
      <div className="space-y-2">
        {settlements.map((s) => {
          const fromColor = colorForName(s.paid_by_name);
          const toColor = colorForName(s.paid_to_name);
          return (
            <div
              key={s.id}
              className="flex items-center gap-2 rounded-md bg-gray-50 px-3 py-2"
            >
              <span
                className={`inline-flex h-5 w-5 items-center justify-center rounded-full text-[9px] font-medium ${fromColor.bg} ${fromColor.text}`}
              >
                {initials(s.paid_by_name)}
              </span>
              <span className="text-xs text-gray-500">paid</span>
              <span className="text-xs font-medium text-gray-900">
                ${s.amount.toFixed(2)}
              </span>
              <span className="text-xs text-gray-500">to</span>
              <span
                className={`inline-flex h-5 w-5 items-center justify-center rounded-full text-[9px] font-medium ${toColor.bg} ${toColor.text}`}
              >
                {initials(s.paid_to_name)}
              </span>
              <span className="text-xs text-gray-500 ml-auto">
                {new Date(s.created_at).toLocaleDateString()}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
