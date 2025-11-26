import AppLayout from "@/components/AppLayout";

export default function ChannelsPage() {
    return (
        <AppLayout title="Channels">
            <div className="max-w-3xl mx-auto">
                <h1 className="text-2xl font-semibold mb-4">Channels</h1>
                <p className="text-sm text-slate-600 mb-4">
                    Here you will see all Telegram channels connected to your account.
                </p>
                <button className="px-4 py-2 rounded-lg bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-700">
                    + Add channel
                </button>
            </div>
        </AppLayout>
    );
}
