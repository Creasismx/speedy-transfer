import Link from "next/link";

export default function SponsorsPage() {
	return (
		<div className="mx-auto max-w-6xl px-4 py-12">
			<h1 className="text-2xl font-semibold">Sponsors</h1>
			<p className="text-foreground/70 mt-2 max-w-2xl">
				Partner with NightSyrc for cinematic product placements and authentic storytelling. Flexible packages for pre-rolls, mid-rolls, dedicated videos, and social promos.
			</p>
			<div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 mt-8">
				{[
					{ title: "Shoutout", price: "$250", features: ["Logo in description", "1x shoutout", "Link tracking"] },
					{ title: "Integration", price: "$750", features: ["45-60s mid-roll", "Talking points", "End-screen card"] },
					{ title: "Dedicated", price: "$2,000", features: ["Full video", "Creative brief", "Cross-post to socials"] },
				].map((tier) => (
					<div key={tier.title} className="rounded-lg border border-black/10 p-6 shadow-sm bg-white dark:border-white/10 dark:bg-black">
						<h3 className="font-semibold">{tier.title}</h3>
						<div className="text-2xl mt-1">{tier.price}</div>
						<ul className="mt-3 space-y-1 text-sm text-foreground/70">
							{tier.features.map((f) => (
								<li key={f}>• {f}</li>
							))}
						</ul>
					</div>
				))}
			</div>
			<div className="mt-8">
				<Link href="/contact" className="inline-flex items-center justify-center rounded-md bg-black px-5 py-2.5 text-sm font-medium text-white shadow hover:bg-black/90">Start a conversation</Link>
			</div>
		</div>
	);
}