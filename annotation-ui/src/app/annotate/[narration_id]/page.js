import datasets from '@/lib/datasets';
import { getAnnotationByNarrationId } from '@/lib/actions';
import Annotate from './client';
import { redirect } from 'next/navigation';

export const dynamic = 'force-dynamic'
export const revalidate = 0

export async function generateMetadata() {
    return {
        headers: {
            'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
        },
    };
}

export default async function AnnotateServer({ params }) {
    const { narration_id } = params;

    const { annotation } = await getAnnotationByNarrationId(narration_id);

    if (narration_id == "random") {
        const specificAnnotation = (await datasets.getRandomAnnotation()).narration_id;
        return redirect(`/annotate/${specificAnnotation}`);
    }
    const file = await datasets.getNarration(narration_id);

    return (
        <Annotate file={file} annotation={annotation} />
    );
}
