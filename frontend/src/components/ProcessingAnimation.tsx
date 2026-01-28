import React from 'react';
import { motion } from 'framer-motion';
import { Brain, Zap, Search, Activity } from 'lucide-react';

const ProcessingAnimation: React.FC = () => {
  const processingSteps = [
    { icon: Search, text: 'Analyzing image...', delay: 0 },
    { icon: Brain, text: 'AI model processing...', delay: 0.5 },
    { icon: Zap, text: 'Generating heatmap...', delay: 1.0 },
    { icon: Activity, text: 'Preparing results...', delay: 1.5 },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8 }}
      className="bg-white  shadow-2xl p-12 text-center border border-purple-200"
    >
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
        className="w-20 h-20 mx-auto mb-8"
      >
        <div className="w-full h-full border-4 border-purple-600 border-t-transparent "></div>
      </motion.div>

      <h2 className="text-2xl font-bold text-classic-text mb-8">
        AI Analysis in Progress
      </h2>

      <div className="space-y-6">
        {processingSteps.map((step, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: step.delay, duration: 0.5 }}
            className="flex items-center justify-center space-x-3"
          >
            <motion.div
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 1.5, repeat: Infinity, delay: step.delay }}
            >
              <step.icon className="w-6 h-6 text-purple-600" />
            </motion.div>
            <span className="text-classic-text-light font-medium">{step.text}</span>
          </motion.div>
        ))}
      </div>

      <motion.p
        animate={{ opacity: [0.5, 1, 0.5] }}
        transition={{ duration: 2, repeat: Infinity }}
        className="mt-8 text-classic-text-light"
      >
        This process typically takes 10-30 seconds
      </motion.p>
    </motion.div>
  );
};

export default ProcessingAnimation;
