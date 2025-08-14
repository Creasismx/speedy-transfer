import Link from "next/link";
import { SOCIAL_LINKS, SITE_NAME } from "@/lib/site";

export default function Footer() {
	return (
		<footer className="mt-16 border-t border-black/10 dark:border-white/10">
			<div className="mx-auto max-w-6xl px-4 py-10 grid gap-6 sm:grid-cols-2">
				<div>
					<div className="font-semibold">{SITE_NAME}</div>
					<p className="text-sm text-foreground/60 mt-2">
						© {new Date().getFullYear()} {SITE_NAME}. All rights reserved.
					</p>
				</div>
				<div className="flex items-center gap-4 justify-start sm:justify-end">
					{SOCIAL_LINKS.youtube && (
						<Link href={SOCIAL_LINKS.youtube} className="text-sm text-foreground/70 hover:text-foreground" target="_blank">
							YouTube
						</Link>
					)}
					{SOCIAL_LINKS.instagram && (
						<Link href={SOCIAL_LINKS.instagram} className="text-sm text-foreground/70 hover:text-foreground" target="_blank">
							Instagram
						</Link>
					)}
					{SOCIAL_LINKS.twitter && (
						<Link href={SOCIAL_LINKS.twitter} className="text-sm text-foreground/70 hover:text-foreground" target="_blank">
							Twitter/X
						</Link>
					)}
					{SOCIAL_LINKS.tiktok && (
						<Link href={SOCIAL_LINKS.tiktok} className="text-sm text-foreground/70 hover:text-foreground" target="_blank">
							TikTok
						</Link>
					)}
				</div>
			</div>
		</footer>
	);
}