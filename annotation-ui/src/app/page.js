import FilesTable from "@/components/FilesTable";
import Image from "next/image";
import { Suspense } from 'react';
import datasets from '@/lib/datasets';

export default async function Home() {
    const data = await datasets.getAll();

    return (
        <main className="flex min-h-screen flex-col items-center justify-center m-4">
            <div className="flex-grow w-full max-w-5xl">
                <h2 className="text-2xl sm:text-3xl font-extrabold">Validation Dataset</h2>
                <Suspense fallback={<div>Loading...</div>}>
                    <FilesTable files={data} />
                </Suspense>
            </div>
        </main>

    );
}
