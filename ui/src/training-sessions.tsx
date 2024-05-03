import React, { useEffect, useState } from 'react'
import 'react-toastify/dist/ReactToastify.css'
import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import AddIcon from '@mui/icons-material/Add'
import EditIcon from '@mui/icons-material/Edit'
import DeleteIcon from '@mui/icons-material/DeleteOutlined'
import SaveIcon from '@mui/icons-material/Save'
import CancelIcon from '@mui/icons-material/Close'
import {
  DataGrid,
  GridActionsCellItem,
  GridColDef,
  GridEditInputCell,
  GridEventListener,
  GridRowEditStopReasons,
  GridRowId,
  GridRowModel,
  GridRowModes,
  GridRowModesModel,
  GridRowsProp,
  GridSlots,
  GridToolbarContainer,
} from '@mui/x-data-grid'
import { TrainingSession, TrainingSessionDisciplineEnum } from './generated'
import { api } from './api'
import { toast } from 'react-toastify'

interface EditToolbarProps {
  setRows: (newRows: (oldRows: GridRowsProp) => GridRowsProp) => void
  setRowModes: (newModel: (oldModel: GridRowModesModel) => GridRowModesModel) => void
}

function GridToolBar(props: EditToolbarProps) {
  const { setRows, setRowModes } = props

  const onAdd = () => {
    const id = 'new'
    setRows((oldRows) => {
      const result = [
        ...oldRows,
        {
          id,
          version: undefined,
          title: '',
          discipline: TrainingSessionDisciplineEnum.Running,
          distance: undefined,
          date: new Date().toISOString().substring(0, 10),
        },
      ]
      return result
    })
    setRowModes((oldModel) => {
      const result = {
        ...oldModel,
        [id]: { mode: GridRowModes.Edit, fieldToFocus: 'title' },
      }
      return result
    })
  }

  return (
    <GridToolbarContainer>
      <Button color="primary" startIcon={<AddIcon />} onClick={onAdd}>
        Add Training Session
      </Button>
    </GridToolbarContainer>
  )
}

export function TrainingSessions() {
  const [trainingSessions, setTrainingSessions] = useState<Array<TrainingSession>>([])
  const [rowModes, setRowModes] = React.useState<GridRowModesModel>({})

  const fetchTrainingSessions = async () => {
    const response = await api.trainingTrackerApiGetTrainingSessions()
    setTrainingSessions(response.data)
  }

  useEffect(() => {
    fetchTrainingSessions().catch(console.error)
  }, [])

  const handleRowEditStop: GridEventListener<'rowEditStop'> = (params, event) => {
    if (params.reason === GridRowEditStopReasons.rowFocusOut) {
      event.defaultMuiPrevented = true
    }
  }

  const handleEditClick = (id: GridRowId) => () => {
    setRowModes({ ...rowModes, [id]: { mode: GridRowModes.Edit } })
  }

  const handleSaveClick = (id: GridRowId) => () => {
    setRowModes({ ...rowModes, [id]: { mode: GridRowModes.View } })
  }

  const handleDeleteClick = (id: GridRowId) => async () => {
    await api.trainingTrackerApiDeleteTrainingSession(id as string)
    await fetchTrainingSessions()
  }

  const handleCancelClick = (id: GridRowId) => () => {
    setRowModes({
      ...rowModes,
      [id]: { mode: GridRowModes.View, ignoreModifications: true },
    })

    const editedRow = trainingSessions.find((row) => row.id === id)
    if (editedRow!.id === 'new') {
      setTrainingSessions(trainingSessions.filter((row) => row.id !== id))
    }
  }

  const processRowUpdate = async (row: GridRowModel) => {
    let response
    if (row.id === 'new') {
      response = await api.trainingTrackerApiCreateTrainingSession(row as TrainingSession)
    } else {
      response = await api.trainingTrackerApiSaveTrainingSession(row.id, row as TrainingSession)
    }
    await fetchTrainingSessions()
    return response.data
  }

  const handleProcessRowUpdateError = (error: any) => {
    console.error('Error saving row:', error)
    switch (error.response?.status) {
      case 400:
        toast.error(`Invalid training session: ${error.response?.data?.detail ?? ''}`)
        break
      case 409:
        toast.error('The training session was already modified by someone else. Please refresh the page.')
        break
      default:
        toast.error(error.toString())
    }
  }

  const handleRowModesModelChange = (newRowModesModel: GridRowModesModel) => {
    setRowModes(newRowModesModel)
  }

  const columns: GridColDef[] = [
    { field: 'title', headerName: 'Title', width: 180, editable: true },
    {
      field: 'discipline',
      headerName: 'Discipline',
      width: 220,
      editable: true,
      type: 'singleSelect',
      valueOptions: Object.values(TrainingSessionDisciplineEnum),
    },
    {
      field: 'distance',
      headerName: 'Distance',
      type: 'number',
      width: 120,
      align: 'right',
      headerAlign: 'right',
      editable: true,
      renderEditCell: (params) => (
        <GridEditInputCell
          {...params}
          inputProps={{
            min: 1,
            step: 1,
          }}
        />
      ),
    },
    {
      field: 'date',
      headerName: 'Date',
      type: 'date',
      valueGetter: (value) => (isNaN(new Date(value).getDate()) ? undefined : new Date(value)),
      valueSetter: (value, row) => ({
        ...row,
        date: isNaN(value) ? undefined : value?.toISOString()?.substring(0, 10),
      }),
      width: 180,
      editable: true,
    },
    {
      field: 'actions',
      type: 'actions',
      headerName: 'Actions',
      width: 100,
      cellClassName: 'actions',
      getActions: ({ id }) => {
        const isInEditMode = rowModes[id]?.mode === GridRowModes.Edit

        if (isInEditMode) {
          return [
            <GridActionsCellItem
              icon={<SaveIcon />}
              label="Save"
              sx={{
                color: 'primary.main',
              }}
              onClick={handleSaveClick(id)}
            />,
            <GridActionsCellItem
              icon={<CancelIcon />}
              label="Cancel"
              className="textPrimary"
              onClick={handleCancelClick(id)}
              color="inherit"
            />,
          ]
        }

        return [
          <GridActionsCellItem
            icon={<EditIcon />}
            label="Edit"
            className="textPrimary"
            onClick={handleEditClick(id)}
            color="inherit"
          />,
          <GridActionsCellItem icon={<DeleteIcon />} label="Delete" onClick={handleDeleteClick(id)} color="inherit" />,
        ]
      },
    },
  ]

  return (
    <Box
      sx={{
        height: 500,
        width: '100%',
        '& .actions': {
          color: 'text.secondary',
        },
        '& .textPrimary': {
          color: 'text.primary',
        },
      }}
    >
      <DataGrid
        rows={trainingSessions}
        columns={columns}
        editMode="row"
        rowModesModel={rowModes}
        onRowModesModelChange={handleRowModesModelChange}
        onRowEditStop={handleRowEditStop}
        processRowUpdate={processRowUpdate}
        onProcessRowUpdateError={handleProcessRowUpdateError}
        slots={{
          toolbar: GridToolBar as GridSlots['toolbar'],
        }}
        slotProps={{
          toolbar: { setRows: setTrainingSessions, setRowModes },
        }}
      />
    </Box>
  )
}
