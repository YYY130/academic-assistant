# Paper Reference: CBAM — Convolutional Block Attention Module

## Meta Information
- **Title**: CBAM: Convolutional Block Attention Module
- **Authors**: Sanghyun Woo, Jongchan Park, Joon-Young Lee, In So Kweon
- **Venue**: ECCV 2018
- **Year**: 2018
- **arXiv**: 1807.06521
- **Citations**: 39,000+

## Abstract
The paper proposes **Convolutional Block Attention Module (CBAM)**, a simple yet effective attention module for feed-forward convolutional neural networks. Given an intermediate feature map, CBAM sequentially infers attention maps along two separate dimensions — **channel** and **spatial** — then multiplies them to the input feature map for adaptive feature refinement. CBAM is a lightweight and general module that can be integrated into any CNN architecture seamlessly with negligible overhead, and is end-to-end trainable. Extensive experiments on ImageNet-1K, MS COCO, and VOC 2007 datasets demonstrate consistent improvements in classification and detection performance.

## Deep Read — Method

### CBAM Architecture
CBAM consists of two sub-modules applied in sequence:

```
Input Feature (F) → Channel Attention Module → Spatial Attention Module → Refined Feature (F'')
```

#### 1. Channel Attention Module
- **Goal**: Learn "what" to attend to (which feature channels are important)
- **Mechanism**: Uses both **average-pooled** and **max-pooled** features to aggregate spatial information
- **Process**:
  1. Apply both AvgPool and MaxPool along spatial dimensions → two 1×1×C descriptors
  2. Pass both through a shared MLP (multi-layer perceptron) with one hidden layer (reduction ratio r=16)
  3. Sum the two output feature vectors
  4. Apply sigmoid → channel attention map M_c ∈ ℝ^{1×1×C}

```
M_c(F) = σ(MLP(AvgPool(F)) + MLP(MaxPool(F)))
```

#### 2. Spatial Attention Module
- **Goal**: Learn "where" to attend to (which spatial locations are important)
- **Mechanism**: Uses spatial relationships between features
- **Process**:
  1. Apply both AvgPool and MaxPool along channel dimension → two 2D maps (H×W×1 each)
  2. Concatenate the two maps → H×W×2 tensor
  3. Apply 7×7 convolution → H×W×1 map
  4. Apply sigmoid → spatial attention map M_s ∈ ℝ^{H×W×1}

```
M_s(F') = σ(f^{7×7}([AvgPool(F'); MaxPool(F')]))
```

### Key Design Choices
- **Sequential channel→spatial**: Channel attention first, then spatial attention (experimentally shown to be better than parallel or spatial→channel)
- **Both pooling strategies**: MaxPool captures distinctive features; AvgPool captures global statistics — complementary signals
- **7×7 kernel for spatial conv**: Larger receptive field captures broader spatial context
- **Reduction ratio r=16**: Balances performance vs. parameter overhead

## Deep Read — Results

### Ablation Studies
| Variant | Top-1 Error (ImageNet) |
|---------|----------------------|
| ResNet-50 (baseline) | 24.56% |
| + Channel Attention only (SE) | 23.74% |
| + Spatial Attention only | 23.92% |
| + CBAM (Channel→Spatial) | **23.34%** |
| + CBAM (Spatial→Channel) | 23.50% |
| + CBAM (Parallel) | 23.61% |

### Multi-Task Performance
| Task | Backbone | Baseline | +CBAM | Improvement |
|------|----------|----------|-------|-------------|
| ImageNet Classification | ResNet-50 | 76.2% | **77.7%** | +1.5% |
| MS COCO Detection | ResNet-50 | 38.7% | **41.1%** | +2.4% |
| VOC 2007 Detection | ResNet-50 | 79.2% | **81.5%** | +2.3% |

### Parameter Overhead
- CBAM adds only **~0.3M parameters** to ResNet-50 (negligible vs. 25.6M total)
- **Computational cost**: negligible increase in FLOPs (<1%)

## Significance in Medical Image Segmentation

While CBAM was originally proposed for general vision tasks, it became one of the **most widely adopted attention modules in medical image segmentation**, especially integrated into U-Net variants (CBAM-UNet):

- **Dual attention (channel + spatial)** addresses two complementary needs:
  - Channel attention: Feature selection (which feature maps matter)
  - Spatial attention: Localization (where in the image matters)
- **Lightweight**: Can be inserted at every skip connection or bottleneck without significant overhead
- **Modular**: Plug-and-play into any U-Net variant

### CBAM-UNet Performance (from literature)
| Dataset | Metric | U-Net | CBAM-UNet | Improvement |
|---------|--------|-------|-----------|-------------|
| Brain MRI | Dice | ~81.0% | **~84.9%** | +3.9% |
| Brain MRI | IoU | ~74.0% | **~78.3%** | +4.3% |

## References
1. Woo, S., Park, J., Lee, J. Y., & Kweon, I. S. (2018). CBAM: Convolutional Block Attention Module. *ECCV 2018*.
2. Xu, Q., et al. (2023). DCSAU-Net: A deeper and more compact split-attention U-Net. *Computers in Biology and Medicine*.
