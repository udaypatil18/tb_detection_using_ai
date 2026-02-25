import React, { useCallback, useState } from 'react';
import { motion } from 'framer-motion';
import { useDropzone } from 'react-dropzone';
import { Upload, Image, AlertCircle, CheckCircle } from 'lucide-react';
import axios from 'axios';
import { PredictionResult } from '../types';

interface UploadSectionProps {
  onImageUpload: (imageUrl: string) => void;
  onPredictionStart: () => void;
  uploadedImage: string | null;
}

const UploadSection: React.FC<UploadSectionProps & { onPredictionComplete?: (result: PredictionResult) => void; onPredictionError?: (message: string) => void; errorMessage?: string | null }> = ({
  onImageUpload,
  onPredictionStart,
  uploadedImage,
  onPredictionComplete,
  onPredictionError,
  errorMessage
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string>(errorMessage || '');
  const [xrayOk, setXrayOk] = useState<boolean>(false);

  // Use Vercel API endpoint in production, fallback to localhost for development
  const env = (import.meta as any).env;
  const API_BASE_URL = env?.VITE_API_BASE
    || (env?.MODE === 'production' ? 'https://your-vercel-domain.vercel.app/api' : 'http://127.0.0.1:5000');

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const selectedFile = acceptedFiles[0];
    if (selectedFile) {
      if (selectedFile.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB');
        return;
      }
      
      const imageUrl = URL.createObjectURL(selectedFile);
      setFile(selectedFile);
      onImageUpload(imageUrl);
    setError('');
    setXrayOk(false);
    }
  }, [onImageUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.bmp', '.tiff']
    },
    multiple: false
  });

  const handleAnalyze = async () => {
    if (!file) return;

    onPredictionStart();

    // Phase 1: X-ray gate
    const gateForm = new FormData();
    gateForm.append('image', file);

    try {
      console.log('[UploadSection] Calling /analyze_json...');
      const gateResp = await axios.post(`${API_BASE_URL}/analyze_json`, gateForm, {
        timeout: 60000,
      });

      if (gateResp.data && (gateResp.data as any).error) {
        const msg = (gateResp.data as any).error as string;
        setError(msg);
        setXrayOk(false);
        onPredictionError?.(msg);
        return;
      }

      const gateData = gateResp.data as PredictionResult;
      if (typeof (gateData as any).xray_confirmed === 'boolean' && !gateData.xray_confirmed) {
        const msg = 'Not an X-ray image!';
        setError(msg);
        setXrayOk(false);
        onPredictionError?.(msg);
        return;
      }

      // Gate passed
      setError('');
      setXrayOk(true);

      // Phase 2: Multitask prediction
      try {
        const predForm = new FormData();
        predForm.append('image', file);
        console.log('[UploadSection] X-ray confirmed. Calling /predict...');
        const predResp = await axios.post(`${API_BASE_URL}/predict`, predForm, {
          // Keep slightly above server-side limits (90s MT + 25s LLaMA guarded)
          timeout: 130000,
        });
        const predData = predResp.data as PredictionResult;
        console.log('[UploadSection] /predict response:', predData);
        onPredictionComplete?.(predData);
      } catch (predErr: any) {
        console.error('[UploadSection] Multitask prediction failed:', predErr);
        let msg = 'Prediction failed. Showing X-ray-only result.';
        if (predErr?.response?.data?.error) {
          msg = `Multitask failed: ${predErr.response.data.error as string}`;
        } else if (predErr?.message && typeof predErr.message === 'string') {
          msg = `Multitask failed: ${predErr.message}`;
        }
        const fallback: PredictionResult = {
          ...gateData,
          warning: msg,
        } as PredictionResult;
        onPredictionComplete?.(fallback);
      }
    } catch (error: any) {
      console.error('[UploadSection] Analysis failed:', error);
      let msg = 'Analysis failed. Please try again.';
      if (error?.response?.data?.error) {
        msg = error.response.data.error as string;
      } else if (error?.message && typeof error.message === 'string') {
        msg = error.message;
      }
      setError(msg);
      setXrayOk(false);
      onPredictionError?.(msg);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8 }}
      className="bg-white  shadow-2xl p-8 border border-purple-200"
    >
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-classic-text mb-2">
          Upload Chest X-ray Image
        </h2>
        <p className="text-classic-text-light">
          Upload a chest X-ray image for AI-powered Tuberculosis detection
        </p>
      </div>

      <motion.div
        whileHover={{ scale: 1.02 }}
        className="mb-8"
      >
        <div
          {...getRootProps()}
          className={`border-2 border-dashed  p-12 text-center cursor-pointer transition-all duration-300 ${
            isDragActive
              ? 'border-purple-600 bg-purple-50'
              : 'border-purple-200 hover:border-purple-600 hover:bg-purple-50/30'
          }`}
        >
          <input {...getInputProps()} />
          <Upload className="w-16 h-16 text-purple-600 mx-auto mb-4" />
          <p className="text-lg font-medium text-classic-text mb-2">
            {isDragActive ? 'Drop the image here...' : 'Drag & drop your image here'}
          </p>
          <p className="text-classic-text-light">
            or <span className="text-purple-600 font-medium">browse files</span>
          </p>
          <p className="text-sm text-classic-text-light mt-2">
            Supports: JPEG, PNG
          </p>
        </div>
      </motion.div>

      {error && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6 p-4 bg-red-50 border border-red-200  flex items-center space-x-2"
        >
          <AlertCircle className="w-5 h-5 text-red-500" />
          <span className="text-red-700">{error}</span>
        </motion.div>
      )}

      {!error && xrayOk && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6 p-3 bg-green-50 border border-green-200  text-green-700 font-medium"
        >
          X-ray confirmed ✅
        </motion.div>
      )}

      {uploadedImage && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <div className="bg-purple-50  p-6">
            <div className="flex items-center space-x-2 mb-4">
              <CheckCircle className="w-5 h-5 text-purple-600" />
              <span className="text-classic-text font-medium">Image uploaded successfully</span>
            </div>
            
            <div className="flex justify-center mb-4">
              <div className="relative">
                <img
                  src={uploadedImage}
                  alt="Uploaded medical scan"
                  className="max-w-md max-h-64 object-contain  shadow-lg"
                />
                <div className="absolute top-2 left-2 bg-white bg-opacity-90 px-2 py-1 ">
                  <Image className="w-4 h-4 inline mr-1" />
                  <span className="text-xs font-medium">Medical Scan</span>
                </div>
              </div>
            </div>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleAnalyze}
              className="w-full bg-purple-600 hover:bg-purple-700 text-white font-medium py-3 px-6  transition-colors duration-300 shadow-lg"
            >
              Start AI Analysis
            </motion.button>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
};

export default UploadSection;
