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
import requests
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging
import time
from dataclasses import dataclass
import platform

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
    model_type: str  # "text-generation", "text-classification", etc.
    required_ram_gb: float = 8.0
    quantized: bool = False
    local_path: Optional[str] = None
    config_file: str = "config.json"
    tokenizer_file: str = "tokenizer.json"

class ModelDownloadError(Exception):
    """Custom exception for model download failures"""
    pass

class HuggingFaceModelManager:
    """Handles Hugging Face model downloading and management"""
    
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.project_root = config_dir.parent
        self.models_dir = self.project_root / "models"
        self.hf_cache_dir = self.models_dir / ".huggingface_cache"
        self.available_models = self._define_huggingface_models()
        
        # Ensure directories exist
        self.models_dir.mkdir(exist_ok=True)
        self.hf_cache_dir.mkdir(exist_ok=True)
        self.lmstudio_available = self._check_lmstudio_available()
        
        # Create models directory
        self.models_dir.mkdir(exist_ok=True)
        
        # Define available models for different use cases
        self.available_models = self._define_available_models()
    
    def _define_available_models(self) -> Dict[str, ModelInfo]:
        """Define available models for different use cases"""
        return {
            "llama3.1": ModelInfo(
                name="llama3.1",
                size_gb=4.7,
                description="Meta's Llama 3.1 8B - Excellent general purpose model",
                use_case="general_analysis_and_reporting",
                ollama_name="llama3.1",
                huggingface_id="meta-llama/Meta-Llama-3.1-8B-Instruct",
                required_ram_gb=8.0,
                quantization="Q4_K_M"
            ),
            "llama3.1:70b": ModelInfo(
                name="llama3.1:70b", 
                size_gb=40.0,
                description="Meta's Llama 3.1 70B - High-quality analysis and reasoning",
                use_case="complex_analysis_and_detailed_reporting",
                ollama_name="llama3.1:70b",
                huggingface_id="meta-llama/Meta-Llama-3.1-70B-Instruct",
                required_ram_gb=48.0,
                quantization="Q4_K_M"
            ),
            "codellama": ModelInfo(
                name="codellama",
                size_gb=3.8,
                description="Meta's Code Llama - Specialized for code generation",
                use_case="mcp_agent_development_and_script_generation", 
                ollama_name="codellama",
                huggingface_id="codellama/CodeLlama-7b-Instruct-hf",
                required_ram_gb=6.0,
                quantization="Q4_K_M"
            ),
            "mistral": ModelInfo(
                name="mistral",
                size_gb=4.1,
                description="Mistral 7B - Fast and efficient for analysis",
                use_case="quick_sentiment_analysis_and_data_processing",
                ollama_name="mistral",
                huggingface_id="mistralai/Mistral-7B-Instruct-v0.3",
                required_ram_gb=6.0,
                quantization="Q4_K_M"
            ),
            "phi3": ModelInfo(
                name="phi3",
                size_gb=2.3,
                description="Microsoft Phi-3 - Lightweight but capable",
                use_case="resource_constrained_environments",
                ollama_name="phi3",
                huggingface_id="microsoft/Phi-3-mini-4k-instruct",
                required_ram_gb=4.0,
                quantization="Q4_K_M"
            ),
            "gemma2": ModelInfo(
                name="gemma2",
                size_gb=5.4,
                description="Google Gemma 2 9B - Strong reasoning capabilities",
                use_case="financial_analysis_and_strategic_insights",
                ollama_name="gemma2",
                huggingface_id="google/gemma-2-9b-it",
                required_ram_gb=10.0,
                quantization="Q4_K_M"
            )
        }
    
    def setup_models(self):
        """Setup local LLM models based on user choice and system capabilities"""
        logger.info(f"Setting up LLM models for choice: {self.llm_choice}")
        
        try:
            if self.llm_choice in ["local", "hybrid"]:
                self._setup_local_models()
            
            if self.llm_choice in ["api", "hybrid"]:
                self._setup_api_models()
            
            # Create model configuration
            self._create_model_config()
            
            logger.info("LLM model setup completed successfully")
            
        except Exception as e:
            logger.error(f"Model setup failed: {e}")
            raise ModelDownloadError(f"Failed to setup models: {e}")
    
    def _setup_local_models(self):
        """Setup local LLM models"""
        logger.info("Setting up local LLM models...")
        
        # Check system resources
        system_ram = self._get_available_ram()
        logger.info(f"Available system RAM: {system_ram:.1f} GB")
        
        # Install Ollama if needed and available
        if not self.ollama_available:
            if self._install_ollama():
                self.ollama_available = True
        
        if self.ollama_available:
            self._setup_ollama_models(system_ram)
        elif self.lmstudio_available:
            self._setup_lmstudio_models(system_ram)
        else:
            logger.warning("No local LLM runtime available. Please install Ollama or LMStudio manually.")
            self._create_manual_setup_instructions()
    
    def _setup_api_models(self):
        """Setup API-based LLM configuration"""
        logger.info("Setting up API-based LLM configuration...")
        
        # API models don't require downloading, just configuration
        # This will be handled in the model config creation
        pass
    
    def _install_ollama(self) -> bool:
        """Install Ollama if possible"""
        logger.info("Attempting to install Ollama...")
        
        system = platform.system().lower()
        
        try:
            if system == "windows":
                return self._install_ollama_windows()
            elif system == "linux":
                return self._install_ollama_linux()
            elif system == "darwin":  # macOS
                return self._install_ollama_macos()
            else:
                logger.warning(f"Unsupported system for automatic Ollama installation: {system}")
                return False
        
        except Exception as e:
            logger.warning(f"Failed to install Ollama: {e}")
            return False
    
    def _install_ollama_windows(self) -> bool:
        """Install Ollama on Windows"""
        try:
            # Download Ollama installer
            installer_url = "https://ollama.com/download/windows"
            installer_path = self.project_root / "ollama-installer.exe"
            
            logger.info("Downloading Ollama installer...")
            response = requests.get(installer_url, stream=True)
            response.raise_for_status()
            
            with open(installer_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info("Running Ollama installer...")
            # Note: This requires user interaction
            subprocess.run([str(installer_path)], check=True)
            
            # Cleanup
            installer_path.unlink()
            
            # Wait for installation to complete and service to start
            time.sleep(30)
            
            return self._check_ollama_available()
            
        except Exception as e:
            logger.error(f"Windows Ollama installation failed: {e}")
            return False
    
    def _install_ollama_linux(self) -> bool:
        """Install Ollama on Linux"""
        try:
            logger.info("Installing Ollama on Linux...")
            
            # Use the official install script
            install_cmd = ["curl", "-fsSL", "https://ollama.com/install.sh", "|", "sh"]
            
            # Run with shell=True for pipe operations
            result = subprocess.run(
                "curl -fsSL https://ollama.com/install.sh | sh",
                shell=True,
                check=True,
                capture_output=True,
                text=True
            )
            
            logger.info("Ollama installation completed")
            
            # Start Ollama service
            try:
                subprocess.run(["systemctl", "start", "ollama"], check=True)
                subprocess.run(["systemctl", "enable", "ollama"], check=True)
            except subprocess.CalledProcessError:
                # Try starting manually
                subprocess.Popen(["ollama", "serve"])
                time.sleep(5)
            
            return self._check_ollama_available()
            
        except Exception as e:
            logger.error(f"Linux Ollama installation failed: {e}")
            return False
    
    def _install_ollama_macos(self) -> bool:
        """Install Ollama on macOS"""
        try:
            logger.info("Installing Ollama on macOS...")
            
            # Check if Homebrew is available
            if self._check_command_exists("brew"):
                subprocess.run(["brew", "install", "ollama"], check=True)
            else:
                # Use the official install script
                result = subprocess.run(
                    "curl -fsSL https://ollama.com/install.sh | sh",
                    shell=True,
                    check=True,
                    capture_output=True,
                    text=True
                )
            
            # Start Ollama service
            subprocess.Popen(["ollama", "serve"])
            time.sleep(5)
            
            return self._check_ollama_available()
            
        except Exception as e:
            logger.error(f"macOS Ollama installation failed: {e}")
            return False
    
    def _setup_ollama_models(self, system_ram: float):
        """Setup models with Ollama"""
        logger.info("Setting up Ollama models...")
        
        # Recommend models based on available RAM
        recommended_models = self._recommend_models_for_ram(system_ram)
        
        logger.info(f"Recommended models for {system_ram:.1f}GB RAM: {recommended_models}")
        
        # Download recommended models
        for model_name in recommended_models:
            model_info = self.available_models[model_name]
            self._download_ollama_model(model_info)
    
    def _setup_lmstudio_models(self, system_ram: float):
        """Setup models with LMStudio"""
        logger.info("LMStudio detected. Creating model recommendations...")
        
        # LMStudio requires manual model downloads
        # We'll create instructions for the user
        recommended_models = self._recommend_models_for_ram(system_ram)
        
        instructions = self._create_lmstudio_instructions(recommended_models)
        instructions_file = self.config_dir / "lmstudio-setup-instructions.md"
        
        with open(instructions_file, 'w') as f:
            f.write(instructions)
        
        logger.info(f"LMStudio setup instructions created: {instructions_file}")
    
    def _download_ollama_model(self, model_info: ModelInfo):
        """Download a model with Ollama"""
        logger.info(f"Downloading model: {model_info.name} ({model_info.size_gb}GB)")
        
        try:
            # Check if model is already available
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                check=True
            )
            
            if model_info.ollama_name in result.stdout:
                logger.info(f"Model {model_info.name} already available")
                return
            
            # Download the model
            logger.info(f"Pulling model {model_info.ollama_name}...")
            
            process = subprocess.Popen(
                ["ollama", "pull", model_info.ollama_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Monitor download progress
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    # Simple progress logging
                    if "pulling" in output.lower() or "downloading" in output.lower():
                        logger.info(output.strip())
            
            return_code = process.poll()
            if return_code == 0:
                logger.info(f"Successfully downloaded {model_info.name}")
            else:
                stderr = process.stderr.read()
                raise ModelDownloadError(f"Failed to download {model_info.name}: {stderr}")
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to download model {model_info.name}: {e}")
            raise ModelDownloadError(f"Ollama model download failed: {e}")
    
    def _recommend_models_for_ram(self, available_ram: float) -> List[str]:
        """Recommend models based on available system RAM"""
        recommendations = []
        
        # Always recommend the lightweight model
        recommendations.append("phi3")
        
        if available_ram >= 8:
            recommendations.append("llama3.1")  # General purpose
            recommendations.append("mistral")   # Fast analysis
        
        if available_ram >= 12:
            recommendations.append("codellama") # Code generation
            recommendations.append("gemma2")   # Financial analysis
        
        if available_ram >= 48:
            recommendations.append("llama3.1:70b")  # High-quality analysis
        
        return recommendations[:3]  # Limit to 3 models to avoid storage issues
    
    def _create_model_config(self):
        """Create comprehensive model configuration"""
        logger.info("Creating model configuration...")
        
        config = {
            "local_models": {},
            "model_assignments": {
                "sentiment_analysis": "mistral",
                "technical_analysis": "gemma2", 
                "report_generation": "llama3.1",
                "code_generation": "codellama",
                "general_analysis": "llama3.1",
                "complex_reasoning": "llama3.1:70b" if self._model_available("llama3.1:70b") else "llama3.1"
            },
            "performance_settings": {
                "context_length": 4096,
                "temperature": 0.7,
                "top_p": 0.9,
                "repeat_penalty": 1.1,
                "num_predict": 2048
            },
            "resource_management": {
                "concurrent_requests": 1,
                "memory_allocation": "auto",
                "cpu_threads": -1  # Use all available
            }
        }
        
        # Add available local models
        if self.ollama_available:
            config["local_models"] = self._get_available_ollama_models()
        
        # Add API model configuration if needed
        if self.llm_choice in ["api", "hybrid"]:
            config["api_models"] = {
                "openai": {
                    "gpt-4o": "general_analysis_and_reporting",
                    "gpt-4o-mini": "quick_analysis_and_classification"
                },
                "anthropic": {
                    "claude-3-5-sonnet-20241022": "complex_reasoning_and_analysis",
                    "claude-3-haiku-20240307": "fast_processing_and_classification"
                }
            }
        
        config_file = self.config_dir / "local-models.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Model configuration saved: {config_file}")
    
    def _get_available_ollama_models(self) -> Dict[str, Any]:
        """Get list of available Ollama models"""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                check=True
            )
            
            models = {}
            for line in result.stdout.split('\n')[1:]:  # Skip header
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 3:
                        model_name = parts[0]
                        model_id = parts[1] 
                        size = parts[2]
                        
                        models[model_name] = {
                            "id": model_id,
                            "size": size,
                            "available": True,
                            "runtime": "ollama"
                        }
            
            return models
            
        except subprocess.CalledProcessError:
            return {}
    
    def _model_available(self, model_name: str) -> bool:
        """Check if a specific model is available"""
        if not self.ollama_available:
            return False
        
        available_models = self._get_available_ollama_models()
        return any(model_name in name for name in available_models.keys())
    
    def _get_available_ram(self) -> float:
        """Get available system RAM in GB"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return memory.total / (1024 ** 3)  # Convert to GB
        except ImportError:
            # Fallback estimation
            system = platform.system().lower()
            if system == "windows":
                try:
                    result = subprocess.run(
                        ["wmic", "computersystem", "get", "TotalPhysicalMemory"],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    for line in result.stdout.split('\n'):
                        if line.strip() and line.strip() != 'TotalPhysicalMemory':
                            return int(line.strip()) / (1024 ** 3)
                except:
                    pass
            
            # Conservative fallback
            return 8.0  # Assume 8GB
    
    def _check_ollama_available(self) -> bool:
        """Check if Ollama is available"""
        return self._check_command_exists("ollama")
    
    def _check_lmstudio_available(self) -> bool:
        """Check if LMStudio is available"""
        # LMStudio doesn't have a command line interface by default
        # Check for common installation paths
        system = platform.system().lower()
        
        if system == "windows":
            lmstudio_paths = [
                Path.home() / "AppData" / "Local" / "LMStudio",
                Path("C:") / "Program Files" / "LMStudio"
            ]
        elif system == "darwin":  # macOS
            lmstudio_paths = [
                Path("/Applications") / "LMStudio.app"
            ]
        else:  # Linux
            lmstudio_paths = [
                Path.home() / "LMStudio",
                Path("/opt") / "LMStudio"
            ]
        
        return any(path.exists() for path in lmstudio_paths)
    
    def _check_command_exists(self, command: str) -> bool:
        """Check if a command exists in the system PATH"""
        return shutil.which(command) is not None
    
    def _create_manual_setup_instructions(self):
        """Create manual setup instructions when automatic setup fails"""
        instructions = f"""
