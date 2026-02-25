import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import LandingPage from './components/LandingPage';
import PredictionApp from './components/PredictionApp';

type ViewState = 'landing' | 'prediction';

function App() {
  const [view, setView] = useState<ViewState>('landing');

  const renderView = () => {
    switch (view) {
      case 'prediction':
        return (
          <PredictionApp onBackToHome={() => setView('landing')} />
        );
      case 'landing':
      default:
        return (
          <LandingPage onStartPrediction={() => setView('prediction')} />
        );
    }
  };

  return (
    <div className="min-h-screen bg-classic-ivory font-classic">
      <AnimatePresence mode="wait">
        <motion.div
          key={view}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3 }}
        >
          {renderView()}
        </motion.div>
      </AnimatePresence>
    </div>
  );
}

export default App;
