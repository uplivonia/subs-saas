import { useEffect, useState } from "react";

export default function Dashboard() {
    const [user, setUser] = useState<any>(null);

    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) return;

        fetch("https://subs-saas.onrender.com/api/v1/users/me", {
            headers: { Authorization: `Bearer ${token}` },
        })
            .then((r) => r.json())
            .then(setUser);
    }, []);

    return (
        <div className="min-h-screen p-10">
            <h1 className="text-3xl font-bold">Dashboard</h1>
            {user ? (
                <p className="mt-4">Welcome, {user.name || "Creator"}!</p>
            ) : (
                <p>Loading user...</p>
            )}
        </div>
    );
}
