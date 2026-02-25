import React from 'react';
import { motion } from 'framer-motion';
import { Brain, Zap, Search, Activity } from 'lucide-react';

const ProcessingAnimation: React.FC = () => {
  const processingSteps = [
    { icon: Search, text: 'Analyzing chest X-ray...', delay: 0 },
    { icon: Brain, text: 'Deep learning model processing...', delay: 0.5 },
    { icon: Zap, text: 'Generating TB heatmap...', delay: 1.0 },
    { icon: Activity, text: 'Preparing TB results...', delay: 1.5 },
  ];

  return (
    <motion.div className="bg-white shadow-2xl p-12 text-center">
      <h2 className="text-2xl font-bold mb-8">
        AI Analysis in Progress
      </h2>

      {processingSteps.map((step, i) => (
        <p key={i} className="text-classic-text-light mb-2">
          {step.text}
        </p>
      ))}

      <p className="mt-6 text-classic-text-light">
        This usually takes 10–30 seconds
      </p>
    </motion.div>
  );
};

export default ProcessingAnimation;
