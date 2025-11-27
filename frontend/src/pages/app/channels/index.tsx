import AppLayout from "@/components/AppLayout";
import Link from "next/link";
import { useEffect, useState } from "react";

const API_BASE = "https://subs-saas.onrender.com/api/v1";

type Project = {
    id: number;
    title: string | null;
    username: string | null;
    telegram_channel_id: number | null;
    active: boolean;
    settings?: {
        status?: string;
        [key: string]: any;
    } | null;
};

export default function ChannelsPage() {
    const [projects, setProjects] = useState<Project[] | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchProjects = async () => {
            try {
                if (typeof window === "undefined") return;

                const token = localStorage.getItem("token");
                if (!token) {
                    setProjects([]);
                    setLoading(false);
                    return;
                }

                const res = await fetch(`${API_BASE}/projects/`, {
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${token}`,
                    },
                });

                if (!res.ok) {
                    console.error("Failed to load projects:", await res.text());
                    setProjects([]);
                    setLoading(false);
                    return;
                }

                const data = await res.json();
                setProjects(data);
            } catch (e) {
                console.error("Network error while loading projects:", e);
                setProjects([]);
            } finally {
                setLoading(false);
            }
        };

        fetchProjects();
    }, []);

    return (
        <AppLayout title="Your channels">
            <div className="max-w-3xl mx-auto">
                <div className="flex items-center justify-between mb-6">
                    <h1 className="text-2xl font-semibold text-slate-900">
                        Your channels
                    </h1>
                    <Link
                        href="/app/channels/new"
                        className="inline-flex items-center px-4 py-2 rounded-xl bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-700 transition-colors"
                    >
                        + Add channel
                    </Link>
                </div>

                {loading && (
                    <p className="text-slate-500 text-sm">Loading your channels…</p>
                )}

                {!loading && projects && projects.length === 0 && (
                    <p className="text-slate-500 text-sm">
                        You don&apos;t have any connected channels yet.
                    </p>
                )}

                {!loading && projects && projects.length > 0 && (
                    <div className="space-y-4">
                        {projects.map((project) => {
                            const status =
                                project.settings?.status ??
                                (project.telegram_channel_id ? "connected" : "pending");

                            return (
                                <div
                                    key={project.id}
                                    className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm flex items-center justify-between"
                                >
                                    <div>
                                        <h2 className="text-sm font-semibold text-slate-900">
                                            {project.title || "Unnamed channel"}
                                        </h2>
                                        <p className="text-xs text-slate-500 mt-1">
                                            Channel ID:{" "}
                                            {project.telegram_channel_id
                                                ? project.telegram_channel_id
                                                : "not linked yet"}
                                        </p>
                                        <p className="text-xs text-slate-500 mt-1">
                                            Status:{" "}
                                            <span
                                                className={
                                                    status === "connected"
                                                        ? "text-emerald-600 font-medium"
                                                        : "text-amber-600 font-medium"
                                                }
                                            >
                                                {status}
                                            </span>
                                        </p>
                                    </div>

                                    {/* Пока просто заглушка на будущее: страница настроек конкретного канала */}
                                    <Link
                                        href={`/app/channels/${project.id}`}
                                        className="text-xs font-medium text-indigo-600 hover:text-indigo-700"
                                    >
                                        Configure →
                                    </Link>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>
        </AppLayout>
    );
}
