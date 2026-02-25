import React from 'react';
import { motion } from 'framer-motion';
import { Heart } from 'lucide-react';

const Footer: React.FC = () => {
  return (
    <motion.footer className="bg-white border-t border-purple-200 mt-16">
      <div className="container mx-auto px-4 py-8 text-center">
        <p className="text-classic-text-light flex justify-center gap-2">
          Made with <Heart className="w-4 h-4 text-purple-600" /> for early
          Tuberculosis detection
        </p>
      </div>
    </motion.footer>
  );
};

export default Footer;
