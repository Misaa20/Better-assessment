export interface Member {
  id: number;
  name: string;
  group_id: number;
  created_at: string;
}

export interface Group {
  id: number;
  name: string;
  created_at: string;
  members: Member[];
}

export interface ExpenseSplit {
  id: number;
  member_id: number;
  member_name: string;
  amount: number;
}

export interface Expense {
  id: number;
  description: string;
  amount: number;
  split_type: "equal" | "exact" | "percentage";
  status: "active" | "voided";
  group_id: number;
  paid_by: number;
  paid_by_name: string;
  created_at: string;
  splits: ExpenseSplit[];
}

export interface MemberBalance {
  member_id: number;
  member_name: string;
  balance: number;
}

export interface SimplifiedDebt {
  from_member_id: number;
  from_member_name: string;
  to_member_id: number;
  to_member_name: string;
  amount: number;
}

export interface BalanceDetails {
  balances: MemberBalance[];
  simplified_debts: SimplifiedDebt[];
}

export interface Settlement {
  id: number;
  amount: number;
  group_id: number;
  paid_by: number;
  paid_by_name: string;
  paid_to: number;
  paid_to_name: string;
  created_at: string;
}

export interface CreateGroupPayload {
  name: string;
  members: string[];
}

export interface SplitInput {
  member_id: number;
  amount?: number;
  percentage?: number;
}

export interface CreateExpensePayload {
  description: string;
  amount: number;
  group_id: number;
  paid_by: number;
  split_type: "equal" | "exact" | "percentage";
  splits: SplitInput[];
}

export interface CreateSettlementPayload {
  group_id: number;
  paid_by: number;
  paid_to: number;
  amount: number;
}

export interface Activity {
  id: number;
  action: string;
  description: string;
  created_at: string;
}

export interface GroupStats {
  total_spent: number;
  expense_count: number;
  member_spending: {
    member_id: number;
    member_name: string;
    total_owed: number;
  }[];
}

export interface ApiError {
  error: string;
  code?: string;
  details?: Record<string, string[]>;
}
