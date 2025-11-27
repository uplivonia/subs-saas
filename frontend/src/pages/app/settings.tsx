import AppLayout from "@/components/AppLayout";
import { useEffect, useState } from "react";

const API_BASE = "https://subs-saas.onrender.com/api/v1";

type StripeStatus = {
    connected: boolean;
    stripe_account_id: string | null;
    stripe_onboarded: boolean;
};

export default function SettingsPage() {
    const [loading, setLoading] = useState(true);
    const [stripeStatus, setStripeStatus] = useState<StripeStatus | null>(null);
    const [linkLoading, setLinkLoading] = useState(false);

    const loadStatus = async () => {
        if (typeof window === "undefined") return;

        const token = localStorage.getItem("token");
        if (!token) {
            setStripeStatus(null);
            setLoading(false);
            return;
        }

        try {
            const res = await fetch(`${API_BASE}/payments/connect/status`, {
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
            });

            if (!res.ok) {
                console.error("Failed to load Stripe status:", await res.text());
                setStripeStatus(null);
            } else {
                const data = await res.json();
                setStripeStatus(data);
            }
        } catch (e) {
            console.error("Network error while loading Stripe status:", e);
            setStripeStatus(null);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadStatus();
    }, []);

    const handleConnectStripe = async () => {
        if (typeof window === "undefined") return;

        const token = localStorage.getItem("token");
        if (!token) {
            alert("Please log in first.");
            return;
        }

        setLinkLoading(true);
        try {
            const res = await fetch(`${API_BASE}/payments/connect/link`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
            });

            if (!res.ok) {
                const text = await res.text();
                console.error("Failed to create Stripe connect link:", text);
                alert("Could not create Stripe onboarding link. Please try again.");
                return;
            }

            const data = await res.json();
            const url = data.url as string | undefined;

            if (!url) {
                alert("Stripe link is missing in response.");
                return;
            }

            window.open(url, "_blank", "noopener,noreferrer");
        } catch (e) {
            console.error("Network error while creating Stripe link:", e);
            alert("Network error. Please try again.");
        } finally {
            setLinkLoading(false);
        }
    };

    const handleRefresh = () => {
        setLoading(true);
        loadStatus();
    };

    const connected = stripeStatus?.connected;

    return (
        <AppLayout title="Settings">
            <div className="max-w-2xl mx-auto">
                <h1 className="text-2xl font-semibold text-slate-900 mb-4">
                    Settings
                </h1>

                <div className="bg-white shadow-sm rounded-2xl border border-slate-200 p-6 space-y-6">
                    <div>
                        <h2 className="text-sm font-semibold text-slate-800 mb-1">
                            Payouts via Stripe
                        </h2>
                        <p className="text-sm text-slate-600">
                            Connect your Stripe account to receive subscription payments
                            from your private channels. We never store card data, Stripe
                            handles all payments securely.
                        </p>
                    </div>

                    <div className="flex items-center justify-between">
                        <div>
                            {loading && (
                                <p className="text-xs text-slate-500">
                                    Checking Stripe connection...
                                </p>
                            )}

                            {!loading && (
                                <>
                                    <p className="text-xs text-slate-500">
                                        Status:{" "}
                                        <span
                                            className={
                                                connected
                                                    ? "text-emerald-600 font-semibold"
                                                    : "text-amber-600 font-semibold"
                                            }
                                        >
                                            {connected ? "Connected" : "Not connected"}
                                        </span>
                                    </p>
                                    {stripeStatus?.stripe_account_id && (
                                        <p className="text-[11px] text-slate-400 mt-1">
                                            Account ID: {stripeStatus.stripe_account_id}
                                        </p>
                                    )}
                                </>
                            )}
                        </div>

                        <div className="flex gap-2">
                            <button
                                type="button"
                                onClick={handleConnectStripe}
                                disabled={linkLoading}
                                className={`inline-flex items-center px-4 py-2 rounded-xl text-sm font-medium ${linkLoading
                                        ? "bg-slate-200 text-slate-500 cursor-wait"
                                        : "bg-indigo-600 text-white hover:bg-indigo-700"
                                    }`}
                            >
                                {connected
                                    ? "Reconnect Stripe"
                                    : "Connect Stripe Account"}
                            </button>

                            <button
                                type="button"
                                onClick={handleRefresh}
                                disabled={loading}
                                className="inline-flex items-center px-3 py-2 rounded-xl text-xs font-medium border border-slate-300 text-slate-600 hover:bg-slate-50"
                            >
                                Refresh
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </AppLayout>
    );
}
