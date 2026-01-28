import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft } from 'lucide-react';
import Header from './Header';
import UploadSection from './UploadSection';
import ProcessingAnimation from './ProcessingAnimation';
import ResultsSection from './ResultsSection';
import Footer from './Footer';
import { PredictionResult } from '../types';

interface PredictionAppProps {
  onBackToHome: () => void;
}

const PredictionApp: React.FC<PredictionAppProps> = ({ onBackToHome }) => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState<PredictionResult | null>(null);
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleImageUpload = (imageUrl: string) => {
    setUploadedImage(imageUrl);
    setResults(null);
    setErrorMsg(null);
  };

  const handlePredictionStart = () => {
    setIsProcessing(true);
    setErrorMsg(null);
  };

  const handlePredictionComplete = (result: PredictionResult) => {
    setIsProcessing(false);
    setResults(result);
    setErrorMsg(null);
  };

  const handlePredictionError = (message: string) => {
    setIsProcessing(false);
    setResults(null);
    setErrorMsg(message);
  };

  const handleNewAnalysis = () => {
    setResults(null);
    setUploadedImage(null);
    setIsProcessing(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-violet-50 to-purple-100 font-classic">
      {/* Back to Home Button */}
      <div className="fixed top-6 left-6 z-50">
        <motion.button
          onClick={onBackToHome}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="glass-effect text-purple-700 px-4 py-2  shadow-purple hover:shadow-purple-lg transition-all duration-300 flex items-center space-x-2 border border-purple-300 hover:border-purple-400"
        >
          <ArrowLeft className="w-4 h-4" />
          <span className="font-medium">Back to Home</span>
        </motion.button>
      </div>

      <Header onLogoClick={onBackToHome} />
      
      <main className="container mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8 }}
          className="max-w-6xl mx-auto"
        >
          {!results && !isProcessing && (
            <UploadSection
              onImageUpload={handleImageUpload}
              onPredictionStart={handlePredictionStart}
              uploadedImage={uploadedImage}
              onPredictionComplete={handlePredictionComplete}
              onPredictionError={handlePredictionError}
              errorMessage={errorMsg}
            />
          )}

          {isProcessing && (
            <ProcessingAnimation />
          )}

          {results && (
            <ResultsSection
              results={results}
              originalImage={uploadedImage}
              onNewAnalysis={handleNewAnalysis}
            />
          )}
        </motion.div>
      </main>

      <Footer />
    </div>
  );
};

export default PredictionApp;
