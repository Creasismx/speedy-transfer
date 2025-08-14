export default function MembersPage() {
	return (
		<div className="mx-auto max-w-6xl px-4 py-12">
			<h1 className="text-2xl font-semibold">Members</h1>
			<p className="text-foreground/70 mt-2 max-w-2xl">
				Join NightSyrc Members for behind-the-scenes posts, early access, and exclusive wallpapers.
			</p>
			<div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 mt-8">
				{[
					{ title: "Supporter", price: "$3/mo", perks: ["Members-only posts", "Discord role"] },
					{ title: "Backstage", price: "$7/mo", perks: ["Early access", "Behind-the-scenes", "Wallpapers"] },
					{ title: "Producer", price: "$15/mo", perks: ["Name in description", "Monthly AMA", "All perks"] },
				].map((tier) => (
					<div key={tier.title} className="rounded-lg border border-black/10 p-6 shadow-sm bg-white dark:border-white/10 dark:bg-black">
						<h3 className="font-semibold">{tier.title}</h3>
						<div className="text-2xl mt-1">{tier.price}</div>
						<ul className="mt-3 space-y-1 text-sm text-foreground/70">
							{tier.perks.map((p) => (
								<li key={p}>• {p}</li>
							))}
						</ul>
						<button className="mt-4 inline-flex items-center justify-center rounded-md bg-black px-4 py-2 text-sm font-medium text-white shadow hover:bg-black/90">Join</button>
					</div>
				))}
			</div>
		</div>
	);
}