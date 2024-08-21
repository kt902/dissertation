"use client";

import { useState } from 'react';
import { DataGrid } from '@mui/x-data-grid';
import Link from 'next/link';

function MyAnnotations({ annotations }) {
  const [selection, setSelection] = useState(undefined);

  // Map statuses to display labels or styled components
  const statusDisplayMap = {
    complete: "✅ Completed",
    pending: "⏳ Pending",
    // in_progress: "In Progress",
    // review: "Under Review"
  };

  return (
    <div className='my-4 space-y-4'>
      <div className='bg-white'>
        <DataGrid
          rows={annotations}
          columns={[
            {
              field: 'narration_id',
              headerName: 'Narration ID',
              flex: 1,
              minWidth: 150,
              renderCell: (params) => (
                <Link href={`/annotate/${params.value}`} style={{textDecoration: 'underline'}}passHref>
                  {params.value}
                </Link>
              ),
            },
            {
              field: 'status',
              headerName: 'Status',
              flex: 1,
              minWidth: 150,
              renderCell: (params) => (
                <span>
                  {statusDisplayMap[params.value] || params.value}
                </span>
              ),
            },
            {
                field: 'narration',
                headerName: 'Narration',
                flex: 1,
                minWidth: 150,
              },
          ]}
          initialState={{
            pagination: {
              paginationModel: { pageSize: 10, page: 0 },
            },
            sorting: {
                sortModel: [{ field: 'status', sort: 'asc' }],
              },
          }}
          onRowSelectionModelChange={(rowID) => {
            setSelection(rowID);
          }}
          pageSizeOptions={[10, 20, 50]}
          getRowId={(row) => row.narration_id}
        />
      </div>
    </div>
  );
}

export default MyAnnotations;
