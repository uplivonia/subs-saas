import { useState } from "react";
import AppLayout from "@/components/AppLayout";
import { useRouter } from "next/router";


export default function AddChannelPage() {
    const router = useRouter();

    const [step, setStep] = useState(1);

    const [projectId, setProjectId] = useState<number | null>(null);

    // ---- FORM STATE ----
    const [channel, setChannel] = useState("");
    const [title, setTitle] = useState("");
    const [desc, setDesc] = useState("");

    const [price, setPrice] = useState("4.99");

    const [checkingBot, setCheckingBot] = useState(false);
    const [botOK, setBotOK] = useState(false);

    // ---- API BASE ----
    const API_BASE = "https://subs-saas.onrender.com/api/v1";

    const token =
        typeof window !== "undefined" ? localStorage.getItem("token") : null;

    // ------------------------------------------
    // STEP 1 → CREATE PROJECT
    // ------------------------------------------
    const handleCreateProject = async () => {
        if (!channel.trim()) {
            alert("Please enter a channel username");
            return;
        }

        const body = {
            channel_username: channel.replace("@", "").trim(),
            title: title || channel,
            description: desc,
        };

        const res = await fetch(`${API_BASE}/projects/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: token ? `Bearer ${token}` : "",
            },
            body: JSON.stringify(body),
        });

        if (!res.ok) {
            alert("Error creating project");
            return;
        }

        const data = await res.json();
        setProjectId(data.id);
        setStep(2);
    };

    // ------------------------------------------
    // STEP 2 → CREATE PLAN
    // ------------------------------------------
    const handleCreatePlan = async () => {
        if (!projectId) return;

        const body = {
            project_id: projectId,
            name: "Monthly subscription",
            price: Number(price),
            currency: "USD",
            interval: "monthly",
        };

        const res = await fetch(`${API_BASE}/plans/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: token ? `Bearer ${token}` : "",
            },
            body: JSON.stringify(body),
        });

        if (!res.ok) {
            alert("Error creating plan");
            return;
        }

        setStep(3);
    };

    // ------------------------------------------
    // STEP 3 → CHECK BOT ADMIN STATUS
    // ------------------------------------------
    const handleCheckBot = async () => {
        if (!projectId) return;

        setCheckingBot(true);

        const res = await fetch(`${API_BASE}/projects/${projectId}/check_bot`, {
            headers: {
                Authorization: token ? `Bearer ${token}` : "",
            },
        });

        setCheckingBot(false);

        const data = await res.json();

        if (data.ok) {
            setBotOK(true);
            setTimeout(() => {
                router.push("/app/channels");
            }, 1500);
        } else {
            alert("Bot is not admin yet. Please add @FansteroBot as admin.");
        }
    };

    // ==========================================
    // RENDER
    // ==========================================
    return (
        <AppLayout title="Add Channel">
            <div className="max-w-xl mx-auto bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
                <h1 className="text-2xl font-semibold mb-1">
                    Add Telegram Channel
                </h1>
                <p className="text-sm text-slate-600 mb-6">
                    Connect your channel and start selling subscriptions.
                </p>

                {/* PROGRESS STEPS */}
                <div className="flex items-center justify-between mb-6">
                    {[1, 2, 3].map((s) => (
                        <div
                            key={s}
                            className={`w-full h-1 mx-1 rounded-full ${step >= s ? "bg-indigo-600" : "bg-slate-200"
                                }`}
                        />
                    ))}
                </div>

                {step === 1 && (
                    <div className="space-y-4">
                        <div>
                            <label className="text-sm font-medium">Channel username</label>
                            <input
                                className="w-full mt-1 px-3 py-2 border border-slate-300 rounded-lg"
                                placeholder="@mychannel"
                                value={channel}
                                onChange={(e) => setChannel(e.target.value)}
                            />
                        </div>

                        <div>
                            <label className="text-sm font-medium">Title (optional)</label>
                            <input
                                className="w-full mt-1 px-3 py-2 border border-slate-300 rounded-lg"
                                placeholder="My Channel"
                                value={title}
                                onChange={(e) => setTitle(e.target.value)}
                            />
                        </div>

                        <div>
                            <label className="text-sm font-medium">Description (optional)</label>
                            <textarea
                                className="w-full mt-1 px-3 py-2 border border-slate-300 rounded-lg"
                                rows={3}
                                placeholder="What is this channel about?"
                                value={desc}
                                onChange={(e) => setDesc(e.target.value)}
                            />
                        </div>

                        <button
                            onClick={handleCreateProject}
                            className="mt-4 w-full bg-indigo-600 text-white py-3 rounded-xl font-medium hover:bg-indigo-700"
                        >
                            Next
                        </button>
                    </div>
                )}

                {step === 2 && (
                    <div className="space-y-4">
                        <div>
                            <label className="text-sm font-medium">Monthly price (USD)</label>
                            <input
                                className="w-full mt-1 px-3 py-2 border border-slate-300 rounded-lg"
                                value={price}
                                onChange={(e) => setPrice(e.target.value)}
                            />
                        </div>

                        <button
                            onClick={handleCreatePlan}
                            className="mt-4 w-full bg-indigo-600 text-white py-3 rounded-xl font-medium hover:bg-indigo-700"
                        >
                            Next
                        </button>
                    </div>
                )}

                {step === 3 && (
                    <div className="space-y-4">
                        <p className="text-slate-700 text-sm">
                            Please add <strong>@FansteroBot</strong> as an administrator to your Telegram channel.
                            Enable permissions: <strong>Add users</strong> and <strong>Remove users</strong>.
                        </p>

                        <button
                            onClick={handleCheckBot}
                            className="mt-4 w-full bg-indigo-600 text-white py-3 rounded-xl font-medium hover:bg-indigo-700"
                        >
                            {checkingBot ? "Checking..." : "Check bot status"}
                        </button>

                        {botOK && (
                            <div className="text-green-600 text-sm pt-2 font-medium">
                                ✓ Bot is admin! Redirecting...
                            </div>
                        )}
                    </div>
                )}
            </div>
        </AppLayout>
    );
}
