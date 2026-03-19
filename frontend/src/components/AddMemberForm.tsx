import { useState } from "react";

interface Props {
  onAdd: (name: string) => Promise<void>;
}

const INPUT =
  "w-full rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm text-gray-900 placeholder-gray-400 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500";

export function AddMemberForm({ onAdd }: Props) {
  const [name, setName] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = name.trim();
    if (!trimmed) return;

    setSubmitting(true);
    setError("");
    try {
      await onAdd(trimmed);
      setName("");
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Failed to add member";
      setError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex items-center gap-2">
      <input
        type="text"
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="New member name"
        className={INPUT}
      />
      <button
        type="submit"
        disabled={submitting || !name.trim()}
        className="whitespace-nowrap rounded-md bg-gray-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-gray-800 disabled:opacity-40"
      >
        {submitting ? "..." : "Add"}
      </button>
      {error && <span className="text-xs text-red-600">{error}</span>}
    </form>
  );
}
