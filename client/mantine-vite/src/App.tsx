import React from 'react';
import { MantineProvider } from '@mantine/core';
import { BrowserRouter as Router, Route, Routes, useNavigate } from 'react-router-dom';
import CodeCalculator from './components/CodeCalculator';
import Home from './components/Home';

const App: React.FC = () => {
  return (
    <MantineProvider>
      <Router>
        <Routes>
          <Route path="/" element={<HomeWrapper />} />
          <Route path="/calculator" element={<CodeCalculator />} />
        </Routes>
      </Router>
    </MantineProvider>
  );
};

const HomeWrapper: React.FC = () => {
  const navigate = useNavigate();
  return <Home onNavigate={() => navigate('/calculator')} />;
};

export default App;
