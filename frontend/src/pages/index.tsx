import Link from "next/link";

export default function Home() {
    return (
        <div className="min-h-screen bg-white text-slate-900 flex flex-col">
            {/* Header */}
            <header className="w-full px-6 py-4 flex items-center justify-between border-b border-slate-200">
                <div className="text-xl font-bold tracking-tight">
                    subs<span className="text-indigo-600">.saas</span>
                </div>
                <Link
                    href="/login"
                    className="px-4 py-2 rounded-lg border border-slate-300 text-sm hover:bg-slate-50"
                >
                    Sign in
                </Link>
            </header>

            {/* Hero */}
            <main className="flex-1 flex items-center justify-center px-6">
                <div className="max-w-4xl mx-auto grid md:grid-cols-2 gap-12 items-center py-16">
                    {/* Text */}
                    <div className="space-y-6">
                        <h1 className="text-4xl md:text-5xl font-bold tracking-tight leading-tight">
                            Turn your Telegram channel
                            <span className="block text-indigo-600">
                                into a subscription business.
                            </span>
                        </h1>

                        <p className="text-slate-600 text-lg max-w-md">
                            Connect your channel, set a price, and start selling subscriptions
                            in minutes. No coding, no friction — everything is automated.
                        </p>

                        <div className="flex gap-4">
                            <Link
                                href="/login"
                                className="px-6 py-3 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700"
                            >
                                Start with Telegram
                            </Link>
                            <Link
                                href="/app"
                                className="px-6 py-3 border border-slate-300 rounded-xl text-sm hover:bg-slate-50"
                            >
                                View demo
                            </Link>
                        </div>

                        <p className="text-xs text-slate-500">
                            Simple setup · Stripe payments · Automatic channel access
                        </p>
                    </div>

                    {/* Mini dashboard card */}
                    <div className="border border-slate-200 rounded-2xl shadow-sm p-6 bg-white">
                        <div className="text-sm text-slate-500 mb-4">Dashboard preview</div>
                        <div className="space-y-4 text-sm">
                            <div className="flex justify-between">
                                <span>Monthly revenue</span>
                                <strong>$1,245</strong>
                            </div>
                            <div className="flex justify-between">
                                <span>Active subscribers</span>
                                <strong>327</strong>
                            </div>
                            <div className="flex justify-between">
                                <span>Connected channels</span>
                                <strong>3</strong>
                            </div>

                            <div className="pt-4 border-t border-slate-200">
                                <p className="text-slate-500 mb-2">Get started in 3 steps:</p>
                                <ol className="list-decimal ml-5 space-y-1 text-slate-700">
                                    <li>Sign in with Telegram</li>
                                    <li>Connect your channel</li>
                                    <li>Start accepting payments</li>
                                </ol>

                                <Link
                                    href="/app/channels"
                                    className="mt-4 inline-flex w-full items-center justify-center px-4 py-2 text-indigo-600 border border-indigo-200 rounded-lg hover:bg-indigo-50"
                                >
                                    + Add channel
                                </Link>
                            </div>
                        </div>
                    </div>
                </div>
            </main>

            {/* Steps section */}
            <section className="max-w-4xl mx-auto px-6 pb-12">
                <h2 className="text-2xl font-semibold mb-8 text-center">
                    Launch your paid channel in 2–3 clicks
                </h2>

                <div className="grid md:grid-cols-3 gap-8 text-sm">
                    <div>
                        <h3 className="font-medium text-base mb-1">
                            1. Sign in with Telegram
                        </h3>
                        <p className="text-slate-600">
                            Secure Telegram authentication — no passwords or forms.
                        </p>
                    </div>
                    <div>
                        <h3 className="font-medium text-base mb-1">
                            2. Connect your channel
                        </h3>
                        <p className="text-slate-600">
                            Paste your channel, set a monthly price, and we generate a
                            subscription flow for you.
                        </p>
                    </div>
                    <div>
                        <h3 className="font-medium text-base mb-1">
                            3. Automate access
                        </h3>
                        <p className="text-slate-600">
                            We automatically add paying members and remove expired ones via
                            your bot.
                        </p>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="w-full px-6 py-6 border-t border-slate-200 text-sm text-slate-500 flex justify-between">
                <span>© {new Date().getFullYear()} subs.saas</span>
                <span>Built for Telegram creators</span>
            </footer>
        </div>
    );
}

