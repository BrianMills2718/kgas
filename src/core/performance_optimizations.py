"""
Performance Optimizations - Phase 8.2

Implements async processing, caching, and batch operations for KGAS tools.
Follows fail-fast principle - optimizations either work properly or fail immediately.
NO DEGRADED MODES - All optimizations must be fully functional.
"""

import asyncio
import time
import hashlib
import json
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    data: Any
    timestamp: datetime
    access_count: int
    size_bytes: int
    ttl_seconds: Optional[int] = None

    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        if self.ttl_seconds is None:
            return False
        return datetime.now() > self.timestamp + timedelta(seconds=self.ttl_seconds)

    def get_age_seconds(self) -> float:
        """Get age of cache entry in seconds"""
        return (datetime.now() - self.timestamp).total_seconds()


class HighPerformanceCache:
    """
    High-performance caching system for KGAS operations.
    
    Features:
    - Thread-safe operations
    - TTL-based expiration
    - Size-based eviction
    - Access-based LRU eviction
    - Performance metrics tracking
    """
    
    def __init__(self, max_size_mb: int = 512, default_ttl_seconds: int = 3600):
        """Initialize cache with size and TTL limits"""
        if max_size_mb <= 0:
            raise ValueError(f"Cache size must be positive, got: {max_size_mb}")
        if default_ttl_seconds <= 0:
            raise ValueError(f"Default TTL must be positive, got: {default_ttl_seconds}")
        
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.default_ttl_seconds = default_ttl_seconds
        self.cache: Dict[str, CacheEntry] = {}
        self.lock = threading.RLock()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'total_requests': 0,
            'total_size_bytes': 0
        }
        
        # Start background cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_expired, daemon=True)
        self.cleanup_thread.start()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self.lock:
            self.stats['total_requests'] += 1
            
            if key not in self.cache:
                self.stats['misses'] += 1
                return None
            
            entry = self.cache[key]
            
            # Check if expired
            if entry.is_expired():
                del self.cache[key]
                self.stats['total_size_bytes'] -= entry.size_bytes
                self.stats['misses'] += 1
                return None
            
            # Update access count and return data
            entry.access_count += 1
            self.stats['hits'] += 1
            return entry.data
    
    def put(self, key: str, data: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Put value in cache"""
        if data is None:
            raise ValueError("Cannot cache None values")
        
        # Calculate size
        try:
            data_size = len(json.dumps(data, default=str).encode('utf-8'))
        except Exception:
            # Fallback size estimation
            data_size = len(str(data).encode('utf-8'))
        
        if data_size > self.max_size_bytes:
            raise ValueError(f"Data too large for cache: {data_size} bytes > {self.max_size_bytes} bytes")
        
        with self.lock:
            # Remove existing entry if present
            if key in self.cache:
                old_entry = self.cache[key]
                self.stats['total_size_bytes'] -= old_entry.size_bytes
            
            # Create new entry
            entry = CacheEntry(
                key=key,
                data=data,
                timestamp=datetime.now(),
                access_count=1,
                size_bytes=data_size,
                ttl_seconds=ttl_seconds or self.default_ttl_seconds
            )
            
            # Ensure we have space
            self._ensure_space(data_size)
            
            # Add to cache
            self.cache[key] = entry
            self.stats['total_size_bytes'] += data_size
            
            return True
    
    def _ensure_space(self, required_bytes: int):
        """Ensure enough space in cache by evicting old entries"""
        while (self.stats['total_size_bytes'] + required_bytes) > self.max_size_bytes:
            if not self.cache:
                break
            
            # Find least recently used entry
            lru_key = min(self.cache.keys(), 
                         key=lambda k: (self.cache[k].access_count, self.cache[k].timestamp))
            
            entry = self.cache[lru_key]
            del self.cache[lru_key]
            self.stats['total_size_bytes'] -= entry.size_bytes
            self.stats['evictions'] += 1
    
    def _cleanup_expired(self):
        """Background thread to clean up expired entries"""
        while True:
            try:
                time.sleep(60)  # Check every minute
                
                with self.lock:
                    expired_keys = [
                        key for key, entry in self.cache.items()
                        if entry.is_expired()
                    ]
                    
                    for key in expired_keys:
                        entry = self.cache[key]
                        del self.cache[key]
                        self.stats['total_size_bytes'] -= entry.size_bytes
                        
            except Exception as e:
                logger.error(f"Cache cleanup error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        with self.lock:
            hit_rate = self.stats['hits'] / max(self.stats['total_requests'], 1)
            return {
                **self.stats,
                'hit_rate': hit_rate,
                'miss_rate': 1 - hit_rate,
                'cache_entries': len(self.cache),
                'size_mb': self.stats['total_size_bytes'] / (1024 * 1024)
            }
    
    def clear(self):
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            self.stats['total_size_bytes'] = 0


class AsyncToolProcessor:
    """
    Async processor for KGAS tools with fail-fast error handling.
    
    Provides async execution of tool operations with proper error propagation.
    NO DEGRADED MODES - Operations either succeed fully or fail immediately.
    """
    
    def __init__(self, max_concurrent_operations: int = 10):
        """Initialize async processor"""
        if max_concurrent_operations <= 0:
            raise ValueError(f"Max concurrent operations must be positive, got: {max_concurrent_operations}")
        
        self.max_concurrent = max_concurrent_operations
        self.semaphore = asyncio.Semaphore(max_concurrent_operations)
        self.cache = HighPerformanceCache(max_size_mb=256, default_ttl_seconds=1800)
        self.stats = {
            'operations_completed': 0,
            'operations_failed': 0,
            'cache_hits': 0,
            'total_execution_time': 0.0,
            'concurrent_operations': 0
        }
    
    async def execute_tool_async(self, tool: Any, request: Any, cache_key: Optional[str] = None) -> Any:
        """Execute tool operation asynchronously with caching"""
        async with self.semaphore:
            self.stats['concurrent_operations'] += 1
            start_time = time.time()
            
            try:
                # Check cache first if cache key provided
                if cache_key:
                    cached_result = self.cache.get(cache_key)
                    if cached_result is not None:
                        self.stats['cache_hits'] += 1
                        return cached_result
                
                # Execute tool operation in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, tool.execute, request)
                
                # Validate result
                if not result:
                    raise RuntimeError(f"Tool {tool.__class__.__name__} returned no result")
                
                # Check for error status
                if hasattr(result, 'status') and result.status == 'error':
                    error_msg = getattr(result, 'error_message', 'Unknown error')
                    raise RuntimeError(f"Tool {tool.__class__.__name__} failed: {error_msg}")
                
                # Cache successful result
                if cache_key and result:
                    try:
                        self.cache.put(cache_key, result, ttl_seconds=1800)  # 30 minutes
                    except Exception as e:
                        logger.warning(f"Failed to cache result: {e}")
                
                execution_time = time.time() - start_time
                self.stats['operations_completed'] += 1
                self.stats['total_execution_time'] += execution_time
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                self.stats['operations_failed'] += 1
                self.stats['total_execution_time'] += execution_time
                
                # Re-raise with context
                raise RuntimeError(f"Async tool execution failed after {execution_time:.3f}s: {e}")
            
            finally:
                self.stats['concurrent_operations'] -= 1
    
    async def execute_batch_async(self, operations: List[Tuple[Any, Any, Optional[str]]]) -> List[Any]:
        """Execute multiple tool operations concurrently"""
        if not operations:
            raise ValueError("Cannot execute empty batch of operations")
        
        if len(operations) > self.max_concurrent * 2:
            raise ValueError(f"Batch too large: {len(operations)} operations > {self.max_concurrent * 2} max")
        
        # Create async tasks for all operations
        tasks = []
        for tool, request, cache_key in operations:
            task = self.execute_tool_async(tool, request, cache_key)
            tasks.append(task)
        
        # Execute all tasks concurrently
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check for failures and fail fast if any operation failed
            failed_operations = [
                (i, result) for i, result in enumerate(results)
                if isinstance(result, Exception)
            ]
            
            if failed_operations:
                error_details = []
                for i, error in failed_operations:
                    error_details.append(f"Operation {i}: {str(error)}")
                
                raise RuntimeError(f"Batch execution failed - {len(failed_operations)}/{len(operations)} operations failed:\n" + 
                                 "\n".join(error_details))
            
            return results
            
        except Exception as e:
            # Log batch failure details
            logger.error(f"Batch execution failed with {len(operations)} operations: {e}")
            raise RuntimeError(f"Batch execution failed: {e}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get async processor performance statistics"""
        cache_stats = self.cache.get_stats()
        
        total_ops = self.stats['operations_completed'] + self.stats['operations_failed']
        avg_execution_time = (self.stats['total_execution_time'] / max(total_ops, 1))
        success_rate = self.stats['operations_completed'] / max(total_ops, 1)
        
        return {
            'async_processor': {
                **self.stats,
                'total_operations': total_ops,
                'success_rate': success_rate,
                'average_execution_time': avg_execution_time,
                'max_concurrent': self.max_concurrent
            },
            'cache_performance': cache_stats
        }


class BatchProcessor:
    """
    High-performance batch processor for KGAS operations.
    
    Optimizes processing of multiple documents or operations by:
    - Grouping similar operations
    - Minimizing tool initialization overhead
    - Parallel processing with controlled concurrency
    - Fail-fast error handling for entire batches
    """
    
    def __init__(self, max_workers: int = 4, batch_size: int = 10):
        """Initialize batch processor"""
        if max_workers <= 0:
            raise ValueError(f"Max workers must be positive, got: {max_workers}")
        if batch_size <= 0:
            raise ValueError(f"Batch size must be positive, got: {batch_size}")
        
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
    def process_documents_batch(self, documents: List[str], tool_chain: List[Any]) -> List[Dict[str, Any]]:
        """Process multiple documents through a chain of tools"""
        if not documents:
            raise ValueError("Cannot process empty document list")
        if not tool_chain:
            raise ValueError("Cannot process documents without tools")
        
        # Split into batches
        batches = [documents[i:i + self.batch_size] for i in range(0, len(documents), self.batch_size)]
        
        all_results = []
        failed_batches = []
        
        # Process batches in parallel
        future_to_batch = {
            self.executor.submit(self._process_single_batch, batch, tool_chain): batch
            for batch in batches
        }
        
        for future in as_completed(future_to_batch):
            batch = future_to_batch[future]
            try:
                batch_results = future.result()
                all_results.extend(batch_results)
            except Exception as e:
                failed_batches.append((batch, str(e)))
                logger.error(f"Batch processing failed for batch {batches.index(batch)}: {e}")
        
        # Fail fast if any batch failed
        if failed_batches:
            total_failed_docs = sum(len(batch) for batch, _ in failed_batches)
            raise RuntimeError(f"Batch processing failed: {total_failed_docs}/{len(documents)} documents failed")
        
        return all_results
    
    def _process_single_batch(self, batch: List[str], tool_chain: List[Any]) -> List[Dict[str, Any]]:
        """Process a single batch of documents"""
        batch_results = []
        
        for doc in batch:
            try:
                result = self._process_single_document(doc, tool_chain)
                batch_results.append(result)
            except Exception as e:
                raise RuntimeError(f"Document processing failed in batch: {e}")
        
        return batch_results
    
    def _process_single_document(self, document: str, tool_chain: List[Any]) -> Dict[str, Any]:
        """Process a single document through the tool chain"""
        current_data = document
        pipeline_results = {}
        
        for i, tool in enumerate(tool_chain):
            try:
                # Create appropriate request for tool
                if hasattr(tool, 'execute'):
                    if 'pdf_loader' in tool.__class__.__name__.lower():
                        request = type('Request', (), {
                            'tool_id': tool.__class__.__name__,
                            'operation': 'load',
                            'input_data': {'file_path': current_data if isinstance(current_data, str) else str(current_data)}
                        })()
                    elif 'chunker' in tool.__class__.__name__.lower():
                        text_data = current_data if isinstance(current_data, str) else str(current_data)
                        request = type('Request', (), {
                            'tool_id': tool.__class__.__name__,
                            'operation': 'chunk',
                            'input_data': {'text': text_data, 'document_ref': f'batch_doc_{i}'}
                        })()
                    elif 'ner' in tool.__class__.__name__.lower():
                        text_data = current_data if isinstance(current_data, str) else str(current_data)
                        request = type('Request', (), {
                            'tool_id': tool.__class__.__name__,
                            'operation': 'extract',
                            'input_data': {'text': text_data, 'chunk_ref': f'batch_chunk_{i}'}
                        })()
                    else:
                        # Generic request
                        request = type('Request', (), {
                            'tool_id': tool.__class__.__name__,
                            'operation': 'process',
                            'input_data': {'data': current_data}
                        })()
                    
                    result = tool.execute(request)
                    
                    # Extract relevant data for next tool
                    if hasattr(result, 'data') and result.data:
                        current_data = result.data
                    else:
                        current_data = result
                    
                    pipeline_results[f'step_{i}_{tool.__class__.__name__}'] = result
                
                else:
                    raise RuntimeError(f"Tool {tool.__class__.__name__} does not have execute method")
                
            except Exception as e:
                raise RuntimeError(f"Tool {tool.__class__.__name__} failed in pipeline: {e}")
        
        return {
            'document': document,
            'final_result': current_data,
            'pipeline_results': pipeline_results,
            'processing_timestamp': datetime.now().isoformat()
        }
    
    def shutdown(self):
        """Shutdown the batch processor"""
        self.executor.shutdown(wait=True)


def create_cache_key(operation: str, input_data: Any) -> str:
    """Create deterministic cache key for operation and input"""
    # Create hash of operation and input data
    data_str = json.dumps(input_data, sort_keys=True, default=str)
    combined = f"{operation}:{data_str}"
    return hashlib.sha256(combined.encode()).hexdigest()[:32]


def validate_performance_requirements(stats: Dict[str, Any], thresholds: Dict[str, float]) -> bool:
    """Validate that performance meets minimum requirements"""
    # Check success rate
    if 'success_rate' in stats and stats['success_rate'] < thresholds.get('min_success_rate', 0.95):
        raise RuntimeError(f"Success rate too low: {stats['success_rate']:.1%} < {thresholds['min_success_rate']:.1%}")
    
    # Check average execution time
    if 'average_execution_time' in stats and stats['average_execution_time'] > thresholds.get('max_avg_time', 5.0):
        raise RuntimeError(f"Average execution time too high: {stats['average_execution_time']:.2f}s > {thresholds['max_avg_time']}s")
    
    # Check cache hit rate
    if 'cache_performance' in stats and 'hit_rate' in stats['cache_performance']:
        hit_rate = stats['cache_performance']['hit_rate']
        if hit_rate < thresholds.get('min_cache_hit_rate', 0.3):
            raise RuntimeError(f"Cache hit rate too low: {hit_rate:.1%} < {thresholds['min_cache_hit_rate']:.1%}")
    
    return True


# Example usage and testing functions
async def example_async_processing():
    """Example of async tool processing"""
    processor = AsyncToolProcessor(max_concurrent_operations=5)
    
    # Mock tools and requests for demonstration
    class MockTool:
        def __init__(self, processing_time=0.1):
            self.processing_time = processing_time
        
        def execute(self, request):
            time.sleep(self.processing_time)  # Simulate processing
            return {"status": "success", "data": f"processed_{request.input_data}"}
    
    tools = [MockTool(0.1) for _ in range(3)]
    requests = [type('Request', (), {'input_data': f'data_{i}'})() for i in range(3)]
    
    # Create batch operations
    operations = [(tool, req, f"cache_key_{i}") for i, (tool, req) in enumerate(zip(tools, requests))]
    
    start_time = time.time()
    results = await processor.execute_batch_async(operations)
    execution_time = time.time() - start_time
    
    print(f"Async batch processing completed in {execution_time:.3f}s")
    print(f"Performance stats: {processor.get_performance_stats()}")
    
    return results


if __name__ == "__main__":
    # Test the performance optimizations
    import asyncio
    
    print("Testing performance optimizations...")
    
    # Test cache
    cache = HighPerformanceCache(max_size_mb=1, default_ttl_seconds=60)
    cache.put("test_key", {"data": "test_value"})
    cached_value = cache.get("test_key")
    print(f"Cache test: {cached_value}")
    print(f"Cache stats: {cache.get_stats()}")
    
    # Test async processing
    asyncio.run(example_async_processing())
    
    print("✅ Performance optimization tests completed")