import { NextResponse } from "next/server";
import { fetchRecentVideos } from "@/lib/youtube";

export const revalidate = 60;

export async function GET() {
	const videos = await fetchRecentVideos(12);
	return NextResponse.json({ videos });
}