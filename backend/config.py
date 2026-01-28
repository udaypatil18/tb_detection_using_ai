"""
Configuration file for Bone Cancer Detection API
Centralizes all configuration parameters for easy management
"""
import os
from typing import List, Dict, Any

class Config:
    """Main configuration class"""
    
    # =================
    # Server Configuration
    # =================
    DEBUG = os.environ.get('FLASK_DEBUG', '0') == '1'
    HOST = os.environ.get('FLASK_HOST', '127.0.0.1')
    PORT = int(os.environ.get('FLASK_PORT', 5000))
    
    # =================
    # Model Configuration
    # =================
    # Model file paths (checks multiple extensions automatically)
    MULTITASK_MODEL_PATHS = [
        "models/multitask_model.keras",
        "models/multitask_model.h5",
        "models/bone_tumor_model.keras",
        "models/bone_tumor_model.h5"
    ]
    
    # Model input specifications
    MODEL_INPUT_HEIGHT = 384
    MODEL_INPUT_WIDTH = 384
    MODEL_INPUT_CHANNELS = 3
    MODEL_NORMALIZATION_RANGE = (-1, 1)  # Normalization range for input images

    # =================
    # LLaMA Report Generator Configuration
    # =================
    # Preferred local directory for base weights to avoid network download
    LLAMA_BASE_DIR = os.environ.get('LLAMA_BASE_DIR')  # e.g., backend/models/llama-3.2-1b-instruct
    # Fallback HF model id (requires network + HF auth when used)
    LLAMA_BASE_MODEL_ID = os.environ.get('LLAMA_BASE_MODEL_ID', 'meta-llama/Llama-3.2-1B-Instruct')
    # Adapter subfolder name under backend/models
    LLAMA_ADAPTER_DIRNAME = os.environ.get('LLAMA_ADAPTER_DIRNAME', 'llama3_bone_lora_adapter')
    
    # =================
    # Prediction Configuration
    # =================
    # Classification labels
    MULTICLASS_LABELS = ["benign", "malignant", "normal"]
    PATHOLOGY_LABELS = [
        "fracture", "lesion", "mass", "osteolysis", 
        "sclerosis", "soft_tissue", "joint_space", "alignment"
    ]
    
    # Prediction thresholds
    PATHOLOGY_THRESHOLD = 0.3  # Minimum confidence for pathology detection
    MAX_PATHOLOGIES_DISPLAY = 5  # Maximum pathologies to show in results
    
    # =================
    # Image Processing Configuration
    # =================
    # Supported image formats
    SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    MAX_IMAGE_SIZE_MB = 10  # Maximum upload size in MB
    
    # Segmentation overlay settings
    SEGMENTATION_THRESHOLD = 0.5
    SEGMENTATION_OVERLAY_ALPHA = 0.6
    SEGMENTATION_COLOR_BGR = (0, 0, 255)  # Red overlay
    
    # Grad-CAM settings
    GRADCAM_OVERLAY_ALPHA = 0.35
    GRADCAM_COLORMAP = 'COLORMAP_JET'
    
    # =================
    # Storage Configuration
    # =================
    STATIC_DIRS = ['static/heatmaps', 'static/uploads']
    TEMP_FILE_PREFIX = "temp_analysis_"
    TEMP_FILE_CLEANUP_HOURS = 24  # Hours after which temp files are cleaned
    
    # =================
    # Performance Configuration
    # =================
    PERFORMANCE_HISTORY_SIZE = 100  # Number of timing records to keep
    ENABLE_PERFORMANCE_LOGGING = True
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # =================
    # Security Configuration
    # =================
    MAX_CONTENT_LENGTH = MAX_IMAGE_SIZE_MB * 1024 * 1024  # In bytes
    ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',') if os.environ.get('ALLOWED_HOSTS') else []
    
    # =================
    # API Configuration
    # =================
    API_RATE_LIMIT = {
        'per_minute': int(os.environ.get('API_RATE_LIMIT_PER_MINUTE', 60)),
        'per_hour': int(os.environ.get('API_RATE_LIMIT_PER_HOUR', 1000))
    }
    
    # Response timeouts
    PREDICTION_TIMEOUT_SECONDS = 30
    MODEL_LOADING_TIMEOUT_SECONDS = 60
    
    @classmethod
    def get_model_config(cls) -> Dict[str, Any]:
        """Get model-specific configuration"""
        return {
            'input_shape': (cls.MODEL_INPUT_HEIGHT, cls.MODEL_INPUT_WIDTH, cls.MODEL_INPUT_CHANNELS),
            'normalization_range': cls.MODEL_NORMALIZATION_RANGE,
            'multiclass_labels': cls.MULTICLASS_LABELS,
            'pathology_labels': cls.PATHOLOGY_LABELS,
            'pathology_threshold': cls.PATHOLOGY_THRESHOLD
        }
    
    @classmethod
    def get_processing_config(cls) -> Dict[str, Any]:
        """Get image processing configuration"""
        return {
            'supported_formats': cls.SUPPORTED_IMAGE_FORMATS,
            'max_size_mb': cls.MAX_IMAGE_SIZE_MB,
            'segmentation_threshold': cls.SEGMENTATION_THRESHOLD,
            'segmentation_overlay_alpha': cls.SEGMENTATION_OVERLAY_ALPHA,
            'gradcam_overlay_alpha': cls.GRADCAM_OVERLAY_ALPHA
        }
    
    @classmethod
    def validate_config(cls) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Check required directories
        for directory in cls.STATIC_DIRS:
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory, exist_ok=True)
                except Exception as e:
                    issues.append(f"Cannot create directory {directory}: {e}")
        
        # Validate model paths
        model_found = False
        for path in cls.MULTITASK_MODEL_PATHS:
            if os.path.exists(path):
                model_found = True
                break
        if not model_found:
            issues.append(f"No model file found in paths: {cls.MULTITASK_MODEL_PATHS}")
        
        # Validate numeric values
        if cls.MODEL_INPUT_HEIGHT <= 0 or cls.MODEL_INPUT_WIDTH <= 0:
            issues.append("Model input dimensions must be positive")
        
        if cls.PATHOLOGY_THRESHOLD < 0 or cls.PATHOLOGY_THRESHOLD > 1:
            issues.append("Pathology threshold must be between 0 and 1")
        
        return issues

class DevelopmentConfig(Config):
    """Development-specific configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    ENABLE_PERFORMANCE_LOGGING = True

class ProductionConfig(Config):
    """Production-specific configuration"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    ENABLE_PERFORMANCE_LOGGING = False
    
    # Tighter security for production
    API_RATE_LIMIT = {
        'per_minute': 30,
        'per_hour': 500
    }
    MAX_IMAGE_SIZE_MB = 5  # Smaller max size for production

class TestingConfig(Config):
    """Testing-specific configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    PERFORMANCE_HISTORY_SIZE = 10  # Smaller for testing
    PREDICTION_TIMEOUT_SECONDS = 10  # Faster timeout for tests

# Configuration factory
def get_config() -> Config:
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development').lower()
    
    if env == 'production':
        return ProductionConfig()
    elif env == 'testing':
        return TestingConfig()
    else:
        return DevelopmentConfig()

# Export the active configuration
config = get_config()