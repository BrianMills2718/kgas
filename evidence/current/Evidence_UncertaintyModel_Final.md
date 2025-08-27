# Evidence: Uncertainty Model Results

## Summary
The uncertainty model uses regex patterns and extraction metrics to estimate quality. When properly tested on paired documents (same content with/without noise), it shows positive correlation between uncertainty and extraction errors.

## Key Results

### Paired Document Test (Same Content, Different Noise):
- **Clean text**: F1 = 0.467, Uncertainty = 0.636
- **OCR noise**: F1 = 0.467, Uncertainty = 0.799
- **Heavy noise**: F1 = 0.364, Uncertainty = 0.794

### What Works:
- Detects OCR patterns (Br1an, gr@ph, etc.)
- Higher uncertainty for noisier text
- Positive correlation when comparing same content

### What's Limited:
- OCR detection is just regex patterns
- Uncertainty doesn't predict extraction quality well
- LLM is robust to OCR errors anyway
- F1 scores still low overall (0.3-0.5)

## Conclusion
The uncertainty model is a basic quality heuristic, not a sophisticated predictor. The real issue is improving extraction performance, not measuring uncertainty.

---

*Generated: 2025-08-27*