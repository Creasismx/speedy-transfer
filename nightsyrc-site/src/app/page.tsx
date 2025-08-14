import Link from "next/link";
import { SITE_NAME, SITE_TAGLINE, YOUTUBE_CHANNEL_URL } from "@/lib/site";
import { fetchRecentVideos } from "@/lib/youtube";
import VideoCard from "@/components/VideoCard";

export default async function Home() {
	const videos = await fetchRecentVideos(6);
	return (
		<div>
			<section className="relative overflow-hidden">
				<div className="mx-auto max-w-6xl px-4 py-16 md:py-24">
					<h1 className="text-4xl md:text-6xl font-semibold tracking-tight">
						{SITE_NAME}
					</h1>
					<p className="mt-4 max-w-2xl text-base md:text-lg text-foreground/70">
						{SITE_TAGLINE}
					</p>
					<div className="mt-6 flex gap-3">
						<Link
							href="/videos"
							className="inline-flex items-center justify-center rounded-md bg-black px-5 py-2.5 text-sm font-medium text-white shadow hover:bg-black/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-black/50"
						>
							Watch videos
						</Link>
						<a
							href={YOUTUBE_CHANNEL_URL}
							target="_blank"
							rel="noopener noreferrer"
							className="inline-flex items-center justify-center rounded-md border border-black/15 px-5 py-2.5 text-sm font-medium hover:bg-black/5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-black/20"
						>
							Subscribe on YouTube
						</a>
					</div>
				</div>
			</section>

			<section className="mx-auto max-w-6xl px-4 py-10">
				<div className="flex items-center justify-between mb-6">
					<h2 className="text-xl font-semibold">Latest uploads</h2>
					<Link href="/videos" className="text-sm text-foreground/70 hover:text-foreground">
						View all
					</Link>
				</div>
				<div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
					{videos.map((v) => (
						<VideoCard key={v.id} video={v} />
					))}
				</div>
			</section>
		</div>
	);
}
