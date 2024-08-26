import {getAllCompleteAnnotations} from "@/lib/actions";

export async function GET() {
    const response = await getAllCompleteAnnotations();

    return Response.json(response);
}
