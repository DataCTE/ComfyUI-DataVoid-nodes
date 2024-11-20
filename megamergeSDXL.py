import torch
import re

class MegaMergeSDXL:
    def __init__(self):
        self.ranges = [
            (0, 16, 1.0, 0.0),    # Model 1 only
            (8, 24, 0.0, 1.0),    # Model 2 only
            (17, 32, 1.0, 0.0),   # Model 1 only
            (25, 40, 0.0, 1.0),   # Model 2 only
            (33, 48, 1.0, 0.0),   # Model 1 only
            (41, 56, 0.0, 1.0),   # Model 2 only
            (49, 64, 1.0, 0.0),   # Model 1 only
            (57, 72, 0.0, 1.0),   # Model 2 only
            (65, 80, 1.0, 0.0)    # Model 1 only
        ]

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model1": ("MODEL",),
                "model2": ("MODEL",),
            },
        }

    RETURN_TYPES = ("MODEL",)
    RETURN_NAMES = ("merged_model",)
    FUNCTION = "merge"
    CATEGORY = "model_merging"

    def get_block_number(self, key):
        """Extract block number from U-Net key if present"""
        patterns = [
            r'input_blocks.(\d+)',
            r'middle_block.(\d+)',
            r'output_blocks.(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, key)
            if match:
                return int(match.group(1))
        return None

    def merge(self, model1, model2):
        # Extract state dictionaries
        m1_state_dict = model1.model.state_dict()
        m2_state_dict = model2.model.state_dict()
        
        merged_state_dict = {}
        
        # Get all U-Net keys
        unet_keys = [k for k in m1_state_dict.keys() if k.startswith('model.diffusion_model')]
        
        # Copy non-UNet keys from model1
        for key in m1_state_dict.keys():
            if key not in unet_keys:
                merged_state_dict[key] = m1_state_dict[key]
        
        # Merge UNet keys
        for key in unet_keys:
            merged_tensor = torch.zeros_like(m1_state_dict[key])
            block_num = self.get_block_number(key)
            
            if block_num is None:
                merged_tensor = (m1_state_dict[key] + m2_state_dict[key]) / 2
                merged_state_dict[key] = merged_tensor
                continue
                
            active_ranges = [r for r in self.ranges if r[0] <= block_num <= r[1]]
            
            if not active_ranges:
                merged_tensor = m1_state_dict[key]
            else:
                weight_sum = torch.zeros_like(m1_state_dict[key])
                total_weight = 0
                
                for *_, m1_ratio, m2_ratio in active_ranges:
                    weight_sum += m1_state_dict[key] * m1_ratio + m2_state_dict[key] * m2_ratio
                    total_weight += m1_ratio + m2_ratio
                
                merged_tensor = weight_sum / total_weight
            
            merged_state_dict[key] = merged_tensor
        
        # Create new model with merged weights
        model_out = model1.clone()
        model_out.model.load_state_dict(merged_state_dict)
        
        return (model_out,)

# Node class mappings for ComfyUI
NODE_CLASS_MAPPINGS = {
    "MegaMergeSDXL": MegaMergeSDXL
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MegaMergeSDXL": "Mega Merge SDXL"
}
