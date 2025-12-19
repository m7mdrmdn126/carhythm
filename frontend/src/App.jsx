import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Welcome from './pages/Welcome';
import ModuleIntro from './pages/ModuleIntro';
import Question from './pages/Question';
import ModuleCompletion from './pages/ModuleCompletion';
import FeedbackPage from './pages/FeedbackPage';
import Complete from './pages/Complete';
import Results from './pages/Results';
import './styles/global.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Welcome />} />
        <Route path="/module/:pageId" element={<ModuleIntro />} />
        <Route path="/question/:pageId" element={<Question />} />
        <Route path="/module-complete" element={<ModuleCompletion />} />
        <Route path="/feedback" element={<FeedbackPage />} />
        <Route path="/email" element={<Complete />} />
        <Route path="/complete" element={<Complete />} />
        <Route path="/results/:sessionId" element={<Results />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
