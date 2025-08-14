import { fetchRecentVideos } from "@/lib/youtube";
import VideoCard from "@/components/VideoCard";

export const revalidate = 60;

export default async function VideosPage() {
	const videos = await fetchRecentVideos(18);
	return (
		<div className="mx-auto max-w-6xl px-4 py-12">
			<h1 className="text-2xl font-semibold mb-6">Videos</h1>
			<div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
				{videos.map((v) => (
					<VideoCard key={v.id} video={v} />
				))}
			</div>
		</div>
	);
}