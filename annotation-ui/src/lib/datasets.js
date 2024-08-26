'use server'

import fileMapping from '@/data/file-mapping.json';
import Papa from 'papaparse';
import dataCSV from '@/data/validations.csv';
import completeDataCSV from '@/data/epic_complete.csv';
import { cookies } from 'next/headers';
 
const getVideoURL = (narration_id) => {
    return `https://kumbi-dissertation.s3.amazonaws.com/EK-100/reduced/${narration_id}.mp4`;
};

async function fetchEntireDataset(sourceData) {
    const data = await new Promise((res) => {
        Papa.parse(sourceData, {
            delimiter: ',', // Specify comma delimiter
            header: true,
            skipEmptyLines: true,
            // dynamicTyping: true,
            quoteChar: '"', // Handle quoted fields
            escapeChar: '"',
            complete: function (results) {

                const dataArray = results.data.map(row => ({
                    narration_id: row.narration_id,
                    narration: row.narration,
                    url: getVideoURL(row.narration_id)
                }));

                // Create a Map for quick access by narration_id
                const dataMap = new Map(dataArray.map(item => [item.narration_id, item]));

                res({ list: dataArray, index: dataMap });
            }
        });
    });

    return data;
}


const validationDataset = fetchEntireDataset(dataCSV);
const completeDataset = fetchEntireDataset(completeDataCSV);

export const getAll = async () => {
    return (await getCurrentDataset()).list;
}

export const getRandomAnnotation = async () => {
    const items = await getAll();
    return items[Math.floor(Math.random() * items.length)];
}

export const getNarration = async (narration_id) => {
    return (await getCurrentDataset()).index.get(narration_id);
}

export const getNarrations = async (narration_ids) => {
    const result = {};
    for (let index = 0; index < narration_ids.length; index++) {
        const narration_id = narration_ids[index];
        
        const item = (await getCurrentDataset()).index.get(narration_id);
        result[narration_id] = item;
    }
    return result;
}

export const getCurrentDatasetName = async () => {
    return cookies().get('current_dataset')?.value || 'validation';
}

export const setCurrentDatasetName = async (dataset) => {
    cookies().set('current_dataset', dataset);
    return;
}


const getCurrentDataset = async () => {
    const datasetName = await getCurrentDatasetName();

    if (datasetName == 'complete') {
        return completeDataset;
    } else {
        return validationDataset;
    }
}

