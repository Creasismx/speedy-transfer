export type YouTubeVideo = {
	id: string;
	title: string;
	thumbnailUrl: string;
	publishedAt: string;
	url: string;
};

type SearchItem = {
	id?: { videoId?: string };
	snippet?: {
		title?: string;
		publishedAt?: string;
		thumbnails?: {
			high?: { url?: string };
			medium?: { url?: string };
			default?: { url?: string };
		};
	};
};

const SAMPLE_VIDEOS: YouTubeVideo[] = [
	{
		id: "dQw4w9WgXcQ",
		title: "Sample Highlight #1",
		thumbnailUrl: "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
		publishedAt: "2024-01-01T00:00:00Z",
		url: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
	},
	{
		id: "oHg5SJYRHA0",
		title: "Sample Highlight #2",
		thumbnailUrl: "https://i.ytimg.com/vi/oHg5SJYRHA0/hqdefault.jpg",
		publishedAt: "2024-02-01T00:00:00Z",
		url: "https://www.youtube.com/watch?v=oHg5SJYRHA0",
	},
];

export async function fetchRecentVideos(maxResults: number = 8): Promise<YouTubeVideo[]> {
	const apiKey = process.env.YOUTUBE_API_KEY;
	const channelId = process.env.YOUTUBE_CHANNEL_ID;

	if (!apiKey || !channelId) {
		return SAMPLE_VIDEOS;
	}

	const params = new URLSearchParams({
		key: apiKey,
		channelId,
		part: "snippet",
		order: "date",
		maxResults: String(maxResults),
		type: "video",
	});

	const url = `https://www.googleapis.com/youtube/v3/search?${params.toString()}`;

	try {
		const res = await fetch(url, { next: { revalidate: 60 } });
		if (!res.ok) {
			return SAMPLE_VIDEOS;
		}
		const data = await res.json();
		const items = (data.items || []) as SearchItem[];
		return items.map((item) => {
			const id = item.id?.videoId ?? "";
			const snippet = item.snippet ?? {};
			const title = snippet.title ?? "Untitled";
			const publishedAt = snippet.publishedAt ?? new Date().toISOString();
			const thumbnailUrl =
				snippet.thumbnails?.high?.url ||
				snippet.thumbnails?.medium?.url ||
				snippet.thumbnails?.default?.url ||
				"https://i.ytimg.com/vi_webp/unknown/hqdefault.webp";
			return {
				id,
				title,
				thumbnailUrl,
				publishedAt,
				url: `https://www.youtube.com/watch?v=${id}`,
			} satisfies YouTubeVideo;
		});
	} catch {
		return SAMPLE_VIDEOS;
	}
}