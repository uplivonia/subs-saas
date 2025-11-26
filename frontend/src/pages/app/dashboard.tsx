import AppLayout from "@/components/AppLayout";

export default function Dashboard() {
    // пока всё статично, позже подтащим реальные данные с бэка
    const stats = [
        { label: "Monthly revenue", value: "$0.00" },
        { label: "Active subscribers", value: "0" },
        { label: "Connected channels", value: "0" },
    ];

    return (
        <AppLayout title="Dashboard">
            <div className="max-w-5xl mx-auto space-y-8">
                {/* Top stats */}
                <section>
                    <h1 className="text-2xl font-semibold mb-4">Overview</h1>
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
                </section>

                {/* Channels + payments preview */}
                <section className="grid gap-6 md:grid-cols-2">
                    <div className="bg-white border border-slate-200 rounded-xl p-4">
                        <div className="flex items-center justify-between mb-3">
                            <h2 className="text-sm font-medium text-slate-800">
                                Connected channels
                            </h2>
                            <span className="text-xs text-indigo-600 cursor-pointer">
                                View all
                            </span>
                        </div>
                        <p className="text-sm text-slate-500 mb-4">
                            You don&apos;t have any channels yet.
                        </p>
                        <button className="px-4 py-2 rounded-lg bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-700">
                            + Add channel
                        </button>
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
