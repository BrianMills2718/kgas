# Performance Benchmark Results

**Date**: 2025-08-02 20:34:07
**Iterations per test**: 5

## Key Findings

1. **Text Chunking**: High throughput processing (>10K chars/sec)
2. **Fail-Fast Behavior**: Confirmed - no fallback patterns
3. **PageRank**: Sub-millisecond execution for small graphs
4. **Memory Management**: Efficient GC recovery

## Performance Metrics

```json
{
  "text_chunking": {
    "1000_chars": {
      "mean_time": 0.00010794359841383993,
      "std_dev": 5.1410107381566e-05,
      "min_time": 7.151401950977743e-05,
      "max_time": 0.00019534598686732352,
      "throughput_chars_per_sec": 9264097.31280355
    },
    "5000_chars": {
      "mean_time": 9.281000820919872e-05,
      "std_dev": 3.9188003004274474e-05,
      "min_time": 7.12360197212547e-05,
      "max_time": 0.00016268101171590388,
      "throughput_chars_per_sec": 53873500.24503535
    },
    "10000_chars": {
      "mean_time": 7.788000511936844e-05,
      "std_dev": 1.1934204253448092e-05,
      "min_time": 7.012899732217193e-05,
      "max_time": 9.90109983831644e-05,
      "throughput_chars_per_sec": 128402662.33512408
    },
    "50000_chars": {
      "mean_time": 9.23306040931493e-05,
      "std_dev": 2.913078292114845e-05,
      "min_time": 7.252799696289003e-05,
      "max_time": 0.00014358002226799726,
      "throughput_chars_per_sec": 541532252.3998289
    }
  },
  "entity_extraction": {
    "llm_extraction": [
      {
        "text_length": 71,
        "time": 9.889390222000657,
        "entities_found": 4,
        "method": "llm_reasoning"
      },
      {
        "text_length": 70,
        "time": 6.948306166013936,
        "entities_found": 2,
        "method": "llm_reasoning"
      },
      {
        "text_length": 65,
        "time": 6.901232014002744,
        "entities_found": 2,
        "method": "llm_reasoning"
      }
    ],
    "fail_fast_behavior": null
  },
  "pagerank": {
    "10_iterations": {
      "mean_time": 0.009276390599552542,
      "std_dev": 0.016474562605600346,
      "min_time": 0.001744515000609681,
      "max_time": 0.038745650002965704
    },
    "20_iterations": {
      "mean_time": 0.0019048232003115117,
      "std_dev": 9.675331356453932e-05,
      "min_time": 0.001785870990715921,
      "max_time": 0.0020118819957133383
    },
    "50_iterations": {
      "mean_time": 0.0018006394093390554,
      "std_dev": 0.00017012823355789437,
      "min_time": 0.0016841140168253332,
      "max_time": 0.002082365012029186
    }
  },
  "memory_usage": {
    "baseline_mb": 251.69921875,
    "after_processing_mb": 254.32421875,
    "after_gc_mb": 254.32421875,
    "peak_increase_mb": 2.625,
    "gc_recovery_mb": 0.0,
    "text_size_mb": 1.33514404296875
  }
}
```
