import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'

const TestPage = () => (
  <div style={{ padding: '20px' }}>
    <h1>Router Test Working</h1>
    <p>React Router is functional</p>
  </div>
)

const TestWithRouter = () => {
  console.log('TestWithRouter rendering...')
  
  return (
    <Router>
      <Routes>
        <Route path="/" element={<TestPage />} />
      </Routes>
    </Router>
  )
}

export default TestWithRouter