import AppLayout from "@/components/AppLayout";
import { useEffect, useState } from "react";

const API_BASE = "https://subs-saas.onrender.com/api/v1";

type Summary = {
    balance: number;
    payout_method: string | null;
    payout_details: string | null;
};

export default function SettingsPage() {
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [requesting, setRequesting] = useState(false);

    const [summary, setSummary] = useState<Summary | null>(null);
    const [payoutMethod, setPayoutMethod] = useState("");
    const [payoutDetails, setPayoutDetails] = useState("");

    const loadSummary = async () => {
        if (typeof window === "undefined") return;

        const token = localStorage.getItem("token");
        if (!token) {
            setSummary(null);
            setLoading(false);
            return;
        }

        try {
            const res = await fetch(`${API_BASE}/payments/me/summary`, {
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
            });

            if (!res.ok) {
                console.error("Failed to load summary:", await res.text());
                setSummary(null);
                setLoading(false);
                return;
            }

            const data = await res.json();
            setSummary(data);
            setPayoutMethod(data.payout_method || "");
            setPayoutDetails(data.payout_details || "");
        } catch (e) {
            console.error("Network error while loading summary:", e);
            setSummary(null);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadSummary();
    }, []);

    const handleSave = async () => {
        if (typeof window === "undefined") return;

        const token = localStorage.getItem("token");
        if (!token) {
            alert("Please log in first.");
            return;
        }

        if (!payoutMethod.trim() || !payoutDetails.trim()) {
            alert("Please fill payout method and details.");
            return;
        }

        setSaving(true);
        try {
            const res = await fetch(`${API_BASE}/payments/me/payout-settings`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({
                    payout_method: payoutMethod,
                    payout_details: payoutDetails,
                }),
            });

            if (!res.ok) {
                const text = await res.text();
                console.error("Failed to save payout settings:", text);
                alert("Could not save payout settings. Try again.");
                return;
            }

            alert("Payout settings saved.");
            await loadSummary();
        } catch (e) {
            console.error("Network error while saving payout settings:", e);
            alert("Network error. Try again.");
        } finally {
            setSaving(false);
        }
    };

    const handleRequestPayout = async () => {
        if (typeof window === "undefined") return;

        const token = localStorage.getItem("token");
        if (!token) {
            alert("Please log in first.");
            return;
        }

        if (!summary) {
            alert("Balance is not loaded yet.");
            return;
        }

        if (summary.balance <= 0) {
            alert("You have no funds to withdraw.");
            return;
        }

        if (!payoutMethod.trim() || !payoutDetails.trim()) {
            alert("Please set payout method and details before requesting payout.");
            return;
        }

        if (!confirm("Request payout of your full available balance?")) {
            return;
        }

        setRequesting(true);
        try {
            const res = await fetch(`${API_BASE}/payments/me/payout-request`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({}),
            });

            const text = await res.text();

            if (!res.ok) {
                console.error("Failed to request payout:", text);
                try {
                    const err = JSON.parse(text);
                    alert(err.detail || "Could not request payout.");
                } catch {
                    alert("Could not request payout.");
                }
                return;
            }

            alert("Payout request created. We will process it soon.");
            await loadSummary();
        } catch (e) {
            console.error("Network error while requesting payout:", e);
            alert("Network error. Try again.");
        } finally {
            setRequesting(false);
        }
    };

    const balance = summary?.balance ?? 0;

    return (
        <AppLayout title="Settings">
            <div className="max-w-2xl mx-auto">
                <h1 className="text-2xl font-semibold text-slate-900 mb-4">
                    Settings
                </h1>

                <div className="bg-white shadow-sm rounded-2xl border border-slate-200 p-6 space-y-6">
                    <div>
                        <h2 className="text-sm font-semibold text-slate-800 mb-1">
                            Creator balance
                        </h2>
                        {loading ? (
                            <p className="text-sm text-slate-500">
                                Loading your balance...
                            </p>
                        ) : (
                            <p className="text-3xl font-semibold text-slate-900">
                                € {balance.toFixed(2)}
                            </p>
                        )}
                        <p className="text-xs text-slate-500 mt-1">
                            You receive 90% of each successful subscription payment.
                            Our platform fee is 10%.
                        </p>
                    </div>

                    <div className="border-t border-slate-200 pt-4">
                        <h2 className="text-sm font-semibold text-slate-800 mb-2">
                            Payout details
                        </h2>
                        <p className="text-xs text-slate-500 mb-3">
                            Add how we should pay you: IBAN (SEPA), Revolut, Wise or
                            crypto address. We will use these details when processing
                            your payout requests.
                        </p>

                        <div className="space-y-3">
                            <div>
                                <label className="block text-xs font-medium text-slate-700 mb-1">
                                    Payout method
                                </label>
                                <input
                                    type="text"
                                    value={payoutMethod}
                                    onChange={(e) => setPayoutMethod(e.target.value)}
                                    placeholder="Example: SEPA IBAN, Revolut, Wise, USDT TRC20"
                                    className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                                />
                            </div>
                            <div>
                                <label className="block text-xs font-medium text-slate-700 mb-1">
                                    Payout details
                                </label>
                                <textarea
                                    value={payoutDetails}
                                    onChange={(e) =>
                                        setPayoutDetails(e.target.value)
                                    }
                                    placeholder="Example: IBAN LT12 3456 ..., or Revolut @username, or USDT TRC20 wallet..."
                                    className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm min-h-[90px] focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                                />
                            </div>
                        </div>

                        <div className="flex items-center gap-3 mt-4">
                            <button
                                type="button"
                                onClick={handleSave}
                                disabled={saving}
                                className={`inline-flex items-center px-4 py-2 rounded-xl text-sm font-medium ${saving
                                        ? "bg-slate-200 text-slate-500 cursor-wait"
                                        : "bg-indigo-600 text-white hover:bg-indigo-700"
                                    }`}
                            >
                                {saving ? "Saving..." : "Save payout settings"}
                            </button>

                            <button
                                type="button"
                                onClick={handleRequestPayout}
                                disabled={requesting || loading || balance <= 0}
                                className={`inline-flex items-center px-4 py-2 rounded-xl text-sm font-medium border ${requesting || loading || balance <= 0
                                        ? "border-slate-200 text-slate-400 cursor-not-allowed"
                                        : "border-emerald-500 text-emerald-600 hover:bg-emerald-50"
                                    }`}
                            >
                                {requesting ? "Requesting..." : "Request payout"}
                            </button>
                        </div>
                        <p className="text-[11px] text-slate-400 mt-2">
                            Minimum payout amount is 20 EUR. We usually process payout
                            requests within a few days.
                        </p>
                    </div>
                </div>
            </div>
        </AppLayout>
    );
}

