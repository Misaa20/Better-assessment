import type { MemberBalance } from "../types";
import { colorForName, initials } from "../utils/memberColor";

interface Props {
  balances: MemberBalance[];
}

export function BalanceCard({ balances }: Props) {
  const maxAbs = Math.max(...balances.map((b) => Math.abs(b.balance)), 1);

  return (
    <div className="rounded-lg border border-gray-200 bg-white">
      <div className="border-b border-gray-100 px-4 py-2.5">
        <h3 className="text-xs font-medium uppercase tracking-wide text-gray-500">
          Balances
        </h3>
      </div>
      <div className="divide-y divide-gray-50 px-4">
        {balances.map((b) => {
          const c = colorForName(b.member_name);
          const pct = Math.abs(b.balance) / maxAbs;
          return (
            <div key={b.member_id} className="flex items-center gap-3 py-2.5">
              <span
                className={`inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-[10px] font-medium ${c.bg} ${c.text}`}
              >
                {initials(b.member_name)}
              </span>
              <span className="min-w-0 flex-1 truncate text-sm text-gray-700">
                {b.member_name}
              </span>
              <div className="flex items-center gap-2">
                <div className="hidden w-16 sm:block">
                  <div className="h-1.5 w-full overflow-hidden rounded-full bg-gray-100">
                    <div
                      className={`h-full rounded-full transition-all ${
                        b.balance > 0.01
                          ? "bg-emerald-400"
                          : b.balance < -0.01
                            ? "bg-red-400"
                            : "bg-gray-200"
                      }`}
                      style={{ width: `${Math.max(pct * 100, 4)}%` }}
                    />
                  </div>
                </div>
                <span
                  className={`w-20 text-right font-mono text-sm tabular-nums ${
                    b.balance > 0.01
                      ? "text-emerald-600"
                      : b.balance < -0.01
                        ? "text-red-600"
                        : "text-gray-400"
                  }`}
                >
                  {b.balance > 0 ? "+" : ""}
                  ${b.balance.toFixed(2)}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
