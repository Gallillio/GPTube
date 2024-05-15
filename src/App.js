// App.js

import React, { useState } from 'react';
import './App.css';

// Left section component
const LeftSection = ({ isOpen }) => {
    return (
      <div className={`left-section ${isOpen ? 'open' : ''}`}>
        {isOpen && ( // Conditionally render content only when isOpen is true
          <nav>
            <ul>
              <li>Menu Item 1</li>
              <li>Menu Item 2</li>
              <li>Menu Item 3</li>
              {/* Add more menu items as needed */}
            </ul>
          </nav>
        )}
      </div>
    );
  };
  
// Middle section component
const MiddleSection = () => {
  return (
    <div className="middle-section">
      <h2>Middle Section</h2>
      {/* Add middle section content here */}
    </div>
  );
};

// Right section component
const RightSection = () => {
  return (
    <div className="right-section">
      <h2>Right Section</h2>
      {/* Add right section content here */}
    </div>
  );
};

// Parent component to manage left section visibility
const App = () => {
  const [isLeftOpen, setIsLeftOpen] = useState(false);

  const toggleLeft = () => {
    setIsLeftOpen(!isLeftOpen);
  };

  return (
    <div className="app">
      <div className="burger-menu" onClick={toggleLeft}>
        &#9776;
      </div>
      <LeftSection isOpen={isLeftOpen} />
      <MiddleSection />
      <RightSection />
    </div>
  );
};

export default App;
