import FilesTable from "@/components/FilesTable";
import Image from "next/image";
import { Suspense } from 'react';
import datasets from '@/lib/datasets';
import { getAnnotations } from "@/lib/actions";
import MyAnnotations from "./client";

export default async function MyAnnotationsServer() {
    let {data: annotations} = await getAnnotations();
    const data = await datasets.getNarrations(annotations.map(a => a.narration_id));
    annotations = annotations.map(a => { return {...a, ...data[a.narration_id]}})

    const allCount = annotations.length;
    const completeCount = annotations.filter(a => a.status == 'complete').length;

    return (
        <main className="flex min-h-screen flex-col items-center justify-center m-4">
            <div className="flex-grow w-full max-w-5xl">
                <h2 className="text-2xl sm:text-3xl font-extrabold">My Annotations</h2>
                <Suspense fallback={<div>Loading...</div>}>
                    <MyAnnotations annotations={annotations} allCount={allCount} completeCount={completeCount} />
                </Suspense>
            </div>
        </main>

    );
}
