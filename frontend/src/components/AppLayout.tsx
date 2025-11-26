import Link from "next/link";
import { useRouter } from "next/router";
import { ReactNode } from "react";

type Props = {
    title?: string;
    children: ReactNode;
};

const navItems = [
    { href: "/app/dashboard", label: "Dashboard" },
    { href: "/app/channels", label: "Channels" },
    // позже добавим Subscribers, Billing и т.п.
    { href: "/app/settings", label: "Settings" },
];

export default function AppLayout({ title, children }: Props) {
    const router = useRouter();

    return (
        <div className="min-h-screen bg-slate-50 text-slate-900 flex">
            {/* Sidebar */}
            <aside className="w-60 border-r border-slate-200 bg-white flex flex-col">
                <div className="px-5 py-4 border-b border-slate-200">
                    <Link href="/" className="text-lg font-bold tracking-tight">
                        subs<span className="text-indigo-600">.saas</span>
                    </Link>
                </div>

                <nav className="flex-1 px-3 py-4 space-y-1">
                    {navItems.map((item) => {
                        const active = router.pathname.startsWith(item.href);
                        return (
                            <Link
                                key={item.href}
                                href={item.href}
                                className={`block px-3 py-2 rounded-lg text-sm ${active
                                        ? "bg-indigo-50 text-indigo-700 font-medium"
                                        : "text-slate-600 hover:bg-slate-100"
                                    }`}
                            >
                                {item.label}
                            </Link>
                        );
                    })}
                </nav>

                <div className="px-4 py-4 border-t border-slate-200 text-xs text-slate-500">
                    <div>Logged in as</div>
                    <div className="font-medium">Creator</div>
                </div>
            </aside>

            {/* Main content */}
            <div className="flex-1 flex flex-col">
                <header className="h-14 border-b border-slate-200 bg-white flex items-center justify-between px-6">
                    <div className="text-sm font-medium text-slate-700">
                        {title || "Dashboard"}
                    </div>
                    <div className="flex items-center gap-3 text-sm text-slate-600">
                        <span className="hidden sm:inline">fanstero.netlify.app</span>
                        <span className="w-8 h-8 rounded-full bg-indigo-500 text-white flex items-center justify-center text-xs font-semibold">
                            CR
                        </span>
                    </div>
                </header>

                <main className="flex-1 px-6 py-6">{children}</main>
            </div>
        </div>
    );
}
