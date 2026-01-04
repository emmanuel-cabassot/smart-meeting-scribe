import torch

# 🚀 BOOST PERFORMANCE RTX 4000 (TF32)
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True

def get_device_config():
    if torch.cuda.is_available():
        return {
            "device": "cuda",
            "compute_type": "int8_float16",
            "name": torch.cuda.get_device_name(0)
        }
    else:
        return {
            "device": "cpu",
            "compute_type": "int8",
            "name": "CPU"
        }

# Variables globales accessibles partout
CONFIG = get_device_config()
DEVICE = CONFIG["device"]
COMPUTE_TYPE = CONFIG["compute_type"]

print(f"⚙️ Configuration : {CONFIG['name']} ({DEVICE})")
