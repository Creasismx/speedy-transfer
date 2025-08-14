import Image from "next/image";
import Link from "next/link";
import type { YouTubeVideo } from "@/lib/youtube";

export default function VideoCard({ video }: { video: YouTubeVideo }) {
	return (
		<Link href={video.url} target="_blank" className="group block rounded-lg overflow-hidden border border-black/10 bg-white shadow-sm hover:shadow-md transition-shadow dark:border-white/10 dark:bg-black">
			<div className="relative aspect-video">
				<Image
					src={video.thumbnailUrl}
					alt={video.title}
					fill
					className="object-cover"
				/>
			</div>
			<div className="p-4">
				<h3 className="font-medium line-clamp-2 group-hover:underline">{video.title}</h3>
				<p className="text-xs text-foreground/60 mt-1">{new Date(video.publishedAt).toLocaleDateString()}</p>
			</div>
		</Link>
	);
}