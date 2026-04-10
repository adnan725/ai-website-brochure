import Input from './components/Input'
import './App.css'
import { BrowserRouter, Routes, Route } from "react-router";
import Chatbot from './components/Chatbot';
import MeetingMinutes from './components/MeetingMinutes';

function App() {

  return (
    <>
      <Routes>
        <Route path="/" element={<Input />} />
        <Route path="/chatbot" element={<Chatbot />} />
        <Route path="/meeting-minutes" element={<MeetingMinutes />} />
      </Routes>
    </>
  )
}

export default App
