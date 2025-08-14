export default function ContactPage() {
	return (
		<div className="mx-auto max-w-2xl px-4 py-12">
			<h1 className="text-2xl font-semibold">Contact</h1>
			<p className="text-foreground/70 mt-2">
				Business inquiries, collaborations, or feedback — get in touch.
			</p>
			<form className="mt-6 space-y-4">
				<div>
					<label className="block text-sm mb-1" htmlFor="name">Name</label>
					<input id="name" className="w-full rounded-md border border-black/15 bg-transparent px-3 py-2 outline-none focus:ring-2 focus:ring-black/20" placeholder="Your name" />
				</div>
				<div>
					<label className="block text-sm mb-1" htmlFor="email">Email</label>
					<input id="email" type="email" className="w-full rounded-md border border-black/15 bg-transparent px-3 py-2 outline-none focus:ring-2 focus:ring-black/20" placeholder="you@example.com" />
				</div>
				<div>
					<label className="block text-sm mb-1" htmlFor="message">Message</label>
					<textarea id="message" rows={6} className="w-full rounded-md border border-black/15 bg-transparent px-3 py-2 outline-none focus:ring-2 focus:ring-black/20" placeholder="How can we help?" />
				</div>
				<button type="button" className="inline-flex items-center justify-center rounded-md bg-black px-5 py-2.5 text-sm font-medium text-white shadow hover:bg-black/90">Send</button>
			</form>
		</div>
	);
}