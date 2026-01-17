
## Real Academic Pipeline Testing Evidence
**Timestamp**: 2025-09-05T08:22:29.464604
**Document**: /tmp/tmp2e0kvpz2.txt
**Pipeline Success**: ✅
**Processing Time**: 0.01s
**Entities Extracted**: 28
**SpaCy Entities**: 0
**LLM Entities**: 28
**LaTeX Generated**: ✅
**BibTeX Generated**: ✅
**Academic Utility Score**: 100.0%


## Real Academic Pipeline Testing Evidence
**Timestamp**: 2025-09-05T08:22:29.467752
**Document**: /tmp/tmpceowenss.txt
**Pipeline Success**: ✅
**Processing Time**: 0.00s
**Entities Extracted**: 28
**SpaCy Entities**: 0
**LLM Entities**: 28
**LaTeX Generated**: ✅
**BibTeX Generated**: ✅
**Academic Utility Score**: 100.0%


## Real Academic Pipeline Testing Evidence
**Timestamp**: 2025-09-05T08:22:29.470387
**Document**: /tmp/tmpsf2ato_d.txt
**Pipeline Success**: ✅
**Processing Time**: 0.00s
**Entities Extracted**: 28
**SpaCy Entities**: 0
**LLM Entities**: 28
**LaTeX Generated**: ✅
**BibTeX Generated**: ✅
**Academic Utility Score**: 100.0%


## Real Academic Pipeline Testing Evidence
**Timestamp**: 2025-09-05T08:22:29.472752
**Document**: /tmp/tmpxzzwjb0j.txt
**Pipeline Success**: ✅
**Processing Time**: 0.00s
**Entities Extracted**: 28
**SpaCy Entities**: 0
**LLM Entities**: 28
**LaTeX Generated**: ✅
**BibTeX Generated**: ✅
**Academic Utility Score**: 100.0%


## **PDF_TO_GRAPH_PIPELINE_TEST**
**TIMESTAMP**: 2025-09-05T08:22:43.612141
**VERIFICATION_HASH**: ada9ed6c8c4bf9e67f9be10dd61a8ca2a285b6943b90faf926afc2851a65690e
**DETAILS**: 
```json
{
  "timestamp": "2025-09-05T08:22:43.612141",
  "operation": "PDF_TO_GRAPH_PIPELINE_TEST",
  "details": {
    "pdf_loading": {
      "status": "failed",
      "error": "No module named 'pypdf'"
    },
    "text_chunking": {
      "status": "unknown",
      "output": null
    },
    "entity_extraction": {
      "status": "unknown",
      "output": null
    },
    "relationship_extraction": {
      "status": "unknown",
      "output": null
    },
    "graph_building": {
      "status": "unknown",
      "output": null
    }
  },
  "system_info": {
    "cpu_usage": 0.0,
    "memory_usage": 47.0,
    "disk_usage": 7.1,
    "python_version": "3.12.3 (main, Aug 14 2025, 17:47:21) [GCC 13.3.0]",
    "timestamp": 1757085763.6187298
  },
  "verification_hash": "ada9ed6c8c4bf9e67f9be10dd61a8ca2a285b6943b90faf926afc2851a65690e"
}
```
---

## **PDF_TO_GRAPH_PIPELINE_TEST**
**TIMESTAMP**: 2025-09-05T08:25:41.214932
**VERIFICATION_HASH**: f867d96fd7097390ebb4df947cf95cf263cf9c40a0f2b490f16d603fdede0748
**DETAILS**: 
```json
{
  "timestamp": "2025-09-05T08:25:41.214932",
  "operation": "PDF_TO_GRAPH_PIPELINE_TEST",
  "details": {
    "pdf_loading": {
      "status": "failed",
      "error": "No module named 'pypdf'"
    },
    "text_chunking": {
      "status": "unknown",
      "output": null
    },
    "entity_extraction": {
      "status": "unknown",
      "output": null
    },
    "relationship_extraction": {
      "status": "unknown",
      "output": null
    },
    "graph_building": {
      "status": "unknown",
      "output": null
    }
  },
  "system_info": {
    "cpu_usage": 0.0,
    "memory_usage": 46.3,
    "disk_usage": 7.1,
    "python_version": "3.12.3 (main, Aug 14 2025, 17:47:21) [GCC 13.3.0]",
    "timestamp": 1757085941.2235374
  },
  "verification_hash": "f867d96fd7097390ebb4df947cf95cf263cf9c40a0f2b490f16d603fdede0748"
}
```
---

