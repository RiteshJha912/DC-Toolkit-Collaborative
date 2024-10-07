import React, { useState } from 'react'
import './App.css'

function App() {
  const [phoneNumber, setPhoneNumber] = useState('')
  const [instagram, setInstagram] = useState('')
  const [twitter, setTwitter] = useState('')
  const [github, setGithub] = useState('')
  const [email, setEmail] = useState('')
  const [output, setOutput] = useState('')

  const formatOutput = (info) => {
    if (!info) return '<p>No information available.</p>'
    const formattedInfo = []

    const formatNestedObject = (obj) => {
      return Object.entries(obj)
        .map(([key, value]) => {
          if (typeof value === 'object' && value !== null) {
            return `<p><strong>${key}:</strong></p>${formatNestedObject(value)}`
          }
          return `<p><strong>${key}:</strong> ${
            value !== null ? value : 'N/A'
          }</p>`
        })
        .join('')
    }

    for (const [key, value] of Object.entries(info)) {
      if (typeof value === 'object' && value !== null) {
        formattedInfo.push(
          `<p><strong>${key}:</strong></p>${formatNestedObject(value)}`
        )
      } else {
        formattedInfo.push(
          `<p><strong>${key}:</strong> ${value !== null ? value : 'N/A'}</p>`
        )
      }
    }

    return formattedInfo.join('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const dataToSend = {
      phoneNumber: phoneNumber || null,
      instagram: instagram || null,
      twitter: twitter || null,
      github: github || null,
      email: email || null,
    }

    try {
      const response = await fetch('http://127.0.0.1:5000/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(dataToSend),
      })

      const data = await response.json()

      const inputInfo = `
                <div class="input-info">
                    <h4><strong>Provided Information:</strong></h4>
                    ${phoneNumber ? `<p>Phone Number: ${phoneNumber}</p>` : ''}
                    ${instagram ? `<p>Instagram: ${instagram}</p>` : ''}
                    ${twitter ? `<p>Twitter: ${twitter}</p>` : ''}
                    ${github ? `<p>GitHub: ${github}</p>` : ''}
                    ${email ? `<p>Email: ${email}</p>` : ''}
                    <br/><br/>
                </div>
            `

      setOutput(`
                ${inputInfo}
                <div class="info-section">
                    <h3><u>Relevant Information:</u></h3>
                    <div>${formatOutput(data.relevant_info)}</div>
                </div>
                <div class="info-section">
                    <h3><u>All Available Information:</u></h3>
                    <div>${formatOutput(data.other_info)}</div>
                </div>
                <div class="result-summary">
                    <p>Results gathered from <strong>${
                      data.tool_count || 'multiple'
                    }</strong> sources.</p>
                </div>
            `)

      setPhoneNumber('')
      setInstagram('')
      setTwitter('')
      setGithub('')
      setEmail('')
    } catch (error) {
      setOutput(
        '<p>There was an error fetching the data. Please try again.</p>'
      )
    }
  }

  const handleFieldChange = (setter) => (e) => {
    setter(e.target.value)
    setOutput('')
  }

  return (
    <div className='container'>
      <h2>OSINT ToolKit: Phone Number & Social Media</h2>
      <form onSubmit={handleSubmit}>
        <input
          type='text'
          placeholder='Enter Phone Number (e.g., +91 XXXXX-XXXXX)'
          value={phoneNumber}
          onChange={handleFieldChange(setPhoneNumber)}
          className='input-box'
        />
        <input
          type='text'
          placeholder='Enter Instagram Username'
          value={instagram}
          onChange={handleFieldChange(setInstagram)}
          className='input-box'
        />
        <input
          type='text'
          placeholder='Enter Twitter Username'
          value={twitter}
          onChange={handleFieldChange(setTwitter)}
          className='input-box'
        />
        <input
          type='text'
          placeholder='Enter GitHub Username'
          value={github}
          onChange={handleFieldChange(setGithub)}
          className='input-box'
        />
        <input
          type='text'
          placeholder='Enter Email Address'
          value={email}
          onChange={handleFieldChange(setEmail)}
          className='input-box'
        />
        <button type='submit' className='submit-btn'>
          Search it up!
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
