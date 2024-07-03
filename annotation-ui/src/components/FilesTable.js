
"use client"

import { useState, useEffect, useCallback } from 'react';
import { DataGrid } from '@mui/x-data-grid';
import { useRouter, useSearchParams, usePathname } from 'next/navigation';

import fileMapping from '@/data/file-mapping.json';


function FilesTable({ files }) {
  const router = useRouter()
  const searchParams = useSearchParams()
  const pathname = usePathname()

  // Get a new searchParams string by merging the current
  // searchParams with a provided key/value pair
  const createQueryString = useCallback(
    (name, value) => {
      const params = new URLSearchParams(searchParams.toString())
      params.set(name, value)

      return params.toString()
    },
    [searchParams]
  )


  const [filesMap, setFilesMap] = useState({});
  const [file, _setFile] = useState(undefined);
  const setFile = useCallback((file) => {
    _setFile(file);
    router.push(pathname + '?' + createQueryString('narration_id', file.narration_id))
  }, [_setFile, createQueryString, pathname, router]);

  useEffect(() => {
    const fileMap = {};
    files.forEach(f => {
      fileMap[f.narration_id] = f;
    });

    const narration_id = searchParams.get('narration_id');
    setFilesMap(fileMap)
    setFile(fileMap[narration_id] || files[0]);
  }, [files, setFile, searchParams]);


  return (
    <div className='space-y-4'>
      {file &&
        <>
          {/* <h2>{file.narration}</h2> */}
          <div className="m-4 p-2 bg-red-500 text-white rounded-lg shadow-lg">
            {file.narration_id}: {file.narration}
          </div>

          <video
            className="h-full w-full rounded-lg"
            controls
            src={`https://kumbi-dissertation.s3.amazonaws.com/EPIC-KITCHENS-100/${fileMapping[file.narration_id]}`}
          />
        </>}

      <div className='bg-white'>
        <ul>
          <DataGrid
            rows={files}
            columns={
              [
                { field: 'narration_id', headerName: 'Narration ID', flex: 1, minWidth: 150, },
                { field: 'narration', headerName: 'Narration', flex: 1, minWidth: 150, },
              ]
            }
            initialState={{
              pagination: {
                paginationModel: { pageSize: 10, page: 0 },
              },
            }}
            onRowSelectionModelChange={rowID => {
              setFile(filesMap[rowID])
            }}
            pageSizeOptions={[10, 20, 50]}
            getRowId={(row) => row.narration_id}
          />
        </ul>
      </div>

    </div>
  );
}

export default FilesTable;
