// client/mantine-vite/src/components/Home.tsx
import React from 'react';
import { Button, Title } from '@mantine/core'; // Import Mantine components
import logo from '/logo.svg'; // Correct path to the logo

const Home: React.FC<{ onNavigate: () => void }> = ({ onNavigate }) => {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center', // Center items horizontally
        justifyContent: 'center', // Center items vertically
        gap: '1rem',
        padding: '0', // Remove padding to take full space
        height: '100vh', // Full height to take entire screen
        width: '100vw', // Full width to take entire screen
        backgroundColor: '#f9f9f9', // Optional: background color
        border: 'none', // Remove border
        borderRadius: '0', // Remove border radius
        position: 'absolute', // Position absolute to cover the screen
        top: 0, // Align to the top
        left: 0, // Align to the left
      }}
    >
      <img src={logo} alt="Logo" height="200" width="200" />
      <Title style={{ textAlign: 'center', fontSize: '1.5rem', fontWeight: 'bold' }}>
        Welcome to the Optipy
      </Title>
      <Button onClick={onNavigate}>
        Go to Code Calculator
      </Button>
    </div>
  );
};

export default Home;