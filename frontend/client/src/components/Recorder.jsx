import { useEffect, useRef, useState } from 'react'
import { io } from 'socket.io-client'
import '../styles/recorder.css'

const SOCKET_URL = 'http://localhost:8000'

const blobToBase64 = (blob) =>
    new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onloadend = () => {
            const result = reader.result
            if (typeof result !== 'string') {
                reject(new Error('No se pudo leer el audio'))
                return
            }

            const [, base64 = ''] = result.split(',')
            resolve(base64)
        }
        reader.onerror = () => reject(reader.error)
        reader.readAsDataURL(blob)
    })

const Recorder = () => {
    const [recording, setRecording] = useState(false)
    const [status, setStatus] = useState('')
    const mediaRecorder = useRef(null)
    const socketRef = useRef(null)
    const streamRef = useRef(null)
    const stopTimeoutRef = useRef(null)
    const lastSpokenTextRef = useRef('')

    const speakTranslation = (text) => {
        if (!text || typeof window === 'undefined' || !window.speechSynthesis) {
            setStatus('El navegador no soporta reproduccion de voz.')
            return
        }

        const normalizedText = text.trim()
        if (!normalizedText || normalizedText === lastSpokenTextRef.current) {
            return
        }

        window.speechSynthesis.cancel()

        const utterance = new SpeechSynthesisUtterance(normalizedText)
        utterance.lang = 'en-US'
        utterance.rate = 1
        utterance.pitch = 1
        utterance.onstart = () => setStatus('Reproduciendo traduccion...')
        utterance.onend = () => setStatus('Audio reproducido.')
        utterance.onerror = () => setStatus('No se pudo reproducir el audio traducido.')

        lastSpokenTextRef.current = normalizedText
        window.speechSynthesis.speak(utterance)
    }

    useEffect(() => {
        const socket = io(SOCKET_URL, {
            transports: ['websocket', 'polling'],
        })

        socket.on('connect', () => {
            setStatus('Conectado al servidor de transcripcion.')
        })

        socket.on('connect_error', () => {
            setStatus('No se pudo conectar con el servidor.')
        })

        socket.on('transcription_ready', () => {
            setStatus('Microfono activo. Habla cuando quieras.')
        })

        socket.on('transcription_result', (data) => {
            const translated = data?.translated?.trim()

            if (!translated) {
                return
            }

            setStatus(data?.isFinal ? 'Traduccion final recibida.' : 'Traduciendo...')

            if (data?.isFinal) {
                speakTranslation(translated)
            }
        })

        socketRef.current = socket

        return () => {
            if (window.speechSynthesis) {
                window.speechSynthesis.cancel()
            }
            socket.disconnect()
            socketRef.current = null
        }
    }, [])

    const stopRecording = () => {
        if (stopTimeoutRef.current) {
            clearTimeout(stopTimeoutRef.current)
            stopTimeoutRef.current = null
        }

        if (mediaRecorder.current && mediaRecorder.current.state !== 'inactive') {
            mediaRecorder.current.stop()
        }
    }

    const startRecording = async () => {
        try {
            lastSpokenTextRef.current = ''
            setStatus('Solicitando acceso al microfono...')

            const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
            streamRef.current = stream

            const recorder = new MediaRecorder(stream, { mimeType: 'audio/webm' })
            mediaRecorder.current = recorder

            socketRef.current?.emit('start_transcription', { suffix: '.webm' })

            recorder.ondataavailable = async (event) => {
                if (!event.data || event.data.size === 0) {
                    return
                }

                try {
                    const audio = await blobToBase64(event.data)
                    socketRef.current?.emit('audio_chunk', { audio, suffix: '.webm' })
                } catch (error) {
                    console.error(error)
                    setStatus('No se pudo enviar un fragmento de audio.')
                }
            }

            recorder.onstop = () => {
                socketRef.current?.emit('end_transcription')

                if (streamRef.current) {
                    streamRef.current.getTracks().forEach((track) => track.stop())
                    streamRef.current = null
                }

                mediaRecorder.current = null
                setRecording(false)
            }

            recorder.start(1000)
            setRecording(true)
            setStatus('Grabando y enviando audio...')

            stopTimeoutRef.current = setTimeout(() => {
                stopRecording()
            }, 5000)
        } catch (error) {
            console.error(error)
            setRecording(false)
            setStatus('No se pudo acceder al microfono.')
        }
    }

    return (
        <div className="recorder-container">
            <button onClick={recording ? stopRecording : startRecording}>
                {recording ? 'Detener grabacion' : 'Empezar grabacion'}
            </button>

            {status && <p>{status}</p>}
        </div>
    )
}

export default Recorder
