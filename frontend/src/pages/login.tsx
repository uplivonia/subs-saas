import { useEffect } from "react";
import Link from "next/link";

const TELEGRAM_BOT_USERNAME = "oneclicksub_bot"; // TODO: поменяешь на реальное имя бота без @
const TELEGRAM_AUTH_URL =
    "https://subs-saas.onrender.com/api/v1/auth/telegram"; // TODO: если у бэка другой URL — поменяем здесь

export default function Login() {
    useEffect(() => {
        // Рендерим Telegram-виджет ТОЛЬКО на клиенте
        const container = document.getElementById("telegram-login-container");
        if (!container) return;

        // очищаем на всякий случай
        container.innerHTML = "";

        const script = document.createElement("script");
        script.src = "https://telegram.org/js/telegram-widget.js?22";
        script.async = true;

        script.setAttribute("data-telegram-login", TELEGRAM_BOT_USERNAME);
        script.setAttribute("data-size", "large");
        script.setAttribute("data-userpic", "false");
        script.setAttribute("data-request-access", "write");
        script.setAttribute("data-auth-url", TELEGRAM_AUTH_URL);

        container.appendChild(script);

        return () => {
            container.innerHTML = "";
        };
    }, []);

    return (
        <div className="min-h-screen bg-white text-slate-900 flex flex-col">
            {/* Header */}
            <header className="w-full px-6 py-4 flex items-center justify-between border-b border-slate-200">
                <Link href="/" className="text-xl font-bold tracking-tight">
                    subs<span className="text-indigo-600">.saas</span>
                </Link>
                <Link
                    href="/"
                    className="px-4 py-2 rounded-lg border border-slate-300 text-sm hover:bg-slate-50"
                >
                    Back to home
                </Link>
            </header>

            {/* Content */}
            <main className="flex-1 flex items-center justify-center px-4">
                <div className="w-full max-w-md border border-slate-200 rounded-2xl shadow-sm p-8 bg-white">
                    <h1 className="text-2xl font-semibold mb-2">
                        Sign in with Telegram
                    </h1>
                    <p className="text-sm text-slate-600 mb-6">
                        Use your Telegram account to access your creator dashboard. No
                        passwords, no forms — just a quick and secure login.
                    </p>

                    <div
                        id="telegram-login-container"
                        className="flex items-center justify-center mb-4"
                    />

                    <p className="text-xs text-slate-500">
                        By continuing, you allow us to read your Telegram ID and basic
                        profile information to create your creator account.
                    </p>
                </div>
            </main>
        </div>
    );
}
