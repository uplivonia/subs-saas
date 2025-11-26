import AppLayout from "@/components/AppLayout";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";

const TELEGRAM_BOT_USERNAME = "oneclicksub_bot";
const API_BASE = "https://subs-saas.onrender.com/api/v1";

export default function AddChannelPage() {
    const router = useRouter();
    const [checking, setChecking] = useState(false);
    const [projectsCount, setProjectsCount] = useState<number | null>(null);

    const creatorLink = `https://t.me/${TELEGRAM_BOT_USERNAME}?start=creator`;

    const token =
        typeof window !== "undefined" ? localStorage.getItem("token") : null;

    const handleCheck = async () => {
        setChecking(true);
        try {
            const res = await fetch(`${API_BASE}/projects/`, {
                headers: {
                    "Content-Type": "application/json",
                    ...(token ? { Authorization: `Bearer ${token}` } : {}),
                },
            });

            if (!res.ok) {
                const text = await res.text();
                console.error("Error loading projects:", text);
                alert("Could not check channels yet. Try again in a few seconds.");
                setChecking(false);
                return;
            }

            const data = await res.json();
            setProjectsCount(data.length || 0);

            if (data.length > 0) {
                // Канал(ы) уже есть — отправляем в список
                setTimeout(() => {
                    router.push("/app/channels");
                }, 1000);
            } else {
                alert(
                    "No channels found yet. Make sure you added the bot and forwarded a message from your channel."
                );
            }
        } catch (e) {
            console.error(e);
            alert("Network error while checking channels.");
        } finally {
            setChecking(false);
        }
    };

    return (
        <AppLayout title="Add Channel">
            <div className="max-w-xl mx-auto bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
                <h1 className="text-2xl font-semibold mb-2">
                    Connect your private channel
                </h1>
                <p className="text-sm text-slate-600 mb-6">
                    We will use Telegram bot to securely connect your private channel.
                    You don&apos;t need @username — just add the bot to your channel.
                </p>

                <ol className="text-sm text-slate-700 space-y-3 mb-6 list-decimal list-inside">
                    <li>
                        Click the button below to open{" "}
                        <span className="font-medium">@{TELEGRAM_BOT_USERNAME}</span> in
                        Telegram.
                    </li>
                    <li>
                        In Telegram, follow the instructions:
                        <br />
                        <span className="text-slate-600">
                            – add the bot as an admin to your private channel <br />
                            – forward any message from that channel to the bot
                        </span>
                    </li>
                    <li>
                        Come back here and press{" "}
                        <span className="font-medium">“Check connection”</span>.
                    </li>
                </ol>

                <div className="space-y-4">
                    <a
                        href={creatorLink}
                        target="_blank"
                        rel="noreferrer"
                        className="block w-full text-center bg-indigo-600 text-white py-3 rounded-xl font-medium hover:bg-indigo-700"
                    >
                        Open Telegram and connect channel
                    </a>

                    <button
                        onClick={handleCheck}
                        className="w-full border border-slate-300 text-slate-800 py-3 rounded-xl text-sm hover:bg-slate-50"
                        disabled={checking}
                    >
                        {checking ? "Checking..." : "I have added the bot, check connection"}
                    </button>

                    {projectsCount !== null && (
                        <p className="text-xs text-slate-500">
                            Found <span className="font-semibold">{projectsCount}</span>{" "}
                            project(s) linked to your account.
                        </p>
                    )}
                </div>
            </div>
        </AppLayout>
    );
}
