import { getAllCompleteAnnotations } from "@/lib/actions";
import { getAnyNarration } from "@/lib/datasets";
import Papa from 'papaparse';

export const dynamic = 'force-dynamic';
export const revalidate = 0;

export async function GET() {
    const { success, data } = await getAllCompleteAnnotations();
    if (!success) {
        return new Response(null, {status: 500});
    }
    // Transform the JSON structure to a flat array
    const flatData = data.map(async ({ user_id, narration_id, annotation }) => {
        const narration = await getAnyNarration(narration_id);
        return {
            user_id,
            narration_id,
            participant_id: narration.participant_id,
            video_id: narration.video_id,
            ...annotation,
        }
    });

    // Convert JSON to CSV
    const csv = Papa.unparse(await Promise.all(flatData));
    return new Response(csv, {
        headers: {
            // 'Content-Disposition': `attachment; filename="ek-100-annotation-data.csv"`,
            // 'Content-Type': 'text/csv',
        }
    });
}
