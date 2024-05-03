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
          <h1>My Training Sessions</h1>
        </Toolbar>
      </AppBar>
      <TrainingSessions />
      <ToastContainer />
    </>
  )
}

export default App
