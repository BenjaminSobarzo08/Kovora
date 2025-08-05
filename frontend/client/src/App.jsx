
import Recorder from './components/Recorder'

function App() {
    return (
        <div style={{ padding: '2rem', fontFamily: 'Arial, sans-serif' }}>
            <h1>Kovora 🎧</h1>
            <p>Haz clic para grabar y recibir subtítulos en tiempo real</p>
            <Recorder />
        </div>
    )
}

export default App


