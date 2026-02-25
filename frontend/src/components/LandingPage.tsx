import React from 'react';
import { motion } from 'framer-motion';
import Header from './Header';
import {
  Shield,
  Brain,
  Zap,
  BrainCircuit,
  ChevronRight,
  Upload,
  FileText,
  CheckCircle,
  ArrowRight,
  Microscope,
  Heart,
  Loader
} from 'lucide-react';

interface LandingPageProps {
  onStartPrediction: () => void;
}

const LandingPage: React.FC<LandingPageProps> = ({ onStartPrediction }) => {
  const technologies = [
    { name: 'EfficientNet', icon: Microscope, description: 'CNN Architecture' },
    { name: 'TensorFlow', icon: Brain, description: 'Deep Learning Framework' },
    { name: 'LLaMA', icon: BrainCircuit, description: 'Medical Report Generation' },
    { name: 'React', icon: Zap, description: 'Frontend Framework' },
    { name: 'Flask', icon: Shield, description: 'Backend API' },
  ];

  const steps = [
    {
      icon: Upload,
      title: 'Upload Image',
      description: 'Upload your chest X-ray image',
      color: 'from-purple-400 to-purple-500'
    },
    {
      icon: Loader,
      title: 'AI Analysis',
      description: 'Deep learning model analyzes the X-ray for TB indicators',
      color: 'from-purple-500 to-violet-600'
    },
    {
      icon: FileText,
      title: 'Generate Report',
      description: 'Comprehensive TB medical report with heatmaps',
      color: 'from-violet-600 to-purple-700'
    },
    {
      icon: CheckCircle,
      title: 'View Results',
      description: 'Instant Tuberculosis screening results',
      color: 'from-purple-700 to-violet-800'
    }
  ];

  return (
    <div className="relative overflow-hidden">
      <Header onLogoClick={() => {}} />

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 via-violet-50 to-purple-100">
        <div className="container mx-auto px-6 text-center">
          <Microscope className="w-32 h-32 text-purple-600 mx-auto mb-6" />

          <h1 className="text-6xl md:text-7xl font-bold mb-6">
            <span className="block text-gradient-purple">
              Tuberculosis Detection
            </span>
            <span className="block text-5xl">
              Chest X-ray Based Screening
            </span>
          </h1>

          <p className="text-xl text-classic-text-light mb-8 max-w-3xl mx-auto">
            AI-powered Tuberculosis detection using chest X-ray images.
            Get fast, reliable, and clinically structured reports.
          </p>

          <motion.button
            onClick={onStartPrediction}
            whileHover={{ scale: 1.05 }}
            className="bg-gradient-to-r from-purple-600 to-violet-600 text-white px-8 py-4 text-lg font-semibold flex items-center gap-2 mx-auto"
          >
            Start Analysis <ArrowRight />
          </motion.button>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-24 bg-gradient-to-b from-purple-50 to-violet-100">
        <div className="container mx-auto px-6">
          <h2 className="text-5xl font-bold text-center mb-16">
            How It Works
          </h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {steps.map((step, index) => (
              <div key={index} className="glass-effect p-8 text-center">
                <step.icon className="w-10 h-10 text-purple-600 mx-auto mb-4" />
                <h3 className="text-xl font-bold mb-3">{step.title}</h3>
                <p className="text-classic-text-light">{step.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gradient-to-r from-purple-900 to-violet-900 py-12">
        <div className="text-center text-white">
          <p className="flex items-center justify-center gap-2">
            Made with <Heart className="w-4 h-4" /> for Tuberculosis screening
          </p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
