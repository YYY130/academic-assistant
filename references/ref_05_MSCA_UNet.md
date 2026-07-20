# Paper Reference: MSCA-UNet — Multi-scale Conv-Attention U-Net

## Meta Information
- **Title**: Multi-scale conv-attention U-Net for medical image segmentation
- **Authors**: P. Pan et al.
- **Venue**: Scientific Reports, Vol.15, 12041 (2025)
- **Year**: 2025
- **DOI**: 10.1038/s41598-025-96101-8
- **Citations**: 44+

## Abstract
The paper proposes a novel network structure based on the U-Net backbone, integrating the **Adaptive Convolution (AC)** module, **Multi-Scale Learning (MSL)** module, and **Conv-Attention** module. The MSL module is designed for multi-scale information fusion. Experimental validation on CVC-ClinicDB, MICCAI 2023 Tooth, and ISIC2017 datasets demonstrates that MSCA-UNet significantly improves segmentation accuracy and model robustness.

## Architecture Contributions

### 1. Adaptive Convolution (AC) Module
- Dynamically adjusts convolution kernel parameters based on input features
- Adapts to varying image characteristics across different medical domains

### 2. Multi-Scale Learning (MSL) Module
- Captures features at multiple scales in parallel
- Addresses the semantic gap between encoder and decoder features
- Fuses multi-scale information comprehensively

### 3. Conv-Attention Module
- Combines convolution with attention mechanism for global context capture
- Enhances feature representation by attending to both local and global patterns

## Results

| Dataset | Metric | MSCA-UNet | Improvement vs Baseline |
|---------|--------|-----------|------------------------|
| CVC-ClinicDB | Dice/IoU | State-of-the-art | Significant |
| MICCAI 2023 Tooth | Dice/IoU | State-of-the-art | Significant |
| ISIC2017 | Dice/IoU | State-of-the-art | Significant |

The model demonstrates that combining multi-scale learning with convolution-based attention achieves robust performance across diverse medical imaging modalities.

## References
1. Pan, P., et al. (2025). Multi-scale conv-attention U-Net for medical image segmentation. *Scientific Reports*, 15, 12041.
