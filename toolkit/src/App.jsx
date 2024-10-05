import React, { useState } from 'react'
import './App.css' 

function App() {
  const [input, setInput] = useState('')
  const [output, setOutput] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const response = await fetch('http://127.0.0.1:5000/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input }),
      })
      const data = await response.json()
      setOutput(data.output)
    } catch (error) {
      console.error('Error:', error)
    }
  }

  return (
    <div className='container'>
      <form onSubmit={handleSubmit}>
        <input
          type='text'
          placeholder='Enter your text'
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className='input-box'
        />
        <button type='submit' className='submit-btn'>
          Submit
        </button>
      </form>
      {output && (
        <div className='output-box'>
          <p>{output}</p>
        </div>
      )}
    </div>
  )
}

export default App
