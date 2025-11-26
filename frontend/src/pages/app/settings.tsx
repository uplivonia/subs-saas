import AppLayout from "@/components/AppLayout";

export default function SettingsPage() {
    return (
        <AppLayout title="Settings">
            <div className="max-w-3xl mx-auto space-y-4">
                <h1 className="text-2xl font-semibold">Settings</h1>
                <p className="text-sm text-slate-600">
                    Profile, language, and billing settings will live here later.
                </p>
                <div className="bg-white border border-slate-200 rounded-xl p-4 text-sm text-slate-600">
                    <p className="font-medium mb-1">Account</p>
                    <p>Email / Telegram-based account. Nothing to configure yet.</p>
                </div>
            </div>
        </AppLayout>
    );
}
