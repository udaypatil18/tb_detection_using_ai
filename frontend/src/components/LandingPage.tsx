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

const LandingPage: React.FC<LandingPageProps> = ({ 
  onStartPrediction
}) => {
  const technologies = [
    { name: 'Efficientnet', icon: Microscope, description: 'CNN Architecture' },
    { name: 'TensorFlow', icon: Brain, description: 'Deep Learning Framework' },
    { name: 'Llama', icon: BrainCircuit, description: 'Textual Explanations' },
    { name: 'React', icon: Zap, description: 'Frontend Framework' },
    { name: 'Flask', icon: Shield, description: 'Backend API' },
  ];

  const steps = [
    {
      icon: Upload,
      title: 'Upload Image',
      description: 'Upload your bone X-ray scan',
      color: 'from-purple-400 to-purple-500'
    },
    {
      icon: Loader,
      title: 'AI Analysis',
      description: 'Deep Learning model analyzes the image for tumor detection',
      color: 'from-purple-500 to-violet-600'
    },
    {
      icon: FileText,
      title: 'Generate Report',
      description: 'Comprehensive medical report with heatmap visualization',
      color: 'from-violet-600 to-purple-700'
    },
    {
      icon: CheckCircle,
      title: 'View Results',
      description: 'Get your detailed analysis results instantly',
      color: 'from-purple-700 to-violet-800'
    }
  ];

  return (
    <div className="relative overflow-hidden">
      <Header 
        onLogoClick={() => {}} // Already on landing page
      />

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 via-violet-50 to-purple-100 overflow-hidden">

        <div className="container mx-auto px-6 text-center relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="mb-8"
          >
            <div className="flex items-center justify-center mb-6">
              <motion.div
                className="relative"
              >
                <Microscope className="w-32 h-32 text-purple-600 drop-shadow-lg" />
              </motion.div>
            </div>
            
            <motion.h1
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.8 }}
              className="text-6xl md:text-7xl font-bold text-classic-text mb-6 leading-tight"
            >
              <span className="block text-gradient-purple">Bone Tumor Detection</span>
              <span className="block text-6xl">Bone Tumor Detection</span>
            </motion.h1>
            
            <motion.p
              className="text-xl md:text-2xl text-classic-text-light mb-8 max-w-3xl mx-auto leading-relaxed"
            >
              Bone tumor detection and analysis. 
              Get instant results with professional medical reports.
            </motion.p>
            
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6, duration: 0.8 }}
              className="flex flex-col sm:flex-row gap-4 justify-center items-center"
            >
              <motion.button
                onClick={onStartPrediction}
                whileHover={{ scale: 1.05, boxShadow: "0 20px 40px rgba(168, 85, 247, 0.4)" }}
                whileTap={{ scale: 0.95 }}
                className="bg-gradient-to-r from-purple-600 to-violet-600 text-white px-8 py-4  text-lg font-semibold shadow-purple-lg hover:shadow-purple transition-all duration-300 flex items-center space-x-2 animate-glow-purple"
              >
                <span>Start Analysis</span>
                <ArrowRight className="w-5 h-5" />
              </motion.button>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-24 bg-gradient-to-b from-purple-50 to-violet-100">
        <div className="container mx-auto px-6">
          <motion.div
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-5xl font-bold text-classic-text mb-6">
              How It Works
            </h2>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {steps.map((step, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.2, duration: 0.8 }}
                viewport={{ once: true }}
                whileHover={{ y: -10, scale: 1.02 }}
                className="relative group"
              >
                <div className="glass-effect  p-8 shadow-purple hover:shadow-purple-lg transition-all duration-300 border border-purple-200 group-hover:border-purple-300 hover-lift">
                  <div className={`w-16 h-16  bg-gradient-to-r ${step.color} flex items-center justify-center mb-6 mx-auto group-hover:scale-110 transition-transform duration-300`}>
                    <step.icon className="w-8 h-8 text-white" />
                  </div>
                  
                  <div className="text-center">
                    <h3 className="text-xl font-bold text-classic-text mb-3">
                      {step.title}
                    </h3>
                    <p className="text-classic-text-light leading-relaxed">
                      {step.description}
                    </p>
                  </div>

                  {index < steps.length - 1 && (
                    <div className="hidden lg:block absolute top-1/2 -right-4 transform -translate-y-1/2">
                      <ChevronRight className="w-8 h-8 text-purple-300" />
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Technology Stack Section */}
      <section className="py-24 bg-gradient-to-br from-violet-100 via-purple-50 to-purple-100">
        <div className="container mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-5xl font-bold text-classic-text mb-6">
              Powered by
            </h2>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-5 gap-4">
            {technologies.map((tech, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1, duration: 0.6 }}
                viewport={{ once: true }}
                whileHover={{ y: -5, scale: 1.05 }}
                className="bg-white  p-6 shadow-lg hover:shadow-xl transition-all duration-300 text-center group border border-purple-100 hover:border-classic-orange-200"
              >
                <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-violet-600  flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                  <tech.icon className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-lg font-bold text-classic-text mb-2">
                  {tech.name}
                </h3>
                <p className="text-classic-text-light text-sm">
                  {tech.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gradient-to-r from-purple-900 to-violet-900 py-12">
        <div className="container mx-auto px-6">
          <div className="text-center">
            <div className="flex items-center justify-center mb-6">
              <Microscope className="w-8 h-8 text-purple-400 mr-3" />
              <span className="text-2xl font-bold text-white">
                Bone Tumor Detection
              </span>
            </div>
            
            <p className="text-white/70 mb-4 flex items-center justify-center space-x-2">
              <span>Made with</span>
              <Heart className="w-4 h-4 text-purple-400" />
              <span>for fighting Bone Cancer</span>
            </p>
            
            <p className="text-white/50 text-sm">
             AI Bone Cancer Detection System
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
