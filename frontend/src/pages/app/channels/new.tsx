import AppLayout from "@/components/AppLayout";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";

const TELEGRAM_BOT_USERNAME = "oneclicksub_bot";
const API_BASE = "https://subs-saas.onrender.com/api/v1";

export default function AddChannelPage() {
    const router = useRouter();
    const [checking, setChecking] = useState(false);
    const [autoChecking, setAutoChecking] = useState(false);
    const [projectsCount, setProjectsCount] = useState<number | null>(null);

    const token =
        typeof window !== "undefined" ? localStorage.getItem("token") : null;

    // Deep-link that opens the bot in "creator" mode
    const creatorLink = `https://t.me/${TELEGRAM_BOT_USERNAME}?start=creator`;

    const checkProjectsAuto = async () => {
        try {
            const res = await fetch(`${API_BASE}/projects/`, {
                headers: {
                    "Content-Type": "application/json",
                    ...(token ? { Authorization: `Bearer ${token}` } : {}),
                },
            });

            if (!res.ok) {
                const text = await res.text();
                console.error("Error loading projects (auto):", text);
                return;
            }

            const data = await res.json();
            setProjectsCount(data.length || 0);

            if (data.length > 0) {
                // At least one channel is connected – send user to the channels list
                router.push("/app/channels");
                setAutoChecking(false);
            }
        } catch (e) {
            console.error("Network error while auto-checking channels.", e);
        }
    };

    const handleCheckManual = async () => {
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
                // Channel(s) already exist – send user to the list
                setTimeout(() => {
                    router.push("/app/channels");
                }, 800);
            } else {
                alert(
                    "No channels found yet. Make sure you added the bot as admin and completed the steps in Telegram."
                );
            }
        } catch (e) {
            console.error(e);
            alert("Network error while checking channels.");
        } finally {
            setChecking(false);
        }
    };

    const handleOpenTelegram = () => {
        // Open bot in Telegram in a new tab / app
        window.open(creatorLink, "_blank", "noopener,noreferrer");

        // Start automatic background checks so user doesn't have to click anything
        setAutoChecking(true);
    };

    useEffect(() => {
        if (!autoChecking) return;

        let cancelled = false;

        const loop = async () => {
            if (cancelled) return;
            await checkProjectsAuto();
            if (!cancelled) {
                setTimeout(loop, 4000);
            }
        };

        // start the polling loop
        loop();

        return () => {
            cancelled = true;
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [autoChecking]);

    return (
        <AppLayout title="Connect your private channel">
            <div className="max-w-2xl mx-auto">
                <h1 className="text-2xl font-semibold text-slate-900 mb-4">
                    Connect your private channel
                </h1>
                <p className="text-slate-600 mb-6">
                    We&apos;ll use our Telegram bot to securely connect your private
                    channel. You don&apos;t need a public @username — just add the bot
                    as an admin to your channel.
                </p>

                <div className="bg-white shadow-sm rounded-2xl border border-slate-200 p-6 space-y-6">
                    <div>
                        <h2 className="text-sm font-semibold text-slate-800 mb-2">
                            How it works
                        </h2>
                        <ol className="list-decimal list-inside text-sm text-slate-600 space-y-1">
                            <li>
                                Click the button below to open{" "}
                                <span className="font-mono">@{TELEGRAM_BOT_USERNAME}</span> in
                                Telegram.
                            </li>
                            <li>
                                In Telegram, follow the bot&apos;s instructions to connect
                                your private channel.
                            </li>
                            <li>
                                Keep this page open. We&apos;ll automatically detect your new
                                channel and redirect you once it&apos;s connected. You can
                                also press{" "}
                                <span className="font-medium">“Check connection”</span>{" "}
                                manually at any time.
                            </li>
                        </ol>
                    </div>

                    <div className="space-y-4">
                        <button
                            type="button"
                            onClick={handleOpenTelegram}
                            className="block w-full text-center bg-indigo-600 text-white py-3 rounded-xl font-medium hover:bg-indigo-700 transition-colors"
                        >
                            Open Telegram and connect channel
                        </button>

                        <button
                            type="button"
                            onClick={handleCheckManual}
                            disabled={checking}
                            className={`block w-full text-center border border-slate-300 py-3 rounded-xl font-medium ${checking
                                    ? "bg-slate-50 text-slate-400 cursor-wait"
                                    : "bg-white text-slate-700 hover:bg-slate-50"
                                }`}
                        >
                            {checking
                                ? "Checking..."
                                : "I have added the bot, check connection"}
                        </button>

                        {projectsCount !== null && (
                            <p className="text-xs text-slate-500">
                                Found{" "}
                                <span className="font-semibold">{projectsCount}</span>{" "}
                                project(s) linked to your account.
                            </p>
                        )}
                    </div>
                </div>
            </div>
        </AppLayout>
    );
}
