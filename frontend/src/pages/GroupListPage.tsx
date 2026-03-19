import { useState } from "react";
import { Link } from "react-router-dom";
import { groupsApi } from "../api/client";
import { useApi } from "../hooks/useApi";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { ErrorMessage } from "../components/ErrorMessage";
import { colorForName, initials } from "../utils/memberColor";

export function GroupListPage() {
  const { data: groups, status, error, reload } = useApi(() => groupsApi.list());

  const [name, setName] = useState("");
  const [memberInput, setMemberInput] = useState("");
  const [formError, setFormError] = useState("");
  const [creating, setCreating] = useState(false);
  const [showForm, setShowForm] = useState(false);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError("");

    const members = memberInput
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);

    if (!name.trim()) return setFormError("Group name is required.");
    if (members.length < 2)
      return setFormError("Enter at least 2 members (comma-separated).");
    if (new Set(members).size !== members.length)
      return setFormError("Member names must be unique.");

    setCreating(true);
    try {
      await groupsApi.create({ name: name.trim(), members });
      setName("");
      setMemberInput("");
      setShowForm(false);
      reload();
    } catch {
      setFormError("Failed to create group.");
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-gray-900">Groups</h1>
          <p className="mt-0.5 text-sm text-gray-500">
            Split expenses with friends
          </p>
        </div>
        {!showForm && (
          <button
            onClick={() => setShowForm(true)}
            className="rounded-md bg-gray-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-gray-800"
          >
            New group
          </button>
        )}
      </div>

      {showForm && (
        <form
          onSubmit={handleCreate}
          className="mb-6 rounded-lg border border-gray-200 bg-white p-4"
        >
          {formError && (
            <div className="mb-3">
              <ErrorMessage message={formError} />
            </div>
          )}
          <div className="space-y-3">
            <div>
              <label className="mb-1 block text-xs font-medium uppercase tracking-wide text-gray-500">
                Group Name
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm text-gray-900 placeholder-gray-400 focus:border-gray-900 focus:ring-1 focus:ring-gray-900 focus:outline-none"
                placeholder="Weekend trip"
                autoFocus
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium uppercase tracking-wide text-gray-500">
                Members
              </label>
              <input
                type="text"
                value={memberInput}
                onChange={(e) => setMemberInput(e.target.value)}
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm text-gray-900 placeholder-gray-400 focus:border-gray-900 focus:ring-1 focus:ring-gray-900 focus:outline-none"
                placeholder="Alice, Bob, Charlie"
              />
              <p className="mt-1 text-xs text-gray-400">Separate names with commas</p>
            </div>
            <div className="flex gap-2 pt-1">
              <button
                type="submit"
                disabled={creating}
                className="rounded-md bg-gray-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-gray-800 disabled:opacity-50"
              >
                {creating ? "Creating..." : "Create"}
              </button>
              <button
                type="button"
                onClick={() => { setShowForm(false); setFormError(""); }}
                className="rounded-md px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900"
              >
                Cancel
              </button>
            </div>
          </div>
        </form>
      )}

      {status === "loading" && <LoadingSpinner />}
      {status === "error" && <ErrorMessage message={error || "Failed to load."} />}
      {status === "success" && groups && (
        <>
          {groups.length === 0 && !showForm ? (
            <div className="py-16 text-center">
              <p className="text-sm text-gray-500">No groups yet</p>
              <button
                onClick={() => setShowForm(true)}
                className="mt-3 text-sm font-medium text-gray-900 underline underline-offset-2 hover:no-underline"
              >
                Create your first group
              </button>
            </div>
          ) : (
            <div className="divide-y divide-gray-100 rounded-lg border border-gray-200 bg-white">
              {groups.map((group) => (
                <Link
                  key={group.id}
                  to={`/groups/${group.id}`}
                  className="flex items-center justify-between px-4 py-3 transition-colors hover:bg-gray-50"
                >
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {group.name}
                    </p>
                    <div className="mt-1.5 flex items-center gap-1">
                      {group.members.slice(0, 5).map((m) => {
                        const c = colorForName(m.name);
                        return (
                          <span
                            key={m.id}
                            title={m.name}
                            className={`inline-flex h-5 w-5 items-center justify-center rounded-full text-[10px] font-medium ${c.bg} ${c.text}`}
                          >
                            {initials(m.name)}
                          </span>
                        );
                      })}
                      {group.members.length > 5 && (
                        <span className="text-xs text-gray-400">
                          +{group.members.length - 5}
                        </span>
                      )}
                    </div>
                  </div>
                  <svg className="h-4 w-4 shrink-0 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                  </svg>
                </Link>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