## **PHASE_INTERFACE_COMPATIBILITY_TEST**
**TIMESTAMP**: 2025-09-05T08:25:48.656189
**VERIFICATION_HASH**: b439f9ffd210ca78babc35abf033333122cb4c27903c9d02482c8da6a3c61fd2
**DETAILS**: 
```json
{
  "timestamp": "2025-09-05T08:25:48.656189",
  "operation": "PHASE_INTERFACE_COMPATIBILITY_TEST",
  "details": {
    "phase1_output": {
      "entities": [
        {
          "name": "Climate Change",
          "type": "CONCEPT",
          "properties": {}
        },
        {
          "name": "Paris Agreement",
          "type": "DOCUMENT",
          "properties": {}
        }
      ],
      "relationships": [
        {
          "source": "Climate Change",
          "target": "Paris Agreement",
          "type": "MENTIONED_IN"
        }
      ]
    },
    "phase2_input_compatibility": false,
    "phase2_output": null,
    "phase3_input_compatibility": false,
    "phase3_output": null,
    "phase1_error": "No module named 'src.core.orchestration.workflow_configuration'",
    "phase2_error": "attempted relative import beyond top-level package"
  },
  "system_info": {
    "cpu_usage": 9.0,
    "memory_usage": 47.6,
    "disk_usage": 7.1,
    "python_version": "3.12.3 (main, Aug 14 2025, 17:47:21) [GCC 13.3.0]",
    "timestamp": 1757085948.6563659
  },
  "verification_hash": "b439f9ffd210ca78babc35abf033333122cb4c27903c9d02482c8da6a3c61fd2"
}
```
---

## **DATA_FLOW_VALIDATION_TEST**
**TIMESTAMP**: 2025-09-05T08:25:48.657986
**VERIFICATION_HASH**: c81ac8363558c5496dfdba7f7592934b176b5be9a2d45b19f8ca0ab117874f3c
**DETAILS**: 
```json
{
  "timestamp": "2025-09-05T08:25:48.657986",
  "operation": "DATA_FLOW_VALIDATION_TEST",
  "details": {
    "input_validation": true,
    "transformation_steps": [
      {
        "step": "text_processing",
        "status": "success",
        "output_type": "str"
      },
      {
        "step": "entity_extraction",
        "status": "success",
        "output_type": "list"
      },
      {
        "step": "relationship_building",
        "status": "success",
        "output_type": "list"
      }
    ],
    "output_validation": true,
    "data_integrity": true
  },
  "system_info": {
    "cpu_usage": 66.7,
    "memory_usage": 47.6,
    "disk_usage": 7.1,
    "python_version": "3.12.3 (main, Aug 14 2025, 17:47:21) [GCC 13.3.0]",
    "timestamp": 1757085948.658307
  },
  "verification_hash": "c81ac8363558c5496dfdba7f7592934b176b5be9a2d45b19f8ca0ab117874f3c"
}
```
---

## Real Academic Pipeline Testing Evidence
**Timestamp**: 2025-09-05T08:25:50.145248
**Document**: /tmp/tmprqi9rpmp.txt
**Pipeline Success**: ✅
**Processing Time**: 0.01s
**Entities Extracted**: 28
**SpaCy Entities**: 0
**LLM Entities**: 28
**LaTeX Generated**: ✅
**BibTeX Generated**: ✅
**Academic Utility Score**: 100.0%


## Real Academic Pipeline Testing Evidence
**Timestamp**: 2025-09-05T08:25:50.148274
**Document**: /tmp/tmppfk0guhv.txt
**Pipeline Success**: ✅
**Processing Time**: 0.00s
**Entities Extracted**: 28
**SpaCy Entities**: 0
**LLM Entities**: 28
**LaTeX Generated**: ✅
**BibTeX Generated**: ✅
**Academic Utility Score**: 100.0%


## Real Academic Pipeline Testing Evidence
**Timestamp**: 2025-09-05T08:25:50.150508
**Document**: /tmp/tmp8mltxvh_.txt
**Pipeline Success**: ✅
**Processing Time**: 0.00s
**Entities Extracted**: 28
**SpaCy Entities**: 0
**LLM Entities**: 28
**LaTeX Generated**: ✅
**BibTeX Generated**: ✅
**Academic Utility Score**: 100.0%


## Real Academic Pipeline Testing Evidence
**Timestamp**: 2025-09-05T08:25:50.152656
**Document**: /tmp/tmpsk55lr52.txt
**Pipeline Success**: ✅
**Processing Time**: 0.00s
**Entities Extracted**: 28
**SpaCy Entities**: 0
**LLM Entities**: 28
**LaTeX Generated**: ✅
**BibTeX Generated**: ✅
**Academic Utility Score**: 100.0%