# Manual Local LLM Setup Instructions

## Ollama Installation (Recommended)

### Windows
1. Download Ollama from: https://ollama.com/download/windows
2. Run the installer and follow the setup wizard
3. Open Command Prompt or PowerShell
4. Run: `ollama pull llama3.1`
5. Run: `ollama pull mistral`

### macOS  
1. Install via Homebrew: `brew install ollama`
2. Or download from: https://ollama.com/download/macos
3. Run: `ollama pull llama3.1`
4. Run: `ollama pull mistral`

### Linux
1. Run: `curl -fsSL https://ollama.com/install.sh | sh`
2. Run: `ollama pull llama3.1`
3. Run: `ollama pull mistral`

## LMStudio Alternative

1. Download LMStudio from: https://lmstudio.ai/
2. Install and launch the application
3. Browse and download these recommended models:
   - Meta-Llama-3.1-8B-Instruct (Q4_K_M)
   - Mistral-7B-Instruct-v0.3 (Q4_K_M)
   - CodeLlama-7b-Instruct (Q4_K_M)

## Verification

After installation, run the setup again:
```bash
python scripts/setup/download-models.py --verify
```

## Configuration

The system will automatically detect your local LLM setup and configure accordingly.
"""
        
        instructions_file = self.config_dir / "manual-llm-setup.md"
        with open(instructions_file, 'w') as f:
            f.write(instructions)
        
        logger.info(f"Manual setup instructions created: {instructions_file}")
    
    def _create_lmstudio_instructions(self, recommended_models: List[str]) -> str:
        """Create LMStudio-specific setup instructions"""
        model_details = [self.available_models[name] for name in recommended_models]
        
        instructions = f"""
