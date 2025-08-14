"use client";

import Link from "next/link";
import { NAV_LINKS, SITE_NAME, YOUTUBE_CHANNEL_URL } from "@/lib/site";
import { usePathname } from "next/navigation";

export default function Header() {
	const pathname = usePathname();
	return (
		<header className="sticky top-0 z-40 w-full border-b border-black/10 bg-white/80 backdrop-blur supports-[backdrop-filter]:bg-white/60 dark:border-white/10 dark:bg-black/60">
			<div className="mx-auto max-w-6xl px-4 py-4 flex items-center justify-between">
				<Link href="/" className="font-semibold tracking-tight text-xl">
					{SITE_NAME}
				</Link>
				<nav className="hidden md:flex items-center gap-6 text-sm">
					{NAV_LINKS.map((link) => {
						const active = pathname === link.href;
						return (
							<Link
								key={link.href}
								href={link.href}
								className={
									"transition-colors hover:text-foreground/80 " +
									(active ? "text-foreground" : "text-foreground/60")
								}
							>
								{link.label}
							</Link>
						);
					})}
				</nav>
				<div className="flex items-center gap-3">
					<a
						href={YOUTUBE_CHANNEL_URL}
						target="_blank"
						rel="noopener noreferrer"
						className="inline-flex items-center justify-center rounded-md bg-black px-4 py-2 text-sm font-medium text-white shadow hover:bg-black/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-black/50"
					>
						Subscribe
					</a>
				</div>
			</div>
		</header>
	);
}