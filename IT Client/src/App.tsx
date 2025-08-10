import React from 'react';
import { MantineProvider } from '@mantine/core';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import CodeCalculator from './components/CodeCalculator';

const App: React.FC = () => {
  return (
    <MantineProvider>
      <Router>
        <Routes>
          <Route path="/" element={<CodeCalculator />} />
        </Routes>
      </Router>
    </MantineProvider>
  );
};

export default App;
