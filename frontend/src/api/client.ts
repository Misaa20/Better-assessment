import axios from "axios";
import type {
  Group,
  Expense,
  Settlement,
  BalanceDetails,
  CreateGroupPayload,
  CreateExpensePayload,
  CreateSettlementPayload,
  Member,
  Activity,
  GroupStats,
} from "../types";

const api = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
});

export const groupsApi = {
  list: () => api.get<{ groups: Group[] }>("/groups").then((r) => r.data.groups),

  get: (id: number) => api.get<Group>(`/groups/${id}`).then((r) => r.data),

  create: (data: CreateGroupPayload) =>
    api.post<Group>("/groups", data).then((r) => r.data),

  delete: (id: number) => api.delete(`/groups/${id}`),

  addMember: (groupId: number, name: string) =>
    api
      .post<Member>(`/groups/${groupId}/members`, { name })
      .then((r) => r.data),

  getBalances: (groupId: number) =>
    api
      .get<BalanceDetails>(`/groups/${groupId}/balances`)
      .then((r) => r.data),

  getActivity: (groupId: number) =>
    api
      .get<{ activities: Activity[] }>(`/groups/${groupId}/activity`)
      .then((r) => r.data.activities),

  getStats: (groupId: number) =>
    api
      .get<GroupStats>(`/groups/${groupId}/stats`)
      .then((r) => r.data),
};

export const expensesApi = {
  listByGroup: (groupId: number) =>
    api
      .get<{ expenses: Expense[] }>(`/expenses/group/${groupId}`)
      .then((r) => r.data.expenses),

  create: (data: CreateExpensePayload) =>
    api.post<Expense>("/expenses", data).then((r) => r.data),

  void: (id: number) =>
    api.post<Expense>(`/expenses/${id}/void`).then((r) => r.data),
};

export const settlementsApi = {
  listByGroup: (groupId: number) =>
    api
      .get<{ settlements: Settlement[] }>(`/settlements/group/${groupId}`)
      .then((r) => r.data.settlements),

  create: (data: CreateSettlementPayload) =>
    api.post<Settlement>("/settlements", data).then((r) => r.data),
};
