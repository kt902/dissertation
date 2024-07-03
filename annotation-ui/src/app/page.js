import FilesTable from "@/components/FilesTable";
import Image from "next/image";
import Papa from 'papaparse';
import dataCSV from '@/data/epic_sample.csv';
import { Suspense } from 'react';

async function getData() {
    const data = await new Promise(async (res) => {
        Papa.parse(dataCSV, {
            delimiter: ',', // Specify comma delimiter
            header: true,
            skipEmptyLines: true,
            // dynamicTyping: true,
            quoteChar: '"', // Handle quoted fields
            escapeChar: '"',
            complete: function (results) {

                const data = results.data;
                const extractedData = data.map(row => ({
                    narration_id: row.narration_id,
                    narration: row.narration
                }));

                res(extractedData);
            }
        });
    });

    return data;
}

export default async function Home() {
    const data = await getData();

    return (
        <main className="flex min-h-screen flex-col items-center justify-center m-4">
            <h1 className="text-2xl sm:text-3xl font-extrabold">Annotation Dataset</h1>
            <div className="flex-grow w-full max-w-5xl items-center justify-center font-mono text-sm">
                <Suspense fallback={<div>Loading...</div>}>
                    <FilesTable files={data} />
                </Suspense>
            </div>
        </main>

    );
}
