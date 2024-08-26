import { getAllCompleteAnnotations } from "@/lib/actions";
import Papa from 'papaparse';

export async function GET() {
    const { success, data } = await getAllCompleteAnnotations();
    if (!success) {
        return new Response(null, {status: 500});
    }
    // Transform the JSON structure to a flat array
    const flatData = data.map(({ user_id, narration_id, annotation }) => ({
        user_id,
        narration_id,
        ...annotation
    }));

    // Convert JSON to CSV
    const csv = Papa.unparse(flatData);
    return new Response(csv, {
        headers: {
            // 'Content-Disposition': `attachment; filename="ek-100-annotation-data.csv"`,
            // 'Content-Type': 'text/csv',
        }
    });
}
