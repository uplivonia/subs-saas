import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen flex items-center justify-center">
      <div className="max-w-md w-full p-8 bg-slate-800 rounded-2xl shadow-lg">
        <h1 className="text-2xl font-bold mb-4">
          Telegram Subscription Automation
        </h1>
        <p className="mb-6 text-sm text-slate-300">
          Automate access to your paid Telegram channels. You keep 100% of
          payments. We handle the automation.
        </p>
        <Link
          href="/login"
          className="inline-flex items-center justify-center w-full py-2 rounded-xl bg-indigo-500 hover:bg-indigo-600 transition"
        >
          Continue with Telegram
        </Link>
      </div>
    </main>
  );
}
