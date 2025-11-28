import AppLayout from "@/components/AppLayout";
import { useRouter } from "next/router";
import Link from "next/link";
import { useEffect, useState, useMemo } from "react";

const API_BASE = "https://subs-saas.onrender.com/api/v1";
const TELEGRAM_BOT_USERNAME = "oneclicksub_bot";

type Project = {
    id: number;
    title?: string | null;
    username?: string | null;
};

type Plan = {
    id: number;
    project_id: number;
    name: string;
    price: number | string;
    currency: string;
    duration_days: number;
    active: boolean;
};

export default function ChannelDetailsPage() {
    const router = useRouter();
    const { id } = router.query;

    const [project, setProject] = useState<Project | null>(null);
    const [plans, setPlans] = useState<Plan[]>([]);
    const [loading, setLoading] = useState(true);
    const [creating, setCreating] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const [planName, setPlanName] = useState("Monthly access");
    const [planPrice, setPlanPrice] = useState("9.99");
    const [planDuration, setPlanDuration] = useState("30");
    const [planCurrency, setPlanCurrency] = useState("EUR");

    const subscriptionLink = useMemo(() => {
        if (!project) return "";
        return `https://t.me/${TELEGRAM_BOT_USERNAME}?start=project_${project.id}`;
    }, [project]);

    const loadData = async (projectId: number) => {
        const token = localStorage.getItem("token");
        if (!token) return;

        try {
            const [p1, p2] = await Promise.all([
                fetch(`${API_BASE}/projects/${projectId}`, {
                    headers: { Authorization: `Bearer ${token}` },
                }),
                fetch(`${API_BASE}/plans/project/${projectId}`, {
                    headers: { Authorization: `Bearer ${token}` },
                }),
            ]);

            if (p1.ok) setProject(await p1.json());
            if (p2.ok) setPlans(await p2.json());
        } catch (err) {
            console.error("Load error:", err);
            setError("Failed to load channel data");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (!id) return;
        const n = parseInt(id as string, 10);
        if (!isNaN(n)) loadData(n);
    }, [id]);

    const safePrice = (price: number | string) => {
        const num = typeof price === "number" ? price : Number(price);
        return isNaN(num) ? "0.00" : num.toFixed(2);
    };

    const handleCopyLink = async () => {
        try {
            await navigator.clipboard.writeText(subscriptionLink);
            alert("Link copied!");
        } catch {
            alert("Failed to copy");
        }
    };

    const handleCreatePlan = async (e: any) => {
        e.preventDefault();
        if (!project) return;

        const token = localStorage.getItem("token");
        if (!token) return;

        setCreating(true);

        try {
            const res = await fetch(`${API_BASE}/plans/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({
                    project_id: project.id,
                    name: planName,
                    price: Number(planPrice),
                    duration_days: Number(planDuration),
                    currency: planCurrency,
                    active: true,
                }),
            });

            if (!res.ok) {
                const msg = await res.text();
                console.error(msg);
                alert("Failed to create plan");
            } else {
                await loadData(project.id);
                setPlanName("Monthly access");
                setPlanPrice("9.99");
                setPlanDuration("30");
            }
        } finally {
            setCreating(false);
        }
    };

    if (loading)
        return (
            <AppLayout title="Channel">
                <p className="text-sm text-slate-500">Loading...</p>
            </AppLayout>
        );

    if (!project)
        return (
            <AppLayout title="Channel">
                <p className="text-sm text-slate-500">Channel not found.</p>
            </AppLayout>
        );

    return (
        <AppLayout title="Channel details">
            <div className="max-w-3xl mx-auto space-y-8">
                <div>
                    <p className="text-xs mb-1">
                        <Link href="/app/channels" className="text-indigo-600">
                            ← Back
                        </Link>
                    </p>
                    <h1 className="text-2xl font-semibold text-slate-900">
                        {project.title || `Channel #${project.id}`}
                    </h1>
                    {project.username && (
                        <p className="text-xs text-slate-500">@{project.username}</p>
                    )}
                </div>

                {/* Subscription Link */}
                <section className="bg-white border rounded-xl p-4">
                    <h2 className="text-sm font-semibold mb-1">Subscription link</h2>
                    <p className="text-xs text-slate-500 mb-3">
                        Share this link with your audience.
                    </p>

                    <div className="flex gap-2 flex-col sm:flex-row">
                        <input
                            readOnly
                            value={subscriptionLink}
                            className="flex-1 border rounded-xl px-3 py-2 bg-slate-50 text-xs"
                        />
                        <button
                            onClick={handleCopyLink}
                            className="px-4 py-2 bg-indigo-600 text-white rounded-xl text-sm"
                        >
                            Copy
                        </button>
                    </div>
                </section>

                {/* Plans */}
                <section className="bg-white border rounded-xl p-4">
                    <h2 className="text-sm font-semibold mb-3">Subscription plans</h2>

                    {plans.length === 0 ? (
                        <p className="text-sm text-slate-500 mb-3">
                            No plans yet — create one below.
                        </p>
                    ) : (
                        <div className="space-y-2 mb-4">
                            {plans.map((plan) => (
                                <div
                                    key={plan.id}
                                    className="border rounded-lg p-3 flex justify-between"
                                >
                                    <div>
                                        <p className="font-medium">{plan.name}</p>
                                        <p className="text-xs text-slate-500">
                                            {safePrice(plan.price)} {plan.currency} /{" "}
                                            {plan.duration_days} days
                                        </p>
                                    </div>

                                    <span
                                        className={`text-xs font-semibold ${plan.active ? "text-green-600" : "text-slate-400"
                                            }`}
                                    >
                                        {plan.active ? "Active" : "Inactive"}
                                    </span>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Create plan */}
                    <form onSubmit={handleCreatePlan} className="grid gap-3">
                        <div>
                            <label className="text-xs">Name</label>
                            <input
                                className="border rounded-xl px-3 py-2 w-full text-sm"
                                value={planName}
                                onChange={(e) => setPlanName(e.target.value)}
                            />
                        </div>

                        <div className="grid grid-cols-3 gap-3">
                            <div>
                                <label className="text-xs">Price</label>
                                <input
                                    className="border rounded-xl px-3 py-2 text-sm w-full"
                                    value={planPrice}
                                    onChange={(e) => setPlanPrice(e.target.value)}
                                />
                            </div>

                            <div>
                                <label className="text-xs">Duration</label>
                                <input
                                    type="number"
                                    className="border rounded-xl px-3 py-2 text-sm w-full"
                                    value={planDuration}
                                    onChange={(e) => setPlanDuration(e.target.value)}
                                />
                            </div>

                            <div>
                                <label className="text-xs">Currency</label>
                                <select
                                    className="border rounded-xl px-3 py-2 text-sm w-full"
                                    value={planCurrency}
                                    onChange={(e) => setPlanCurrency(e.target.value)}
                                >
                                    <option value="EUR">EUR</option>
                                    <option value="USD">USD</option>
                                </select>
                            </div>
                        </div>

                        <button
                            type="submit"
                            className={`px-4 py-2 rounded-xl text-white ${creating ? "bg-slate-400" : "bg-indigo-600 hover:bg-indigo-700"
                                }`}
                        >
                            {creating ? "Creating..." : "Create plan"}
                        </button>
                    </form>
                </section>
            </div>
        </AppLayout>
    );
}
