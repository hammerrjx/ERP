import { createRoot } from 'react-dom/client'
import App from './app/App'
import './styles.css'

globalThis.__ERP_REACT_ROOT__ ||= createRoot(document.getElementById('root'))
globalThis.__ERP_REACT_ROOT__.render(<App />)
