import React, { useState } from 'react'
import './App.css' // We will add some CSS styles here

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

      // Function to format the output into a readable format
      const formatOutput = (info) => {
        return Object.entries(info)
          .map(([key, value]) => `<strong>${key}:</strong> ${value}`)
          .join('<br />')
      }

      setOutput(
        `<div class="info-section">
        <h3><u>Relevant Information:</u></h3>
        <div>${formatOutput(data.relevant_info)}</div>
      </div>
      <div class="info-section">
        <h3><br/><br/><u>All Information:</u></h3>
        <div>${formatOutput(data.other_info)}</div>
      </div>
      <div class="result-summary">
        <p>Results from across ${data.tool_count} different sources.</p>
      </div>`
      )
    } catch (error) {
      console.error('Error:', error)
    }
  }


  return (
    <div className='container'>
      <h2>Enter a Phone Number </h2>
      <form onSubmit={handleSubmit}>
        <input
          type='text'
          placeholder='Enter phone number'
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className='input-box'
        />
        <button type='submit' className='submit-btn'>
          Submit
        </button>
      </form>
      {output && (
        <div
          className='output-box'
          dangerouslySetInnerHTML={{ __html: output }}
        />
      )}
    </div>
  )
}

export default App
