import AppLayout from "@/components/AppLayout";
import Link from "next/link";
import { useEffect, useState } from "react";

const API_BASE = "https://subs-saas.onrender.com/api/v1";

type Project = {
    id: number;
    telegram_channel_id: number;
    title?: string | null;
    username?: string | null;
    active: boolean;
    user_id: number;
};

export default function ChannelsPage() {
    const [projects, setProjects] = useState<Project[]>([]);
    const [loading, setLoading] = useState(true);

    const token =
        typeof window !== "undefined" ? localStorage.getItem("token") : null;

    useEffect(() => {
        const load = async () => {
            try {
                const res = await fetch(`${API_BASE}/projects/`, {
                    headers: {
                        "Content-Type": "application/json",
                        ...(token ? { Authorization: `Bearer ${token}` } : {}),
                    },
                });
                const data = await res.json();
                setProjects(data);
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        };
        load();
    }, [token]);

    return (
        <AppLayout title="Channels">
            <div className="max-w-4xl mx-auto">
                <div className="flex items-center justify-between mb-4">
                    <h1 className="text-2xl font-semibold">Channels</h1>
                    <Link
                        href="/app/channels/new"
                        className="inline-flex px-4 py-2 rounded-lg bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-700"
                    >
                        + Add channel
                    </Link>
                </div>

                {loading ? (
                    <p className="text-sm text-slate-600">Loading...</p>
                ) : projects.length === 0 ? (
                    <p className="text-sm text-slate-600">
                        You don&apos;t have any channels yet. Click &quot;Add channel&quot;
                        to connect your first private channel.
                    </p>
                ) : (
                    <div className="bg-white border border-slate-200 rounded-xl divide-y divide-slate-100">
                        {projects.map((p) => (
                            <div key={p.id} className="px-4 py-3 flex items-center justify-between">
                                <div>
                                    <div className="text-sm font-medium">
                                        {p.title || "(no title)"}
                                    </div>
                                    <div className="text-xs text-slate-500">
                                        ID: {p.telegram_channel_id}
                                        {p.username && ` • @${p.username}`}
                                    </div>
                                </div>
                                <div className="text-xs text-slate-500">
                                    {p.active ? "Active" : "Inactive"}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </AppLayout>
    );
}
