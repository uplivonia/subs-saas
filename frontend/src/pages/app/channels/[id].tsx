import AppLayout from "@/components/AppLayout";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";

const API_BASE = "https://subs-saas.onrender.com/api/v1";
const TELEGRAM_BOT_USERNAME = "oneclicksub_bot"; // если переименуешь бота – поменяй здесь

type Project = {
    id: number;
    user_id: number;
    title: string | null;
    username: string | null;
    telegram_channel_id: number | null;
    active: boolean;
    settings?: {
        status?: string;
        [key: string]: any;
    } | null;
};

type Plan = {
    id: number;
    project_id: number;
    name: string;
    price: number;
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

    // поля формы создания плана
    const [planName, setPlanName] = useState("");
    const [planPrice, setPlanPrice] = useState("");
    const [planDuration, setPlanDuration] = useState("30");
    const [planCurrency, setPlanCurrency] = useState("EUR");

    const numericId =
        typeof id === "string" ? parseInt(id, 10) : Array.isArray(id) ? parseInt(id[0], 10) : NaN;

    const token =
        typeof window !== "undefined" ? localStorage.getItem("token") : null;

    useEffect(() => {
        if (!numericId || Number.isNaN(numericId)) return;

        const fetchData = async () => {
            try {
                if (!token) {
                    setLoading(false);
                    return;
                }

                // 1) грузим проект
                const projRes = await fetch(`${API_BASE}/projects/${numericId}`, {
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${token}`,
                    },
                });

                if (!projRes.ok) {
                    console.error("Failed to load project:", await projRes.text());
                    setLoading(false);
                    return;
                }

                const projData: Project = await projRes.json();
                setProject(projData);

                // 2) грузим планы
                const plansRes = await fetch(
                    `${API_BASE}/plans/project/${numericId}`,
                    {
                        headers: {
                            "Content-Type": "application/json",
                            Authorization: `Bearer ${token}`,
                        },
                    }
                );

                if (!plansRes.ok) {
                    console.error("Failed to load plans:", await plansRes.text());
                    setPlans([]);
                    setLoading(false);
                    return;
                }

                const plansData: Plan[] = await plansRes.json();
                setPlans(plansData);
            } catch (e) {
                console.error("Error while loading channel data:", e);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [numericId, token]);

    const handleCreatePlan = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!project || !token) return;

        const priceNum = parseFloat(planPrice.replace(",", "."));
        const durationNum = parseInt(planDuration, 10);

        if (!planName || Number.isNaN(priceNum) || Number.isNaN(durationNum)) {
            alert("Please fill in name, price and duration correctly.");
            return;
        }

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
                    price: priceNum,
                    currency: planCurrency,
                    duration_days: durationNum,
                    active: true,
                }),
            });

            if (!res.ok) {
                const text = await res.text();
                console.error("Failed to create plan:", text);
                alert("Failed to create plan. Please try again.");
                return;
            }

            const newPlan: Plan = await res.json();
            setPlans((prev) => [...prev, newPlan]);

            // очистить форму
            setPlanName("");
            setPlanPrice("");
            setPlanDuration("30");
            setPlanCurrency("EUR");
        } catch (e) {
            console.error("Network error while creating plan:", e);
            alert("Network error while creating plan.");
        } finally {
            setCreating(false);
        }
    };

    const handleCopyLink = async () => {
        if (!project) return;
        const url = `https://t.me/${TELEGRAM_BOT_USERNAME}?start=project_${project.id}`;

        try {
            await navigator.clipboard.writeText(url);
            alert("Subscription link copied to clipboard!");
        } catch {
            alert(`Subscription link: ${url}`);
        }
    };

    const status =
        project?.telegram_channel_id
            ? "connected"
            : project?.settings?.status ?? "pending";

    const subscriberLink =
        project &&
        `https://t.me/${TELEGRAM_BOT_USERNAME}?start=project_${project.id}`;

    return (
        <AppLayout title="Channel settings">
            <div className="max-w-4xl mx-auto space-y-8">
                <button
                    type="button"
                    onClick={() => router.push("/app/channels")}
                    className="text-xs text-slate-500 hover:text-slate-700 mb-2"
                >
                    ← Back to channels
                </button>

                {loading && <p className="text-slate-500 text-sm">Loading…</p>}

                {!loading && !project && (
                    <p className="text-slate-500 text-sm">
                        Channel not found or you don&apos;t have access to it.
                    </p>
                )}

                {!loading && project && (
                    <>
                        {/* Channel info */}
                        <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
                            <h1 className="text-xl font-semibold text-slate-900 mb-1">
                                {project.title || "Unnamed channel"}
                            </h1>
                            <p className="text-xs text-slate-500">
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

                        {/* Subscriber link */}
                        {subscriberLink && (
                            <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm space-y-2">
                                <h2 className="text-sm font-semibold text-slate-900">
                                    Subscription link
                                </h2>
                                <p className="text-xs text-slate-500">
                                    Share this link with your audience. They will open the bot
                                    and see your subscription plans for this channel.
                                </p>
                                <div className="flex flex-col sm:flex-row sm:items-center gap-2 mt-2">
                                    <div className="flex-1">
                                        <code className="block w-full text-xs bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 overflow-x-auto">
                                            {subscriberLink}
                                        </code>
                                    </div>
                                    <button
                                        type="button"
                                        onClick={handleCopyLink}
                                        className="px-3 py-2 rounded-lg bg-indigo-600 text-white text-xs font-medium hover:bg-indigo-700 transition-colors"
                                    >
                                        Copy link
                                    </button>
                                </div>
                            </div>
                        )}

                        {/* Plans */}
                        <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm space-y-4">
                            <div className="flex items-center justify-between">
                                <h2 className="text-sm font-semibold text-slate-900">
                                    Subscription plans
                                </h2>
                            </div>

                            {plans.length === 0 && (
                                <p className="text-xs text-slate-500">
                                    You don&apos;t have any plans yet. Create your first paid
                                    subscription below.
                                </p>
                            )}

                            {plans.length > 0 && (
                                <div className="space-y-3">
                                    {plans.map((plan) => (
                                        <div
                                            key={plan.id}
                                            className="border border-slate-200 rounded-xl px-3 py-3 flex items-center justify-between"
                                        >
                                            <div>
                                                <p className="text-sm font-medium text-slate-900">
                                                    {plan.name}
                                                </p>
                                                <p className="text-xs text-slate-500 mt-0.5">
                                                    {plan.price} {plan.currency} / {plan.duration_days} days
                                                </p>
                                            </div>
                                            <span className="text-xs text-emerald-600 font-medium">
                                                Active
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            )}

                            {/* Create plan form */}
                            <form
                                onSubmit={handleCreatePlan}
                                className="mt-4 border-t border-slate-100 pt-4 space-y-3"
                            >
                                <h3 className="text-xs font-semibold text-slate-800 uppercase tracking-wide">
                                    Create new plan
                                </h3>

                                <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
                                    <div className="sm:col-span-2">
                                        <label className="block text-xs text-slate-600 mb-1">
                                            Name
                                        </label>
                                        <input
                                            type="text"
                                            value={planName}
                                            onChange={(e) => setPlanName(e.target.value)}
                                            className="w-full border border-slate-300 rounded-lg px-2 py-1.5 text-sm"
                                            placeholder="Monthly access"
                                            required
                                        />
                                    </div>

                                    <div>
                                        <label className="block text-xs text-slate-600 mb-1">
                                            Price
                                        </label>
                                        <input
                                            type="text"
                                            value={planPrice}
                                            onChange={(e) => setPlanPrice(e.target.value)}
                                            className="w-full border border-slate-300 rounded-lg px-2 py-1.5 text-sm"
                                            placeholder="9.99"
                                            required
                                        />
                                    </div>

                                    <div>
                                        <label className="block text-xs text-slate-600 mb-1">
                                            Currency
                                        </label>
                                        <select
                                            value={planCurrency}
                                            onChange={(e) => setPlanCurrency(e.target.value)}
                                            className="w-full border border-slate-300 rounded-lg px-2 py-1.5 text-sm bg-white"
                                        >
                                            <option value="EUR">EUR</option>
                                            <option value="USD">USD</option>
                                        </select>
                                    </div>
                                </div>

                                <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
                                    <div>
                                        <label className="block text-xs text-slate-600 mb-1">
                                            Duration (days)
                                        </label>
                                        <input
                                            type="number"
                                            min={1}
                                            value={planDuration}
                                            onChange={(e) => setPlanDuration(e.target.value)}
                                            className="w-full border border-slate-300 rounded-lg px-2 py-1.5 text-sm"
                                            required
                                        />
                                    </div>
                                </div>

                                <button
                                    type="submit"
                                    disabled={creating}
                                    className={`mt-2 inline-flex items-center px-4 py-2 rounded-xl text-sm font-medium ${creating
                                            ? "bg-slate-200 text-slate-500 cursor-wait"
                                            : "bg-indigo-600 text-white hover:bg-indigo-700"
                                        }`}
                                >
                                    {creating ? "Creating…" : "Create plan"}
                                </button>
                            </form>
                        </div>
                    </>
                )}
            </div>
        </AppLayout>
    );
}
