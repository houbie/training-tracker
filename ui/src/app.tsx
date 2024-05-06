import React from 'react'
import { AppBar, Toolbar } from '@mui/material'
import { ToastContainer } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css'
import { TrainingSessions } from './training-sessions'

function App() {
  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <h1>Training Tracker</h1>
        </Toolbar>
      </AppBar>
      <TrainingSessions />
      <ToastContainer />
    </>
  )
}

export default App
