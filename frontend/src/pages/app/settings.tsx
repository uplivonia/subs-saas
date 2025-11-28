import AppLayout from "@/components/AppLayout";

export default function SettingsPage() {
    return (
        <AppLayout title="Settings">
            <div className="max-w-2xl mx-auto">
                <h1 className="text-2xl font-semibold text-slate-900 mb-4">
                    Settings
                </h1>

                <div className="bg-white shadow-sm rounded-2xl border border-slate-200 p-6 space-y-4">
                    <h2 className="text-sm font-semibold text-slate-800">
                        Payouts
                    </h2>

                    <p className="text-sm text-slate-600">
                        All subscription payments are processed by our Stripe account.
                        You don&apos;t need to connect Stripe or any other payment
                        system.
                    </p>

                    <p className="text-sm text-slate-600">
                        Creators receive <span className="font-semibold">90%</span> of
                        each successful payment. Our platform fee is{" "}
                        <span className="font-semibold">10%</span>.
                    </p>

                    <p className="text-xs text-slate-500 mt-2">
                        Soon you&apos;ll be able to see your balance and request payouts
                        directly from this page.
                    </p>
                </div>
            </div>
        </AppLayout>
    );
}