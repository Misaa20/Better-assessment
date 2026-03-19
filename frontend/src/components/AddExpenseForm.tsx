import { useState } from "react";
import type { Member, CreateExpensePayload } from "../types";

interface Props {
  groupId: number;
  members: Member[];
  onSubmit: (payload: CreateExpensePayload) => Promise<void>;
}

type SplitType = "equal" | "exact" | "percentage";

const INPUT =
  "w-full rounded-md border border-gray-300 px-3 py-2 text-sm text-gray-900 placeholder-gray-400 focus:border-gray-900 focus:ring-1 focus:ring-gray-900 focus:outline-none";

export function AddExpenseForm({ groupId, members, onSubmit }: Props) {
  const [description, setDescription] = useState("");
  const [amount, setAmount] = useState("");
  const [paidBy, setPaidBy] = useState<number>(members[0]?.id ?? 0);
  const [splitType, setSplitType] = useState<SplitType>("equal");
  const [selectedMembers, setSelectedMembers] = useState<number[]>(
    members.map((m) => m.id)
  );
  const [splitValues, setSplitValues] = useState<Record<number, string>>({});
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const toggleMember = (id: number) => {
    setSelectedMembers((prev) =>
      prev.includes(id) ? prev.filter((m) => m !== id) : [...prev, id]
    );
  };

  const getAutoFilledValue = (memberId: number): string => {
    if (splitType !== "percentage" && splitType !== "exact") return "";

    const otherSelected = selectedMembers.filter((id) => id !== memberId);
    const othersTotal = otherSelected.reduce(
      (sum, id) => sum + (parseFloat(splitValues[id] || "") || 0),
      0
    );

    const target = splitType === "percentage" ? 100 : parseFloat(amount) || 0;
    const remaining = Math.round((target - othersTotal) * 100) / 100;

    const hasOwnValue =
      splitValues[memberId] !== undefined && splitValues[memberId] !== "";
    if (hasOwnValue) return splitValues[memberId];

    const filledOthersCount = otherSelected.filter(
      (id) => splitValues[id] !== undefined && splitValues[id] !== ""
    ).length;

    if (filledOthersCount === otherSelected.length && remaining >= 0) {
      return remaining.toString();
    }
    return "";
  };

  const getRemainingLabel = (): string | null => {
    if (splitType === "equal") return null;
    const total = selectedMembers.reduce(
      (sum, id) => sum + (parseFloat(getAutoFilledValue(id)) || 0),
      0
    );
    const target = splitType === "percentage" ? 100 : parseFloat(amount) || 0;
    const remaining = Math.round((target - total) * 100) / 100;
    if (Math.abs(remaining) < 0.01) return null;
    const unit = splitType === "percentage" ? "%" : "$";
    return `${remaining > 0 ? remaining : 0}${unit} remaining`;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    const amountNum = parseFloat(amount);
    if (!description.trim()) return setError("Description is required.");
    if (isNaN(amountNum) || amountNum <= 0)
      return setError("Amount must be positive.");
    if (selectedMembers.length === 0)
      return setError("Select at least one member.");

    const splits = selectedMembers.map((mid) => {
      const base: { member_id: number; amount?: number; percentage?: number } =
        { member_id: mid };
      const resolvedValue = parseFloat(getAutoFilledValue(mid)) || 0;
      if (splitType === "exact") base.amount = resolvedValue;
      if (splitType === "percentage") base.percentage = resolvedValue;
      return base;
    });

    setSubmitting(true);
    try {
      await onSubmit({
        description: description.trim(),
        amount: amountNum,
        group_id: groupId,
        paid_by: paidBy,
        split_type: splitType,
        splits,
      });
      setDescription("");
      setAmount("");
      setSplitValues({});
    } catch (err: unknown) {
      if (err && typeof err === "object" && "response" in err) {
        const axiosErr = err as { response?: { data?: { error?: string } } };
        setError(axiosErr.response?.data?.error || "Failed to add expense.");
      } else {
        setError("Failed to add expense.");
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="rounded-lg border border-gray-200 bg-white"
    >
      <div className="border-b border-gray-100 px-4 py-2.5">
        <h3 className="text-xs font-medium uppercase tracking-wide text-gray-500">
          Add expense
        </h3>
      </div>

      <div className="space-y-3 p-4">
        {error && (
          <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            {error}
          </div>
        )}

        <input
          type="text"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className={INPUT}
          placeholder="What was it for?"
        />

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="mb-1 block text-xs text-gray-500">Amount</label>
            <div className="relative">
              <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-sm text-gray-400">
                $
              </span>
              <input
                type="number"
                step="0.01"
                min="0.01"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                className={INPUT + " pl-7"}
                placeholder="0.00"
              />
            </div>
          </div>
          <div>
            <label className="mb-1 block text-xs text-gray-500">Paid by</label>
            <select
              value={paidBy}
              onChange={(e) => setPaidBy(Number(e.target.value))}
              className={INPUT}
            >
              {members.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className="mb-1.5 block text-xs text-gray-500">Split</label>
          <div className="inline-flex rounded-md border border-gray-300">
            {(["equal", "exact", "percentage"] as SplitType[]).map(
              (type, i) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => setSplitType(type)}
                  className={`px-3 py-1.5 text-xs font-medium transition-colors ${
                    i > 0 ? "border-l border-gray-300" : ""
                  } ${
                    splitType === type
                      ? "bg-gray-900 text-white"
                      : "text-gray-600 hover:bg-gray-50"
                  } ${i === 0 ? "rounded-l-md" : ""} ${
                    i === 2 ? "rounded-r-md" : ""
                  }`}
                >
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </button>
              )
            )}
          </div>
        </div>

        <div>
          <label className="mb-1.5 block text-xs text-gray-500">
            Split among
          </label>
          <div className="space-y-1.5">
            {members.map((m) => (
              <div key={m.id} className="flex items-center gap-2">
                <label className="flex min-w-0 flex-1 cursor-pointer items-center gap-2">
                  <input
                    type="checkbox"
                    checked={selectedMembers.includes(m.id)}
                    onChange={() => toggleMember(m.id)}
                    className="h-3.5 w-3.5 rounded border-gray-300 text-gray-900 focus:ring-gray-900"
                  />
                  <span className="truncate text-sm text-gray-700">
                    {m.name}
                  </span>
                </label>
                {splitType !== "equal" && selectedMembers.includes(m.id) && (
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    placeholder={splitType === "percentage" ? "%" : "$"}
                    value={getAutoFilledValue(m.id)}
                    onChange={(e) =>
                      setSplitValues((prev) => ({
                        ...prev,
                        [m.id]: e.target.value,
                      }))
                    }
                    className="w-20 rounded-md border border-gray-300 px-2 py-1 text-right text-sm tabular-nums text-gray-900 placeholder-gray-400 focus:border-gray-900 focus:ring-1 focus:ring-gray-900 focus:outline-none"
                  />
                )}
              </div>
            ))}
          </div>
          {getRemainingLabel() && (
            <p className="mt-1.5 text-xs text-amber-600">
              {getRemainingLabel()}
            </p>
          )}
        </div>

        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-md bg-gray-900 py-2 text-sm font-medium text-white hover:bg-gray-800 disabled:opacity-50"
        >
          {submitting ? "Adding..." : "Add expense"}
        </button>
      </div>
    </form>
  );
}
