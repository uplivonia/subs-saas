import AppLayout from "@/components/AppLayout";
import { useRouter } from "next/router";
import Link from "next/link";
import { useEffect, useState, useMemo } from "react";

const API_BASE = "https://subs-saas.onrender.com/api/v1";
// если переименуешь бота – поменяй здесь:
const TELEGRAM_BOT_USERNAME = "oneclicksub_bot";

type Project = {
    id: number;
    user_id: number;
    title: string | null;
    username: string | null;
    telegram_channel_id: number | null;
    active: boolean;
    settings?: {
        status?: string;
        connection_code?: string;
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
    const [error, setError] = useState<string | null>(null);

    // поля для нового плана
    const [planName, setPlanName] = useState("Monthly access");
    const [planPrice, setPlanPrice] = useState("9.99");
    const [planDuration, setPlanDuration] = useState("30");
    const [planCurrency, setPlanCurrency] = useState("EUR");

    // готовая подписочная ссылка
    const subscriptionLink = useMemo(() => {
        if (!project) return "";
        return `https://t.me/${TELEGRAM_BOT_USERNAME}?start=project_${project.id}`;
    }, [project]);

    const loadData = async (projectId: number) => {
        if (typeof window === "undefined") return;

        const token = localStorage.getItem("token");
        if (!token) {
            setError("You are not logged in.");
            setLoading(false);
            return;
        }

        try {
            const [projRes, plansRes] = await Promise.all([
                fetch(`${API_BASE}/projects/${projectId}`, {
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${token}`,
                    },
                }),
                fetch(`${API_BASE}/plans/project/${projectId}`, {
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${token}`,
                    },
                }),
            ]);

            if (!projRes.ok) {
                const text = await projRes.text();
                console.error("Failed to load project:", text);
                setError("Failed to load channel data.");
            } else {
                const projData: Project = await projRes.json();
                setProject(projData);
            }

            if (!plansRes.ok) {
                const text = await plansRes.text();
                console.error("Failed to load plans:", text);
            } else {
                const plansData: Plan[] = await plansRes.json();
                setPlans(plansData);
            }
        } catch (e) {
            console.error("Error loading channel data:", e);
            setError("Failed to load channel data.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (!id) return;
        const numericId = parseInt(id as string, 10);
        if (Number.isNaN(numericId)) {
            setError("Invalid channel id.");
            setLoading(false);
            return;
        }
        loadData(numericId);
    }, [id]);

    const handleCopyLink = async () => {
        if (!subscriptionLink) return;
        try {
            await navigator.clipboard.writeText(subscriptionLink);
            alert("Subscription link copied to clipboard.");
        } catch (e) {
            console.error("Failed to copy link:", e);
            alert("Could not copy link. Please copy it manually.");
        }
    };

    const handleCreatePlan = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!project) return;

        if (!planName.trim()) {
            alert("Please enter plan name.");
            return;
        }

        const priceNum = Number(planPrice.replace(",", "."));
        const durationNum = parseInt(planDuration, 10);

        if (Number.isNaN(priceNum) || priceNum <= 0) {
            alert("Please enter valid price.");
            return;
        }
        if (Number.isNaN(durationNum) || durationNum <= 0) {
            alert("Please enter valid duration (days).");
            return;
        }

        if (typeof window === "undefined") return;
        const token = localStorage.getItem("token");
        if (!token) {
            alert("Please log in.");
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
                    name: planName.trim(),
                    price: priceNum,
                    currency: planCurrency,
                    duration_days: durationNum,
                    active: true,
                }),
            });

            const text = await res.text();

            if (!res.ok) {
                console.error("Failed to create plan:", text);
                try {
                    const err = JSON.parse(text);
                    alert(err.detail || "Could not create plan.");
                } catch {
                    alert("Could not create plan.");
                }
                return;
            }

            // успешно создали – обновляем список тарифов
            await loadData(project.id);
            setPlanName("Monthly access");
            setPlanPrice("9.99");
            setPlanDuration("30");
        } catch (e) {
            console.error("Network error while creating plan:", e);
            alert("Network error. Try again.");
        } finally {
            setCreating(false);
        }
    };

    const title =
        project?.title ||
        (project?.username ? `@${project.username}` : project ? `Channel #${project.id}` : "Channel");

    return (
        <AppLayout title="Channel details">
            <div className="max-w-4xl mx-auto space-y-6">
                <div className="flex items-center justify-between">
                    <div>
                        <p className="text-xs text-slate-500 mb-1">
                            <Link href="/app/channels" className="text-indigo-600">
                                ← Back to channels
                            </Link>
                        </p>
                        <h1 className="text-2xl font-semibold text-slate-900">{title}</h1>
                        {project?.username && (
                            <p className="text-xs text-slate-500 mt-1">
                                Telegram: @{project.username}
                            </p>
                        )}
                    </div>
                </div>

                {error && (
                    <p className="text-sm text-red-500 bg-red-50 border border-red-100 rounded-xl px-3 py-2">
                        {error}
                    </p>
                )}

                {loading ? (
                    <p className="text-sm text-slate-500">Loading channel data…</p>
                ) : !project ? (
                    <p className="text-sm text-slate-500">Channel not found.</p>
                ) : (
                    <>
                        {/* Subscription link */}
                        <section className="bg-white border border-slate-200 rounded-2xl p-4 space-y-2">
                            <h2 className="text-sm font-semibold text-slate-800 mb-1">
                                Subscription link
                            </h2>
                            <p className="text-xs text-slate-500 mb-2">
                                Share this link with your audience. They will open the bot and
                                see your subscription plans for this channel.
                            </p>
                            <div className="flex flex-col sm:flex-row gap-3">
                                <input
                                    type="text"
                                    readOnly
                                    value={subscriptionLink}
                                    className="flex-1 rounded-xl border border-slate-300 px-3 py-2 text-xs text-slate-700 bg-slate-50"
                                />
                                <button
                                    type="button"
                                    onClick={handleCopyLink}
                                    className="inline-flex items-center justify-center px-4 py-2 rounded-xl bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-700"
                                >
                                    Copy link
                                </button>
                            </div>
                        </section>

                        {/* Plans list + create form */}
                        <section className="bg-white border border-slate-200 rounded-2xl p-4">
                            <h2 className="text-sm font-semibold text-slate-800 mb-3">
                                Subscription plans
                            </h2>

                            {plans.length === 0 ? (
                                <p className="text-sm text-slate-500 mb-4">
                                    You don&apos;t have any plans yet. Create your first plan
                                    below.
                                </p>
                            ) : (
                                <div className="space-y-2 mb-5">
                                    {plans.map((plan) => (
                                        <div
                                            key={plan.id}
                                            className="flex items-center justify-between rounded-xl border border-slate-200 px-3 py-2 text-sm"
                                        >
                                            <div>
                                                <p className="font-medium text-slate-800">
                                                    {plan.name}
                                                </p>
                                                <p className="text-xs text-slate-500">
                                                    {plan.price.toFixed(2)} {plan.currency} /{" "}
                                                    {plan.duration_days} days
                                                </p>
                                            </div>
                                            <span
                                                className={`text-xs font-medium ${plan.active
                                                        ? "text-emerald-600"
                                                        : "text-slate-400"
                                                    }`}
                                            >
                                                {plan.active ? "Active" : "Inactive"}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            )}

                            <div className="border-t border-slate-200 pt-4 mt-2">
                                <h3 className="text-xs font-semibold text-slate-700 mb-2">
                                    Create new plan
                                </h3>
                                <form
                                    onSubmit={handleCreatePlan}
                                    className="grid gap-3 md:grid-cols-4"
                                >
                                    <div className="md:col-span-2">
                                        <label className="block text-xs font-medium text-slate-700 mb-1">
                                            Name
                                        </label>
                                        <input
                                            type="text"
                                            value={planName}
                                            onChange={(e) => setPlanName(e.target.value)}
                                            className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                                            placeholder="Monthly access"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-xs font-medium text-slate-700 mb-1">
                                            Price
                                        </label>
                                        <input
                                            type="text"
                                            value={planPrice}
                                            onChange={(e) => setPlanPrice(e.target.value)}
                                            className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                                            placeholder="9.99"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-xs font-medium text-slate-700 mb-1">
                                            Duration (days)
                                        </label>
                                        <input
                                            type="number"
                                            min={1}
                                            value={planDuration}
                                            onChange={(e) => setPlanDuration(e.target.value)}
                                            className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                                            placeholder="30"
                                        />
                                    </div>

                                    <div className="md:col-span-1">
                                        <label className="block text-xs font-medium text-slate-700 mb-1">
                                            Currency
                                        </label>
                                        <select
                                            value={planCurrency}
                                            onChange={(e) => setPlanCurrency(e.target.value)}
                                            className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                                        >
                                            <option value="EUR">EUR</option>
                                            <option value="USD">USD</option>
                                        </select>
                                    </div>

                                    <div className="md:col-span-3 flex items-end">
                                        <button
                                            type="submit"
                                            disabled={creating}
                                            className={`inline-flex items-center px-4 py-2 rounded-xl text-sm font-medium ${creating
                                                    ? "bg-slate-200 text-slate-500 cursor-wait"
                                                    : "bg-indigo-600 text-white hover:bg-indigo-700"
                                                }`}
                                        >
                                            {creating ? "Creating…" : "Create plan"}
                                        </button>
                                    </div>
                                </form>
                            </div>
                        </section>
                    </>
                )}
            </div>
        </AppLayout>
    );
}
