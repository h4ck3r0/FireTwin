# Gauge Reader Tuning Guide

## Understanding Hough Circle Detection Parameters

### hough_circles_param1 (Canny Threshold)
- **Default**: 100
- **Range**: 10-500
- **Effect**: Controls edge detection sensitivity
- **Lower values** (50-100): Detect fainter circles, more false positives
- **Higher values** (150-300): Detect only strong circles, fewer false positives

**Tuning**: If no circles detected, decrease param1. If too many false positives, increase it.

### hough_circles_param2 (Accumulator Threshold)
- **Default**: 30
- **Range**: 1-100
- **Effect**: Minimum accumulator votes for circle detection
- **Lower values** (10-20): More circles detected, more false positives
- **Higher values** (50-100): Fewer circles, only prominent ones

**Tuning**: Decrease for detecting multiple gauges or faint circles. Increase for precision.

### Hough Circles Radius Range
- **minRadius**: 50-300 pixels (typical: 50-100)
- **maxRadius**: 100-1000 pixels (typical: 200-300)

**Tuning**: Set range to match your gauge size in the frame. Use tighter ranges for faster processing.

## Understanding Hough Line Detection Parameters

### Canny Edge Detection Thresholds
- **threshold1**: 50 (default) - Lower threshold for edge connectivity
- **threshold2**: 150 (default) - Upper threshold for strong edges
- **Range**: 30-300

**Tuning**:
- Decrease both if needle edges are faint
- Increase to reduce noise in complex lighting
- Ratio should be roughly 1:2 or 1:3

### Hough Line Parameters
- **minLineLength**: 50-100 pixels (minimum needle length)
- **maxLineGap**: 5-20 pixels (gap allowed in connected lines)

**Tuning**:
- Increase minLineLength for stable needle detection
- Decrease maxLineGap to connect broken needle segments

## Gaussian Blur Kernel

- **Default**: (15, 15)
- **Ranges**: (5, 5) to (31, 31), must be odd numbers

**Tuning**:
- Smaller kernels (5, 5) for sharp images
- Larger kernels (21, 21) for noisy video
- Larger = smoother but slower processing

## Common Issues & Solutions

### Issue: Circle Not Detected
1. Decrease `param1` (Canny threshold)
2. Decrease `param2` (accumulator threshold)
3. Increase blur kernel size: (21, 21) or (25, 25)
4. Check lighting - gauge needs distinct edges
5. Adjust radius range

### Issue: Needle Not Detected
1. Decrease Canny thresholds (threshold1 and threshold2)
2. Reduce needle must be more than minLineLength
3. Check contrast - needle needs clear edges
4. Try reducing maxLineGap

### Issue: False Detections (Wrong Circle/Needle)
1. Increase `param2` (accumulator threshold)
2. Increase `threshold2` (upper Canny threshold)
3. Tighten radius range
4. Increase minLineLength for needle
5. Improve lighting

### Issue: Shaking/Jittering Readings
1. Increase smoothing_alpha in main.py (toward 1.0)
2. Increase minLineLength
3. Reduce Gaussian blur (smaller kernel)
4. Improve lighting

## Performance Optimization

### For Real-Time Processing (Target: 30+ FPS)
1. Reduce frame resolution (resize by 0.75 or 0.5)
2. Increase blur kernel: (21, 21)
3. Increase HoughCircles param2 to skip false positives
4. Increase minLineLength to avoid processing noise

### Example Optimized Configuration
```json
{
  "min_angle": 45,
  "max_angle": 315,
  "min_pressure": 0,
  "max_pressure": 100,
  "hough_circles_param1": 150,
  "hough_circles_param2": 50,
  "hough_circles_minRadius": 80,
  "hough_circles_maxRadius": 250,
  "canny_threshold1": 100,
  "canny_threshold2": 200,
  "gaussian_kernel": [21, 21],
  "hough_lines_minLineLength": 80,
  "hough_lines_maxLineGap": 5
}
```

## Testing Your Configuration

1. Save test configuration
2. Run: `python src/main.py --calibration calibrations/test.json`
3. Observe:
   - FPS in top-right
   - Detection rate
   - Circle/needle detection accuracy
4. Adjust parameters one at a time
5. Save final configuration

## Hardware Considerations

### Low-End (Slow) Computers
- Use smaller Gaussian kernel: (11, 11)
- Increase HoughCircles param2 to 50-100
- Resize frames to 50% of original
- Reduce frame capture resolution

### High-End (Fast) Computers
- Can use larger kernels: (25, 25)
- Can enable more aggressive smoothing
- Can process full resolution
- Can detect multiple gauges simultaneously
