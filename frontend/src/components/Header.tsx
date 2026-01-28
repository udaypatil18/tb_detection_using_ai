import React from 'react';
import { motion } from 'framer-motion';
import { Microscope } from 'lucide-react';

interface HeaderProps {
  onLogoClick?: () => void;
}

const Header: React.FC<HeaderProps> = ({ onLogoClick }) => {
  return (
    <motion.header
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.8, ease: 'easeOut' }}
      className="glass-effect shadow-purple border-b-4 border-purple-500 relative z-50"
    >
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-center">
          {/* Centered Logo */}
          <motion.div
            whileHover={{ scale: 1.05 }}
            onClick={onLogoClick}
            className="flex items-center space-x-3 cursor-pointer"
          >
            <div className="relative">
              <Microscope className="w-10 h-10 text-purple-600" />
            </div>
            <div className="text-center">
              <h1 className="text-2xl font-bold text-classic-text leading-none">
                Bone Tumor Detection
              </h1>
              <p className="text-classic-text-light text-xs font-medium">
                AI-Powered Detection
              </p>
            </div>
          </motion.div>
        </div>
      </div>
    </motion.header>
  );
};

export default Header;
