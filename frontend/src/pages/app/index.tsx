import { useRouter } from "next/router";
import { useEffect } from "react";

export default function AppPage() {
    const router = useRouter();

    useEffect(() => {
        if (router.query.token) {
            localStorage.setItem("token", router.query.token as string);
            router.replace("/app/dashboard");
        }
    }, [router.query]);

    return <p>Loading...</p>;
}