# LMStudio Model Setup Instructions

LMStudio has been detected on your system. Please follow these steps to download the recommended models:

## Recommended Models for Your System

"""
        
        for model in model_details:
            instructions += f"""
### {model.name}
- **Size**: {model.size_gb}GB
- **Use Case**: {model.use_case.replace('_', ' ').title()}
- **Description**: {model.description}
- **HuggingFace ID**: `{model.huggingface_id}`
- **Recommended Quantization**: {model.quantization}

"""
        
        instructions += """
## Download Steps

1. Open LMStudio
2. Go to the "Discover" tab
3. Search for each model by its HuggingFace ID
4. Download the Q4_K_M quantized version for optimal performance
5. Once downloaded, models will be available for the Agent Investment Platform

## Starting Local Server

1. In LMStudio, go to the "Local Server" tab  
2. Load your preferred model
3. Start the server (default: http://localhost:1234)
4. The Agent Investment Platform will automatically detect and use the server

## Configuration

The system will automatically configure itself to use your LMStudio models.
No additional configuration is required.
"""
        
        return instructions
    
    def interactive_setup(self):
        """Interactive model setup with user guidance"""
        print("\n🤖 Local LLM Model Setup")
        print("=" * 40)
        
        # System information
        ram_gb = self._get_available_ram()
        print(f"💾 Available RAM: {ram_gb:.1f}GB")
        
        # Runtime availability
        print(f"🔧 Ollama Available: {'✅' if self.ollama_available else '❌'}")
        print(f"🔧 LMStudio Available: {'✅' if self.lmstudio_available else '❌'}")
        
        if not self.ollama_available and not self.lmstudio_available:
            print("\n⚠️  No local LLM runtime detected.")
            install_choice = input("Would you like to install Ollama? (y/N): ").strip().lower()
            
            if install_choice == 'y':
                if self._install_ollama():
                    self.ollama_available = True
                    print("✅ Ollama installation completed")
                else:
                    print("❌ Ollama installation failed")
                    self._create_manual_setup_instructions()
                    return
            else:
                self._create_manual_setup_instructions()
                return
        
        # Model recommendations
        recommended = self._recommend_models_for_ram(ram_gb)
        print(f"\n📋 Recommended models for your system:")
        
        for i, model_name in enumerate(recommended, 1):
            model = self.available_models[model_name]
            print(f"  {i}. {model.name} - {model.description} ({model.size_gb}GB)")
        
        # Download confirmation
        download_choice = input(f"\nDownload recommended models? (Y/n): ").strip().lower()
        
        if download_choice != 'n':
            if self.ollama_available:
                for model_name in recommended:
                    self._download_ollama_model(self.available_models[model_name])
            
            self._create_model_config()
            print("✅ Model setup completed!")
        else:
            print("⏭️  Skipping model download. You can download manually later.")

def main():
    """Main entry point for standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Local LLM Model Manager")
    parser.add_argument("--interactive", action="store_true", help="Interactive setup")
    parser.add_argument("--verify", action="store_true", help="Verify setup")
    parser.add_argument("--llm-choice", default="local", choices=["local", "api", "hybrid"])
    
    args = parser.parse_args()
    
    # Setup paths
    project_root = Path(__file__).parent.parent.parent
    config_dir = project_root / "config"
    
    downloader = ModelDownloader(config_dir, args.llm_choice)
    
    try:
        if args.verify:
            # Verification mode
            print("🔍 Verifying LLM setup...")
            available_models = downloader._get_available_ollama_models()
            if available_models:
                print("✅ Local models available:")
                for name, info in available_models.items():
                    print(f"  - {name} ({info['size']})")
            else:
                print("❌ No local models found")
        
        elif args.interactive:
            downloader.interactive_setup()
        else:
            downloader.setup_models()
            print("✅ Model setup completed")
            
    except Exception as e:
        print(f"❌ Model setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()