import type { Activity } from "../types";

const ACTION_ICONS: Record<string, string> = {
  group_created: "🏠",
  member_added: "👤",
  expense_added: "💸",
  expense_voided: "🚫",
  settlement_made: "🤝",
};

function timeAgo(dateStr: string): string {
  const now = Date.now();
  const then = new Date(dateStr).getTime();
  const seconds = Math.floor((now - then) / 1000);

  if (seconds < 60) return "just now";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

interface Props {
  activities: Activity[];
}

export function ActivityFeed({ activities }: Props) {
  if (activities.length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-4">
        <h3 className="text-xs font-medium uppercase tracking-wider text-gray-500 mb-3">
          Activity
        </h3>
        <p className="text-sm text-gray-400">No activity yet</p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <h3 className="text-xs font-medium uppercase tracking-wider text-gray-500 mb-3">
        Activity
      </h3>
      <div className="space-y-2.5">
        {activities.slice(0, 10).map((a) => (
          <div key={a.id} className="flex items-start gap-2.5">
            <span className="mt-0.5 text-sm leading-none">
              {ACTION_ICONS[a.action] || "•"}
            </span>
            <div className="min-w-0 flex-1">
              <p className="text-sm text-gray-700 leading-snug">
                {a.description}
              </p>
              <p className="text-[11px] text-gray-400 mt-0.5">
                {a.created_at ? timeAgo(a.created_at) : ""}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
