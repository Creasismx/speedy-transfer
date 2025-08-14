export default function ShopPage() {
	return (
		<div className="mx-auto max-w-6xl px-4 py-12">
			<h1 className="text-2xl font-semibold">Shop</h1>
			<p className="text-foreground/70 mt-2 max-w-2xl">
				Official NightSyrc merch and curated affiliate picks. Support the channel while getting gear you will love.
			</p>
			<div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 mt-8">
				{new Array(6).fill(null).map((_, i) => (
					<div key={i} className="rounded-lg border border-black/10 p-6 shadow-sm bg-white dark:border-white/10 dark:bg-black h-40" />
				))}
			</div>
		</div>
	);
}