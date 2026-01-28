import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { RefreshCw, AlertTriangle, Info } from 'lucide-react';
import { PredictionResult } from '../types';
import axios from 'axios';

interface ResultsSectionProps {
  results: PredictionResult;
  originalImage: string | null;
  onNewAnalysis: () => void;
}

const ResultsSection: React.FC<ResultsSectionProps> = ({ 
  results, 
  originalImage, 
  onNewAnalysis 
}) => {
  const [reportText, setReportText] = useState<string | null>(null);
  const [reportChecks, setReportChecks] = useState<{ [k: string]: boolean } | null>(null);
  const [reportLoading, setReportLoading] = useState<boolean>(false);

  // Use same API base logic as UploadSection

  // Declare API base URL once for all handlers
  const env = (import.meta as any).env;
  const API_BASE_URL = env?.VITE_API_BASE
    || (env?.MODE === 'production' ? 'https://your-vercel-domain.vercel.app/api' : 'http://127.0.0.1:5000');

  const reportControllerRef = React.useRef<AbortController | null>(null);

  // Cleanup files on backend when starting new analysis
  const handleNewAnalysisWithCleanup = () => {
    // Abort any pending report generation
    if (reportControllerRef.current) {
      reportControllerRef.current.abort();
      reportControllerRef.current = null;
    }

    // Fire-and-forget cleanup (don't await)
    axios.post(`${API_BASE_URL}/cleanup_files`).catch(err => {
      console.error('Cleanup failed:', err);
    });
    
    onNewAnalysis();
  };


  // Use same API base logic as UploadSection
  // Use API_BASE_URL from top-level scope

  const hasStructured = Array.isArray(results.predictions) && results.predictions.length > 0;

  const handleDownloadReport = async (isAutoTriggered = false) => {
    try {
      // Cancel previous request if exists
      if (reportControllerRef.current) {
        reportControllerRef.current.abort();
      }
      const controller = new AbortController();
      reportControllerRef.current = controller;

      setReportLoading(true);
      const instruction = 'Generate a full report for an osteochondroma case or normal case';
      const inputStruct = {
        multiclass_label: results.multiclass || results.prediction,
        top_pathology_labels: (results.pathology_scores?.map(p => p.name) || results.pathology || []).slice(0, 5),
        predicted_tumor_type: results.tumor_subtype || '',
        confidence: typeof results.confidence === 'number' ? results.confidence : 0,
      };
      const payload: any = { instruction, input: inputStruct };
      console.log('Sending payload to /report:', payload);
      // Increase timeout to 2 minutes (120000 ms)
      const resp = await axios.post(`${API_BASE_URL}/report`, payload, { 
        timeout: 1200000,
        signal: controller.signal
      });
      console.log('Report API response:', resp.data);
      const data = resp.data;
      console.log('Parsing response data:', data);
      
      // Check if data is raw text
      if (typeof data === 'string') {
        setReportText(data);
        setReportChecks(null);
        return;
      }
      
      // Parse as JSON response
      if (data?.report) {
        // Clean any instruction/json artifacts from report
        let cleanReport = data.report;
        cleanReport = cleanReport.replace(/\{[^}]*\}/g, ''); // Remove JSON objects
        cleanReport = cleanReport.replace(/\[[^\]]*\]/g, ''); // Remove arrays
        cleanReport = cleanReport.replace(/(instruction:|input:).*/gi, ''); // Remove instruction lines
        cleanReport = cleanReport.trim();
        
        setReportText(cleanReport);
        setReportChecks(data.checks || null);
      } else if (data?.status === 'error' || data?.error) {
        console.error('Report error:', data.error || 'Unknown error');
        // Only throw error if manually triggered
        if (!isAutoTriggered) {
          throw new Error(data.error || 'Report generation failed');
        }
      } else {
        console.warn('Report API returned success but no report content:', data);
        // Only throw error if manually triggered
        if (!isAutoTriggered) {
          throw new Error('Report generated but no content returned');
        }
      }
      setReportLoading(false);
    } catch (error) {
      if (axios.isCancel(error)) {
        console.log('Report generation canceled');
        return;
      }
      console.error('Report download failed:', error);
      // Only alert if not canceled AND not auto-triggered
      if (!axios.isCancel(error) && !isAutoTriggered) {
        alert('Report generation failed. Please try again.');
      }
      setReportLoading(false);
    } finally {
      reportControllerRef.current = null;
    }
  };

  // Auto-trigger report generation once multitask results arrive, if not already generated
  useEffect(() => {
    const hasMT = !!(results.multiclass || results.prediction);
    if (hasMT && !reportText && !reportLoading) {
      // Start background generation, UI will show loader under results
      // Pass true to indicate this is auto-triggered (don't show alert on failure)
      handleDownloadReport(true);
    }
    
    // Cleanup on unmount or dependency change
    return () => {
      if (reportControllerRef.current) {
        reportControllerRef.current.abort();
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [results.multiclass, results.prediction, results.tumor_subtype]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8 }}
      className="space-y-8"
    >
      {/* Results Header */}
      <div className="bg-white  shadow-2xl p-8 border border-purple-200">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-classic-text mb-2">
            Analysis Results
          </h2>
          <p className="text-classic-text-light">
            AI-powered Bone Tumor Detection Completed
          </p>
        </div>
        {/* PDF Download Button and LLaMA status moved below */}

        {results.warning && (
          <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200  flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5 text-yellow-600" />
            <span className="text-yellow-800">{results.warning}</span>
          </div>
        )}

        {hasStructured ? (
          <div className="mb-6">
            <h3 className="text-xl font-semibold mb-3 text-classic-text">Detected Tumor Class:</h3>
            <ul className="space-y-2">
              {results.predictions!.map((p, idx) => (
                <li key={idx} className="flex justify-between bg-purple-50 border border-purple-200  px-3 py-2">
                  <span className="font-medium capitalize text-classic-text">{p.class}</span>
                  <span className="text-classic-text-light">{(p.confidence * 100).toFixed(1)}%</span>
                </li>
              ))}
            </ul>
            {results.xray_confirmed && (
              <p className="mt-3 text-sm text-green-700">X-ray confirmed ✅</p>
            )}
          </div>
        ) : (
          <div className="flex items-center justify-center space-x-4 mb-8">
            <Info className="w-8 h-8 text-medical-text" />
            <div>
              <h3 className="text-2xl font-bold mb-2">Classification</h3>
              {results.prediction && (
                <p className="text-classic-text">{results.prediction}</p>
              )}
              {typeof results.confidence === 'number' && (
                <p className="text-medical-text-light">Confidence: {(results.confidence * 100).toFixed(1)}%</p>
              )}
            </div>
          </div>
        )}

        {/* Keep a brief analysis note here (full report shown below the images) */}
        {!results.llama_report && (
          <div className="bg-purple-50  p-6 mb-8">
            <h4 className="font-semibold text-classic-text mb-3">Medical Analysis:</h4>
            <p className="text-classic-text-light leading-relaxed">
              {results.explanation || 'AI analysis completed successfully. Please consult with healthcare professionals for medical interpretation.'}
            </p>
          </div>
        )}

        <div className="flex justify-center">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleNewAnalysisWithCleanup}
            className="bg-purple-600 hover:bg-purple-700 text-white font-medium py-3 px-8  transition-colors duration-300 flex items-center space-x-2 shadow-lg"
          >
            <RefreshCw className="w-5 h-5" />
            <span>New Scan</span>
          </motion.button>
        </div>
      </div>


      {/* Image Comparison */}
      <div className="bg-white  shadow-2xl p-8 border border-purple-200">
        <h3 className="text-2xl font-bold text-classic-text mb-6 text-center">
          Comprehensive Analysis
        </h3>

        {/* Multitask Results */}
        {(results.multiclass || results.pathology || results.tumor_subtype) && (
          <div className="mb-8 grid md:grid-cols-3 gap-6">
            {results.multiclass && (
              <div className="bg-blue-50  p-4">
                <h4 className="font-semibold text-blue-900 mb-2">Tumor  Multiclass Classification</h4>
                <p className="text-red-600 capitalize text-2xl font-medium">{results.multiclass}</p>
              </div>
            )}
            
            {/* Tumor Subtype - only shown when available */}
            {results.tumor_subtype && (
              <div className="bg-purple-50  p-4">
                <h4 className="font-semibold text-purple-900 mb-2">Probable Tumor Type Identified</h4>
                <p className="text-purple-800 text-lg font-medium capitalize">
                  {results.tumor_subtype.replace('_', ' ')}
                </p>
              </div>
            )}
            
            {results.pathology && results.pathology.length > 0 && (
              <div className="bg-green-50  p-4">
                <h4 className="font-semibold text-green-900 mb-2">Probable Identified Locations</h4>
                {results.pathology_scores && results.pathology_scores.length > 0 ? (
                  <ul className="text-green-800 space-y-1">
                    {results.pathology_scores.map((p, idx) => (
                      <li key={idx} className="capitalize flex justify-between">
                        <span>• {p.name.replace('_', ' ')}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <ul className="text-green-800 space-y-1">
                    {results.pathology.map((path, idx) => (
                      <li key={idx} className="capitalize">• {path.replace('_', ' ')}</li>
                    ))}
                  </ul>
                )}
              </div>
            )}
          </div>
        )}
        
        <div className="grid lg:grid-cols-3 md:grid-cols-2 gap-6">
          {/* Original Image */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="space-y-4"
          >
            <h4 className="text-lg font-semibold text-classic-text text-center">
              Original X-ray
            </h4>
            {originalImage && (
              <div className="bg-purple-50  p-4">
                <img
                  src={originalImage}
                  alt="Original medical scan"
                  className="w-full h-64 object-contain  shadow-lg"
                />
              </div>
            )}
          </motion.div>

          {/* Segmentation Overlay */}
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.6 }}
            className="space-y-4"
          >
            <h4 className="text-lg font-semibold text-classic-text text-center">
              Tumor Segmentation
            </h4>
            <div className="bg-purple-50  p-4">
              {results.segmentation_overlay ? (
                <img
                  src={results.segmentation_overlay}
                  alt="Tumor segmentation overlay"
                  className="w-full h-64 object-contain  shadow-lg"
                />
              ) : (
                <div className="w-full h-64 bg-gray-200  flex items-center justify-center">
                  <p className="text-gray-500">Segmentation not available</p>
                </div>
              )}
            </div>
            <p className="text-sm text-classic-text-light text-center">
              Highlighted regions show detected tumor areas
            </p>
          </motion.div>

          {/* Grad-CAM Visualization */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4, duration: 0.6 }}
            className="space-y-4"
          >
            <h4 className="text-lg font-semibold text-classic-text text-center">
              Grad-CAM Highlights
            </h4>
            <div className="bg-purple-50  p-4">
              {results.gradcam_overlay ? (
                <img
                  src={results.gradcam_overlay}
                  alt="Grad-CAM attention heatmap"
                  className="w-full h-64 object-contain  shadow-lg"
                />
              ) : results.heatmap_data ? (
                <img
                  src={results.heatmap_data}
                  alt="Grad-CAM heatmap"
                  className="w-full h-64 object-contain  shadow-lg"
                />
              ) : results.heatmap_url ? (
                <img
                  src={`${API_BASE_URL}${results.heatmap_url}`}
                  alt="Grad-CAM heatmap"
                  className="w-full h-64 object-contain  shadow-lg"
                />
              ) : (
                <div className="w-full h-64 bg-gray-200  flex items-center justify-center">
                  <p className="text-gray-500">Heatmap not available</p>
                </div>
              )}
            </div>
            <p className="text-sm text-classic-text-light text-center">
              Areas AI focused on for decision making
            </p>
          </motion.div>
        </div>
      </div>
             {/* LLaMA Report Section — placed below the multitask/image sections */}
            {reportLoading && (
              <div className="bg-white  shadow-2xl p-8 border border-purple-200">
                <h3 className="text-2xl font-bold text-classic-text mb-3 text-center">AI-Generated Report</h3>
                <p className="text-center text-classic-text-light">Generating report… Please wait.</p>
                <div className="mt-4 flex justify-center">
                  <div className="animate-spin  h-10 w-10 border-t-2 border-b-2 border-purple-600"></div>
                </div>
              </div>
            )}
            {reportText && (
              <div className="bg-white  shadow-2xl p-8 border border-purple-200">
                <h3 className="text-2xl font-bold text-classic-text mb-6 text-center">
                  AI-Generated Report
                </h3>
                {reportChecks && (
                  <div className="flex flex-wrap gap-3 justify-center mb-4">
                    <span className={`px-3 py-1  text-sm ${reportChecks.key_findings ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-700'}`}>Key Findings</span>
                    <span className={`px-3 py-1  text-sm ${reportChecks.patient_expl ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-700'}`}>Patient-Friendly Explanation</span>
                    <span className={`px-3 py-1  text-sm ${reportChecks.treatment_plan ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-700'}`}>Treatment Plan</span>
                  </div>
                )}
                <div className="prose max-w-none text-classic-text leading-relaxed bg-purple-50 p-6  border border-purple-200">
                  {(() => {
                    // Extract only the response part after [/INST]
                    const cleanText = reportText?.split('[/INST]').pop()?.trim() || reportText || '';
                    return cleanText.split('\n').map((line, i) => {
                      if (!line.trim()) return null;
                      if (line.match(/^\d\./)) return <h3 key={i} className="mt-4 font-semibold">{line}</h3>;
                      return <p key={i}>{line}</p>;
                    });
                  })()}
                </div>
              </div>
            )}
    </motion.div>
  );
};

export default ResultsSection;
