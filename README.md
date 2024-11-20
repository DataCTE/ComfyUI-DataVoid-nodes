# ComfyUI-DataVoid-nodes

A collection of custom nodes for ComfyUI focused on model merging and style adaptation.

## Nodes

### IPAdapter (Same.Energy)
A node that automatically fetches reference images from Same.Energy based on style prompts and applies them using IPAdapter.

#### Features:
- Automatically searches and retrieves reference images based on style descriptions
- Integrates with IPAdapter for style transfer
- Handles cleanup of temporary images
- Supports negative images and attention masks
- Built-in error handling for API requests

#### Parameters:
- `model`: The base model to apply the style to
- `ipadapter`: IPAdapter model
- `clip_vision`: CLIP Vision model
- `style_prompt`: Description of the desired style (e.g., "studio ghibli style")
- `weight`: Strength of the style application (0.0 to 5.0)
- `start_at`: Starting point for style application (0.0 to 1.0)
- `end_at`: Ending point for style application (0.0 to 1.0)
- `image_negative` (optional): Negative reference image
- `attn_mask` (optional): Attention mask for localized application

### Mega Merge SDXL
A sophisticated model merging node designed specifically for SDXL models, using block-wise merging strategies.

#### Features:
- Intelligent block-based model merging
- Preserves non-UNet components
- Supports complex merging patterns
- Memory efficient processing

#### Parameters:
- `model1`: First SDXL model
- `model2`: Second SDXL model

#### Merging Strategy:
The node uses a predefined range pattern that alternates between models across different blocks:
```python
ranges = [
(0, 16, 1.0, 0.0), # Model 1 only
(8, 24, 0.0, 1.0), # Model 2 only
(17, 32, 1.0, 0.0), # Model 1 only
# ... and so on
]
```

## Installation

1. Clone this repository into your ComfyUI custom nodes directory:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/datacte/ComfyUI-DataVoid-nodes.git
```
