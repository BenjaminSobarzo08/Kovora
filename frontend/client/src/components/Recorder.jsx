// src/components/Recorder.jsx
import { useState, useRef } from 'react'
import '../styles/recorder.css'

const Recorder = () => {
    const [recording, setRecording] = useState(false)
    const [subtitle, setSubtitle] = useState('')
    const mediaRecorder = useRef(null)
    const audioChunks = useRef([])

    const startRecording = async () => {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
        mediaRecorder.current = new MediaRecorder(stream)

        audioChunks.current = []

        mediaRecorder.current.ondataavailable = (e) => {
            audioChunks.current.push(e.data)
        }

        mediaRecorder.current.onstop = async () => {
            const blob = new Blob(audioChunks.current, { type: 'audio/webm' })
            const file = new File([blob], 'recording.webm')

            const formData = new FormData()
            formData.append('file', file)

            try {
                const res = await fetch('http://localhost:8000/transcribe', {
                    method: 'POST',
                    body: formData,
                })

                const data = await res.json()
                if (data.text) setSubtitle(data.text)
                else setSubtitle('Error de transcripción.')
            } catch (err) {
                setSubtitle('Error al conectar con el servidor.')
                console.log(err.message)
            }
        }

        mediaRecorder.current.start()
        setRecording(true)

        // Detener automáticamente después de 5 segundos
        setTimeout(() => {
            mediaRecorder.current.stop()
            setRecording(false)
        }, 5000)
    }

    return (
        <div className="recorder-container">
            <button onClick={startRecording} disabled={recording}>
                {recording ? 'Grabando...' : '🎙️ Empezar grabación'}
            </button>

            {subtitle && (
                <div className="subtitle-box">
                    <p>{subtitle}</p>
                </div>
            )}
        </div>
    )
}

export default Recorder
