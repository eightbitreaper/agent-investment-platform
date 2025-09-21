#!/usr/bin/env python3
"""
Hugging Face Model Download and Management Script for Agent Investment Platform

This script handles automated downloading and management of LLM models from Hugging Face Hub.
Leverages free model downloads and automatic repository syncing for latest model definitions.
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
import time
from dataclasses import dataclass

# Setup logging
logger = logging.getLogger(__name__)

@dataclass 
class HuggingFaceModel:
    """Information about a Hugging Face model"""
    repo_id: str
    name: str
    size_gb: float
    description: str
    use_case: List[str]
    model_type: str
    required_ram_gb: float = 8.0

class HuggingFaceModelManager:
    """Handles Hugging Face model downloading and management"""
    
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.project_root = config_dir.parent
        self.models_dir = self.project_root / "models"
        self.hf_cache_dir = self.models_dir / ".huggingface_cache"
        
        # Ensure directories exist
        self.models_dir.mkdir(exist_ok=True)
        self.hf_cache_dir.mkdir(exist_ok=True)
        
        # Set Hugging Face cache directory
        os.environ["HF_HOME"] = str(self.hf_cache_dir)
        os.environ["TRANSFORMERS_CACHE"] = str(self.hf_cache_dir)
        
        self.available_models = self._define_models()

    def _define_models(self) -> Dict[str, HuggingFaceModel]:
        """Define available Hugging Face models for financial analysis"""
        return {
            "microsoft/Phi-3-mini-4k-instruct": HuggingFaceModel(
                repo_id="microsoft/Phi-3-mini-4k-instruct",
                name="Phi-3 Mini",
                size_gb=2.4,
                description="Small, efficient model for general financial analysis",
                use_case=["general", "classification", "summarization"],
                model_type="text-generation",
                required_ram_gb=4.0
            ),
            
            "ProsusAI/finbert": HuggingFaceModel(
                repo_id="ProsusAI/finbert",
                name="FinBERT",
                size_gb=0.4,
                description="BERT model fine-tuned for financial sentiment analysis",
                use_case=["sentiment", "classification", "news_analysis"],
                model_type="text-classification",
                required_ram_gb=2.0
            ),
            
            "sentence-transformers/all-MiniLM-L6-v2": HuggingFaceModel(
                repo_id="sentence-transformers/all-MiniLM-L6-v2",
                name="All-MiniLM-L6-v2",
                size_gb=0.1,
                description="Sentence embeddings for semantic similarity",
                use_case=["embeddings", "similarity", "clustering"],
                model_type="sentence-transformers",
                required_ram_gb=1.0
            )
        }

    def install_dependencies(self) -> bool:
        """Install required Hugging Face libraries"""
        try:
            logger.info("Installing Hugging Face dependencies...")
            packages = [
                "huggingface_hub>=0.24.0",
                "transformers>=4.40.0",
                "torch>=2.0.0",
                "sentence-transformers>=2.7.0"
            ]
            
            subprocess.run([
                sys.executable, "-m", "pip", "install"
            ] + packages, check=True, capture_output=True, text=True)
            
            logger.info("✓ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install dependencies: {e}")
            return False

    def download_model(self, model_key: str) -> bool:
        """Download a specific model from Hugging Face"""
        if model_key not in self.available_models:
            logger.error(f"Unknown model: {model_key}")
            return False
            
        model = self.available_models[model_key]
        logger.info(f"Downloading {model.name} ({model.size_gb} GB)...")
        
        try:
            from huggingface_hub import snapshot_download
            
            # Create model-specific directory
            model_dir = self.models_dir / model_key.replace("/", "_")
            model_dir.mkdir(exist_ok=True)
            
            # Download model repository
            logger.info(f"Downloading repository: {model.repo_id}")
            local_path = snapshot_download(
                repo_id=model.repo_id,
                cache_dir=str(self.hf_cache_dir),
                local_dir=str(model_dir),
                local_dir_use_symlinks=True,
                resume_download=True
            )
            
            # Store model metadata
            model_info = {
                "repo_id": model.repo_id,
                "name": model.name,
                "local_path": str(model_dir),
                "size_gb": model.size_gb,
                "use_case": model.use_case,
                "model_type": model.model_type,
                "downloaded_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Save model metadata
            metadata_file = model_dir / "model_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(model_info, f, indent=2)
                
            logger.info(f"✓ Successfully downloaded {model.name}")
            return True
            
        except ImportError:
            logger.error("Missing dependencies. Install with: pip install huggingface_hub transformers")
            return False
        except Exception as e:
            logger.error(f"Failed to download {model.name}: {e}")
            return False

    def setup_models(self, models_to_download: Optional[List[str]] = None) -> bool:
        """Set up Hugging Face models for the platform"""
        logger.info("Setting up Hugging Face models...")
        
        if not self.install_dependencies():
            return False
            
        # Default models if none specified
        if models_to_download is None:
            models_to_download = [
                "microsoft/Phi-3-mini-4k-instruct",
                "ProsusAI/finbert",
                "sentence-transformers/all-MiniLM-L6-v2"
            ]
        
        success = True
        for model_key in models_to_download:
            if model_key in self.available_models:
                if not self.download_model(model_key):
                    success = False
            else:
                logger.warning(f"Unknown model: {model_key}")
                
        return success

    def list_downloaded_models(self) -> Dict[str, Any]:
        """List all downloaded models and their metadata"""
        downloaded = {}
        
        for model_dir in self.models_dir.iterdir():
            if model_dir.is_dir() and not model_dir.name.startswith('.'):
                metadata_file = model_dir / "model_metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                        downloaded[model_dir.name] = metadata
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid metadata file: {metadata_file}")
                        
        return downloaded

    def create_model_config(self) -> bool:
        """Create configuration files for downloaded models"""
        try:
            downloaded = self.list_downloaded_models()
            
            # Create Hugging Face model configuration
            hf_config = {
                "huggingface_models": {
                    "cache_dir": str(self.hf_cache_dir),
                    "models_dir": str(self.models_dir),
                    "available_models": {}
                }
            }
            
            for model_name, metadata in downloaded.items():
                hf_config["huggingface_models"]["available_models"][model_name] = {
                    "repo_id": metadata["repo_id"],
                    "local_path": metadata["local_path"],
                    "use_case": metadata["use_case"],
                    "model_type": metadata["model_type"],
                    "size_gb": metadata["size_gb"]
                }
            
            # Save configuration
            config_file = self.config_dir / "huggingface-models.json"
            with open(config_file, 'w') as f:
                json.dump(hf_config, f, indent=2)
                
            logger.info(f"✓ Model configuration saved to: {config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create model config: {e}")
            return False

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Hugging Face Model Manager")
    parser.add_argument("--models", nargs="+", help="Specific models to download")
    parser.add_argument("--list", action="store_true", help="List downloaded models")
    parser.add_argument("--config-dir", type=Path, default=Path("config"), 
                       help="Configuration directory")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Initialize model manager
    manager = HuggingFaceModelManager(args.config_dir)
    
    try:
        if args.list:
            downloaded = manager.list_downloaded_models()
            if downloaded:
                print("\n📚 Downloaded Models:")
                for name, info in downloaded.items():
                    print(f"  • {info['name']} ({info['size_gb']} GB)")
                    print(f"    Repository: {info['repo_id']}")
                    print(f"    Use cases: {', '.join(info['use_case'])}")
                    print()
            else:
                print("No models downloaded yet.")
        else:
            # Download models
            models = args.models or list(manager.available_models.keys())
            
            print(f"🚀 Setting up Hugging Face models...")
            print(f"Models to download: {', '.join(models)}")
            
            success = manager.setup_models(models)
            if success:
                manager.create_model_config()
                print("\n✅ Model setup completed successfully!")
                print("Models are ready for use with free Hugging Face Hub integration.")
            else:
                print("\n❌ Model setup failed!")
                sys.exit(1)
                
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()