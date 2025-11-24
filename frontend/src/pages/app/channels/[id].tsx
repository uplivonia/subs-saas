import { useRouter } from "next/router";

export default function ChannelDetails() {
  const router = useRouter();
  const { id } = router.query;

  return (
    <div className="p-4">
      <h2 className="text-lg font-semibold mb-2">Channel {id}</h2>
      <p>Here you will configure subscription plans and see analytics.</p>
    </div>
  );
}
