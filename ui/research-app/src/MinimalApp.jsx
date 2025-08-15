import React from 'react'

// Test 1: Can we render anything?
const MinimalApp = () => {
  console.log('MinimalApp rendering...')
  
  return (
    <div style={{ padding: '20px' }}>
      <h1>Minimal App Test</h1>
      <p>If you see this, basic React is working</p>
    </div>
  )
}

export default MinimalApp