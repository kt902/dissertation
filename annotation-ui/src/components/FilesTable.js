"use client"

import { useState, useEffect, useCallback } from 'react';
import { DataGrid } from '@mui/x-data-grid';
import { useRouter, useSearchParams, usePathname } from 'next/navigation';

import fileMapping from '@/data/file-mapping.json';
import { Divider } from '@mui/material';


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


  const [isOpen, setIsOpen] = useState(false);

  const toggleCollapse = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div className='space-y-4'>
      {file &&
        <>
          {/* <h2>{file.narration}</h2> */}

          <div className="m-4 p-1 bg-red-500 text-white rounded-lg shadow-lg">
            {file.narration_id}: "{file.narration}"
          </div>
          {/* <div>
            <Video id={file.narration_id} />
            <Annotate />
          </div> */}
          <div className="flex flex-col md:flex-row">
            <div className="w-full md:w-2/3 p-4 flex items-center justify-center">
              <Video id={file.narration_id} />
            </div>
            <div className="w-full md:w-1/3 p-4">
              <button
                onClick={toggleCollapse}
                className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition duration-300"
              >
                {isOpen ? 'Collapse' : 'Expand'}
              </button>
              <div className={`${isOpen ? 'max-w-full' : 'max-w-0'}`}>
                <Annotate />
              </div>
            </div>

          </div>
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

// TODO: look at https://amittksharma.github.io/react-video-player-extended/example/index.html
function Video({ id }) {
  return <video
    className="w-full rounded-lg"
    controls
    src={`https://kumbi-dissertation.s3.amazonaws.com/EPIC-KITCHENS-100/${fileMapping[id]}`}
  />
}

              function Annotate() {
  const [responses, setResponses] = useState({
                question1: '',
              question2: '',
              question3: '',
  });

  const handleChange = (e) => {
    const {name, value} = e.target;
              setResponses({...responses, [name]: value });
  };

  const handleSubmit = async (e) => {
                e.preventDefault();
    // const response = await fetch('/api/submit-form', {
                //     method: 'POST',
                //     headers: {
                //         'Content-Type': 'application/json',
                //     },
                //     body: JSON.stringify(responses),
                // });
                // if (response.ok) {
                //     alert('Form submitted successfully!');
                // } else {
                //     alert('Failed to submit form.');
                // }
              };

              const questions = [
              {id: 'pixel', label: 'How would you rate the overall video resolution and sharpness?' },
              {id: 'primary-visible', label: 'How clearly visible are the primary objects involved in the action?' },
              {id: 'action-completeness', label: 'How completely does the video segment capture the entire action, including the beginning and end?' },
              {id: 'object-obscure', label: "To what extent are objects obscured by other objects or the person's hands?" }
              ]
              return (
              <form onSubmit={handleSubmit} className="mx-auto p-8 bg-white shadow-md rounded-md space-y-4">
                <h3 className="text-xl font-bold mb-6">Annotate</h3>
                {
                  questions.map(({ id, label }) => {
                    return (
                      <div key={id}>
                        <label className="block text-gray-700 font-semibold mb-2">{label}</label>
                        <div className="flex space-x-2 w-full">
                          {[1, 2, 3, 4, 5].map(value => (
                            <label key={value} className="flex flex-col items-center">
                              <input
                                type="radio"
                                name={id}
                                value={value}
                                checked={responses[id] === value.toString()}
                                onChange={handleChange}
                                className="mb-1"
                              />
                              <span>{value}</span>
                            </label>
                          ))}
                        </div>
                      </div>
                    );
                  })
                }
                <button type="submit" className="w-full px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition duration-300">
                  Save
                </button>
              </form>
              );
};


              export default FilesTable;
