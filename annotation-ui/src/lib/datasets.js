import fileMapping from '@/data/file-mapping.json';
import Papa from 'papaparse';
import dataCSV from '@/data/epic_sample.csv';

const getVideoURL = (narration_id) => {
    return `https://kumbi-dissertation.s3.amazonaws.com/EPIC-KITCHENS-100/${fileMapping[narration_id]}`;
};

async function fetchEntireDataset() {
    const data = await new Promise((res) => {
        Papa.parse(dataCSV, {
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


const dataset = fetchEntireDataset();

export const getAll = async () => {
    return (await dataset).list;
}

export const getRandomAnnotation = async () => {
    const items = await getAll();
    return items[Math.floor(Math.random() * items.length)];
}

export const getNarration = async (narration_id) => {
    return (await dataset).index.get(narration_id);
}

export const getNarrations = async (narration_ids) => {
    const result = {};
    for (let index = 0; index < narration_ids.length; index++) {
        const narration_id = narration_ids[index];
        
        const item = (await dataset).index.get(narration_id);
        result[narration_id] = item;
    }
    return result;
}


export default {
    getAll,
    getNarration,
    getRandomAnnotation,
    getNarrations
}
