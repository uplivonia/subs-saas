import AppLayout from "@/components/AppLayout";
import Link from "next/link";
import { useEffect, useState } from "react";

const API_BASE = "https://subs-saas.onrender.com/api/v1";

type OverviewResponse = {
    balance: number;
    connected_channels: number;
    active_subscribers: number;
    total_revenue: number;
};

type Project = {
    id: number;
    title?: string | null;
    telegram_username?: string | null;
};

export default function Dashboard() {
    const [loading, setLoading] = useState(true);
    const [projects, setProjects] = useState<Project[]>([]);
    const [overview, setOverview] = useState<OverviewResponse | null>(null);
    const [error, setError] = useState<string | null>(null);

    const loadData = async () => {
        if (typeof window === "undefined") return;

        const token = localStorage.getItem("token");
        if (!token) {
            setError("You are not logged in.");
            setLoading(false);
            return;
        }

        try {
            const [projectsRes, overviewRes] = await Promise.all([
                fetch(`${API_BASE}/projects/`, {
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${token}`,
                    },
                }),
                fetch(`${API_BASE}/payments/creator/overview`, {
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${token}`,
                    },
                }),
            ]);

            if (!projectsRes.ok) {
                console.error("Failed to load projects:", await projectsRes.text());
            } else {
                const projectsData = await projectsRes.json();
                if (Array.isArray(projectsData)) {
                    setProjects(projectsData as Project[]);
                }
            }

            if (!overviewRes.ok) {
                console.error("Failed to load overview:", await overviewRes.text());
            } else {
                const ov = (await overviewRes.json()) as OverviewResponse;
                setOverview(ov);
            }
        } catch (e) {
            console.error("Error while loading dashboard data:", e);
            setError("Failed to load dashboard data.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadData();
    }, []);

    const balance = overview?.balance ?? 0;
    const activeSubscribers = overview?.active_subscribers ?? 0;
    const connectedChannels =
        overview?.connected_channels ?? projects.length ?? 0;
    const totalRevenue = overview?.total_revenue ?? 0;

    const stats = [
        { label: "Available balance", value: `EUR ${balance.toFixed(2)}` },
        { label: "Active subscribers", value: String(activeSubscribers) },
        { label: "Connected channels", value: String(connectedChannels) },
    ];

    return (
        <AppLayout title="Dashboard">
            <div className="max-w-5xl mx-auto space-y-8">
                {/* Top stats */}
                <section>
                    <h1 className="text-2xl font-semibold mb-4">Overview</h1>

                    {error && (
                        <p className="mb-3 text-sm text-red-500">
                            {error}
                        </p>
                    )}

                    <div className="grid gap-4 md:grid-cols-3">
                        {stats.map((stat) => (
                            <div
                                key={stat.label}
                                className="bg-white border border-slate-200 rounded-xl p-4"
                            >
                                <p className="text-xs text-slate-500">{stat.label}</p>
                                <p className="mt-2 text-xl font-semibold">{stat.value}</p>
                            </div>
                        ))}
                    </div>

                    <p className="mt-3 text-xs text-slate-500">
                        Total revenue from all paid subscriptions:{" "}
                        <span className="font-semibold">
                            EUR {totalRevenue.toFixed(2)}
                        </span>
                    </p>
                </section>

                {/* Channels + payments preview */}
                <section className="grid gap-6 md:grid-cols-2">
                    <div className="bg-white border border-slate-200 rounded-xl p-4">
                        <div className="flex items-center justify-between mb-3">
                            <h2 className="text-sm font-medium text-slate-800">
                                Connected channels
                            </h2>
                            <Link
                                href="/app/channels"
                                className="text-xs text-indigo-600 cursor-pointer"
                            >
                                View all
                            </Link>
                        </div>

                        {loading ? (
                            <p className="text-sm text-slate-500">Loading channels...</p>
                        ) : connectedChannels === 0 ? (
                            <>
                                <p className="text-sm text-slate-500 mb-4">
                                    You don&apos;t have any channels yet.
                                </p>
                                <Link
                                    href="/app/channels/new"
                                    className="inline-flex px-4 py-2 rounded-lg bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-700"
                                >
                                    + Add channel
                                </Link>
                            </>
                        ) : (
                            <>
                                <p className="text-sm text-slate-500 mb-3">
                                    You have {connectedChannels}{" "}
                                    {connectedChannels === 1 ? "channel" : "channels"} connected.
                                </p>
                                <ul className="space-y-1 mb-3">
                                    {projects.slice(0, 3).map((p) => (
                                        <li
                                            key={p.id}
                                            className="text-sm text-slate-700 flex items-center justify-between"
                                        >
                                            <span>{p.title || `Channel #${p.id}`}</span>
                                            {p.telegram_username && (
                                                <span className="text-xs text-slate-400">
                                                    {p.telegram_username}
                                                </span>
                                            )}
                                        </li>
                                    ))}
                                </ul>
                                <Link
                                    href="/app/channels"
                                    className="inline-flex px-3 py-1.5 rounded-lg border border-slate-200 text-xs text-slate-700 hover:bg-slate-50"
                                >
                                    Manage channels
                                </Link>
                            </>
                        )}
                    </div>

                    <div className="bg-white border border-slate-200 rounded-xl p-4">
                        <div className="flex items-center justify-between mb-3">
                            <h2 className="text-sm font-medium text-slate-800">
                                Recent payments
                            </h2>
                            <span className="text-xs text-slate-400">Coming soon</span>
                        </div>
                        <p className="text-sm text-slate-500">
                            Once you connect a channel and start selling subscriptions, your
                            latest payments will appear here.
                        </p>
                    </div>
                </section>
            </div>
        </AppLayout>
    );
}
