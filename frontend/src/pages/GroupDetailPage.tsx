import { useParams, Link } from "react-router-dom";
import { groupsApi, expensesApi, settlementsApi } from "../api/client";
import { useApi } from "../hooks/useApi";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { ErrorMessage } from "../components/ErrorMessage";
import { BalanceCard } from "../components/BalanceCard";
import { DebtSummary } from "../components/DebtSummary";
import { ExpenseList } from "../components/ExpenseList";
import { AddExpenseForm } from "../components/AddExpenseForm";
import { ActivityFeed } from "../components/ActivityFeed";
import { GroupStatsCard } from "../components/GroupStatsCard";
import { SettlementHistory } from "../components/SettlementHistory";
import { AddMemberForm } from "../components/AddMemberForm";
import { colorForName, initials } from "../utils/memberColor";
import type { SimplifiedDebt, CreateExpensePayload } from "../types";

export function GroupDetailPage() {
  const { groupId } = useParams<{ groupId: string }>();
  const id = Number(groupId);

  const {
    data: group,
    status: groupStatus,
    error: groupError,
  } = useApi(() => groupsApi.get(id), [id]);

  const {
    data: expenses,
    status: expenseStatus,
    reload: reloadExpenses,
  } = useApi(() => expensesApi.listByGroup(id), [id]);

  const { data: balanceData, reload: reloadBalances } = useApi(
    () => groupsApi.getBalances(id),
    [id]
  );

  const {
    data: settlements,
    reload: reloadSettlements,
  } = useApi(() => settlementsApi.listByGroup(id), [id]);

  const { data: activities, reload: reloadActivity } = useApi(
    () => groupsApi.getActivity(id),
    [id]
  );

  const { data: stats, reload: reloadStats } = useApi(
    () => groupsApi.getStats(id),
    [id]
  );

  const reloadAll = () => {
    reloadExpenses();
    reloadBalances();
    reloadSettlements();
    reloadActivity();
    reloadStats();
  };

  const handleAddExpense = async (payload: CreateExpensePayload) => {
    await expensesApi.create(payload);
    reloadAll();
  };

  const handleVoidExpense = async (expenseId: number) => {
    await expensesApi.void(expenseId);
    reloadAll();
  };

  const handleSettle = async (debt: SimplifiedDebt) => {
    await settlementsApi.create({
      group_id: id,
      paid_by: debt.from_member_id,
      paid_to: debt.to_member_id,
      amount: debt.amount,
    });
    reloadAll();
  };

  const handleAddMember = async (name: string) => {
    await groupsApi.addMember(id, name);
    window.location.reload();
  };

  if (groupStatus === "loading") return <LoadingSpinner />;
  if (groupStatus === "error")
    return (
      <div className="mx-auto max-w-4xl px-4 py-8">
        <ErrorMessage message={groupError || "Failed to load group."} />
      </div>
    );
  if (!group) return null;

  return (
    <div className="mx-auto max-w-4xl px-4 py-6">
      <div className="mb-5">
        <Link
          to="/"
          className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-900"
        >
          <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
          Groups
        </Link>
      </div>

      <div className="mb-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-xl font-semibold text-gray-900">{group.name}</h1>
            <div className="mt-2 flex items-center gap-1.5">
              {group.members.map((m) => {
                const c = colorForName(m.name);
                return (
                  <span
                    key={m.id}
                    title={m.name}
                    className={`inline-flex h-6 w-6 items-center justify-center rounded-full text-[10px] font-medium ${c.bg} ${c.text}`}
                  >
                    {initials(m.name)}
                  </span>
                );
              })}
              <span className="ml-1 text-xs text-gray-400">
                {group.members.length} members
              </span>
            </div>
          </div>
        </div>
        <div className="mt-3 max-w-xs">
          <AddMemberForm onAdd={handleAddMember} />
        </div>
      </div>

      <div className="grid gap-5 lg:grid-cols-5">
        <div className="space-y-4 lg:col-span-2">
          {stats && <GroupStatsCard stats={stats} />}
          {balanceData && (
            <>
              <BalanceCard balances={balanceData.balances} />
              <DebtSummary
                debts={balanceData.simplified_debts}
                onSettle={handleSettle}
              />
            </>
          )}
          <SettlementHistory settlements={settlements || []} />
          {activities && <ActivityFeed activities={activities} />}
        </div>

        <div className="space-y-4 lg:col-span-3">
          <AddExpenseForm
            groupId={id}
            members={group.members}
            onSubmit={handleAddExpense}
          />

          {expenseStatus === "loading" ? (
            <LoadingSpinner />
          ) : (
            <ExpenseList
              expenses={expenses || []}
              onVoid={handleVoidExpense}
            />
          )}
        </div>
      </div>
    </div>
  );
}
