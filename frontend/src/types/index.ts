export interface PredictionItem {
  class: string;
  confidence: number;
  tumor_type?: string;
  pathologies?: string[];
}

export interface PredictionResult {
  // Core response fields
  xray_confirmed: boolean;
  message: string;
  
  // Multitask model outputs
  multiclass?: string;
  pathology?: string[];
  pathology_scores?: { name: string; prob: number }[];
  tumor_subtype?: string;
  tumor_subtype_confidence?: number;
  segmentation_mask?: string; // Base64 image
  segmentation_overlay?: string; // Base64 image
  gradcam_overlay?: string; // Base64 image
  uploaded_filename?: string; // Name of the uploaded file
  
  // Legacy compatibility
  predictions?: PredictionItem[];
  heatmap_url?: string;
  warning?: string;
  error?: string;

  // Legacy fields kept for compatibility with old UI
  prediction?: string;
  confidence?: number;
  explanation?: string;
  heatmap_data?: string; // Base64 encoded heatmap for Vercel
  model_used?: string;

  // LLaMA report integration
  llama_report?: string;
  llama_checks?: { key_findings?: boolean; patient_expl?: boolean; treatment_plan?: boolean };
}