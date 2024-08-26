import * as datasets from '@/lib/datasets';
import { getAnnotationByNarrationId, getRandomPendingAnnotation } from '@/lib/actions';
import Annotate from './client';
import { redirect } from 'next/navigation';
import { getServerSession } from "next-auth/next"
import { authOptions } from "@/app/api/auth/[...nextauth]/route";
import { notFound } from 'next/navigation';

export const dynamic = 'force-dynamic'
export const revalidate = 0


export default async function AnnotateServer({ params }) {
    // const session = await getServerSession(authOptions);

    const { narration_id } = params;

    if (narration_id == "random") {
        const { annotation } = await getRandomPendingAnnotation();
        // console.log("annotate", annotation)

        if (!annotation) {
            return notFound();
        }

        return redirect(`/annotate/${annotation.narration_id}`);
    }

    const { annotation, allCount, completeCount } = await getAnnotationByNarrationId(narration_id);

    if (!annotation) {
        return notFound();
    }

    const file = await datasets.getNarration(narration_id);

    return (
        <Annotate
            file={file}
            annotation={annotation.annotation}
            completeCount={completeCount}
            allCount={allCount} />
    );
}
