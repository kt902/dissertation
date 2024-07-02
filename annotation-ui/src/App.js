import './App.css';
import fileMapping from './file-mapping.json';
import { useState, useEffect } from 'react';
import { DataGrid } from '@mui/x-data-grid';
import Papa from 'papaparse';
import './App.css';
import dataCSV from './epic_sample.csv';

const data = new Promise(async (res) => {
  const response = await fetch(dataCSV);
  const csv = await response.text();

  Papa.parse(csv, {
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

function App() {
  const [files, setFiles] = useState([]);
  const [filesMap, setFilesMap] = useState({});
  const [file, setFile] = useState(undefined);

  useEffect(() => {
    data.then(d => {
      const files = d.map(r => r);
      const fileMap = {};
      files.forEach(f => {
        fileMap[f.narration_id] = f;
      });
      setFiles(files);
      setFilesMap(fileMap)
      setFile(files[0]);
    });
  }, []);


  const columns = [
    { field: 'narration_id', headerName: 'Narration ID', width: 500 },
    { field: 'narration', headerName: 'Narration', width: 500 },
  ];

  return (
    <div className="App">
      <h1>Annotation UI</h1>
      {file &&
        <div>
          <h2>{file.narration}</h2>
          <video controls src={`https://kumbi-dissertation.s3.amazonaws.com/EPIC-KITCHENS-100/${fileMapping[file.narration_id]}`} />
        </div>}

      <div>
        <ul>
          <DataGrid
            rows={files}
            columns={columns}
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

export default App;
