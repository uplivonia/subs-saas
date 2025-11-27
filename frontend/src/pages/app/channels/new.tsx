import AppLayout from "@/components/AppLayout";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";

const API_BASE = "https://subs-saas.onrender.com/api/v1";

export default function AddChannelPage() {
    const router = useRouter();
    const [loading, setLoading] = useState(false);
    const [projectId, setProjectId] = useState<number | null>(null);
    const [status, setStatus] = useState<string | null>(null);

    const token =
        typeof window !== "undefined" ? localStorage.getItem("token") : null;

    const createProject = async () => {
        if (!token) {
            alert("Missing auth token.");
            return null;
        }

        const payload = {
            title: "New Private Channel",
            active: true,
            owner_telegram_id: null, // backend reads user by JWT, not this
        };

        const res = await fetch(`${API_BASE}/projects/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({
                title: "New Private Channel",
                active: true,
            }),
        });

        if (!res.ok) {
            console.error(await res.text());
            alert("Failed to create project.");
            return null;
        }

        const project = await res.json();
        return project.id;
    };

    const getConnectLink = async (projectId: number) => {
        const res = await fetch(
            `${API_BASE}/projects/${projectId}/connect-link`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
            }
        );

        if (!res.ok) {
            console.error(await res.text());
            alert("Failed to get Telegram connect link.");
            return null;
        }

        const data = await res.json();
        return data.bot_link;
    };

    const pollProjectStatus = async (projectId: number) => {
        const res = await fetch(`${API_BASE}/projects/${projectId}`, {
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`,
            },
        });

        if (!res.ok) return null;

        const data = await res.json();
        return data.settings?.status || null;
    };

    const startPolling = (projectId: number) => {
        const interval = setInterval(async () => {
            const s = await pollProjectStatus(projectId);
            setStatus(s);

            if (s === "connected") {
                clearInterval(interval);
                router.push(`/app/channels`);
            }
        }, 3000);

        return () => clearInterval(interval);
    };

    const handleOpenTelegram = async () => {
        setLoading(true);

        // 1️⃣ Create project
        const id = await createProject();
        if (!id) {
            setLoading(false);
            return;
        }
        setProjectId(id);

        // 2️⃣ Get deep-link (bot_link)
        const botLink = await getConnectLink(id);
        if (!botLink) {
            setLoading(false);
            return;
        }

        // 3️⃣ Open Telegram bot
        window.open(botLink, "_blank");

        // 4️⃣ Start polling backend
        startPolling(id);
    };

    return (
        <AppLayout title="Connect your private channel">
            <div className="max-w-2xl mx-auto">
                <h1 className="text-2xl font-semibold text-slate-900 mb-4">
                    Connect your private channel
                </h1>
                <p className="text-slate-600 mb-6">
                    We will use our Telegram bot to securely connect your
                    private channel. Just add the bot as an admin — we detect
                    the rest automatically.
                </p>

                <div className="bg-white shadow-sm rounded-2xl border border-slate-200 p-6 space-y-6">
                    <div>
                        <h2 className="text-sm font-semibold text-slate-800 mb-2">
                            How it works
                        </h2>
                        <ol className="list-decimal list-inside text-sm text-slate-600 space-y-1">
                            <li>Click the button below to open the bot.</li>
                            <li>Add the bot as an admin to your private channel.</li>
                            <li>
                                Return here — we will automatically detect
                                when your channel is connected.
                            </li>
                        </ol>
                    </div>

                    <div className="space-y-4">
                        <button
                            type="button"
                            onClick={handleOpenTelegram}
                            disabled={loading}
                            className="block w-full text-center bg-indigo-600 text-white py-3 rounded-xl font-medium hover:bg-indigo-700 transition-colors"
                        >
                            {loading
                                ? "Connecting..."
                                : "Open Telegram and connect channel"}
                        </button>

                        {projectId && (
                            <p className="text-center text-sm text-slate-600">
                                Waiting for your channel to be connected…
                                <br />
                                Status:{" "}
                                <span className="font-medium">
                                    {status || "pending"}
                                </span>
                            </p>
                        )}
                    </div>
                </div>
            </div>
        </AppLayout>
    );
}
