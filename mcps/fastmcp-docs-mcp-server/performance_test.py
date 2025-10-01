#!/usr/bin/env python3
"""
Performance comparison script for original vs improved FastMCP Documentation Server
"""

import time
import tempfile
import os
from pathlib import Path

# For this script to work, we need to temporarily modify the server to make functions testable
# Since the original server functions are decorated and not directly callable,
# this script demonstrates how we could compare performance if both were testable

def create_test_docs(docs_dir):
    """Create a set of test documentation files"""
    # Create some nested documentation structure
    os.makedirs(os.path.join(docs_dir, "api"), exist_ok=True)
    os.makedirs(os.path.join(docs_dir, "tutorials"), exist_ok=True)
    os.makedirs(os.path.join(docs_dir, "examples"), exist_ok=True)
    
    # Create multiple files
    for i in range(10):
        with open(os.path.join(docs_dir, f"doc_{i}.md"), "w") as f:
            f.write(f"# Document {i}\n\nThis is document {i} content for testing performance.\n" * 20)
        
        with open(os.path.join(docs_dir, "api", f"api_doc_{i}.md"), "w") as f:
            f.write(f"# API Document {i}\n\nAPI documentation for function {i}.\n" * 15)
        
        with open(os.path.join(docs_dir, "tutorials", f"tutorial_{i}.md"), "w") as f:
            f.write(f"# Tutorial {i}\n\nStep-by-step tutorial {i} about FastMCP.\n" * 10)
        
        with open(os.path.join(docs_dir, "examples", f"example_{i}.md"), "w") as f:
            f.write(f"# Example {i}\n\nCode example showing how to use FastMCP in example {i}.\n" * 12)


def test_performance():
    """Test performance of the improved server"""
    print("Setting up performance test...")
    
    # Create temporary documentation
    temp_docs = tempfile.mkdtemp()
    create_test_docs(temp_docs)
    
    print(f"Created test documentation in: {temp_docs}")
    print("Testing with 40 files containing various content...")
    
    # Import the testable improved server
    import sys
    sys.path.insert(0, '.')
    import testable_improved_server as improved_server
    
    # Temporarily update the docs path
    original_docs_path = improved_server.DOCS_BASE_PATH
    improved_server.DOCS_BASE_PATH = temp_docs
    
    # Update config as well if available
    if hasattr(improved_server, 'config'):
        improved_server.config.docs_base_path = temp_docs
    
    print("\nPerformance comparison:")
    print("======================")
    
    # Test search performance
    print("\n1. Testing search_documentation performance...")
    start_time = time.time()
    results = improved_server._search_documentation_impl("FastMCP")
    end_time = time.time()
    print(f"   Search time: {end_time - start_time:.4f} seconds")
    print(f"   Found {len(results)} results")
    
    # Test file reading performance (with cache)
    print("\n2. Testing read_documentation_file performance (first read)...")
    start_time = time.time()
    content = improved_server._read_documentation_file_impl("doc_0.md")
    first_read_time = time.time() - start_time
    print(f"   First read time: {first_read_time:.4f} seconds")
    
    print("3. Testing read_documentation_file performance (cached read)...")
    start_time = time.time()
    content = improved_server._read_documentation_file_impl("doc_0.md")
    cached_read_time = time.time() - start_time
    print(f"   Cached read time: {cached_read_time:.4f} seconds")
    print(f"   Cache improvement: {first_read_time/cached_read_time:.2f}x faster")
    
    # Test listing sections
    print("\n4. Testing list_documentation_sections performance...")
    start_time = time.time()
    sections = improved_server._list_documentation_sections_impl()
    end_time = time.time()
    print(f"   List sections time: {end_time - start_time:.4f} seconds")
    print(f"   Found {len(sections)} sections")
    
    # Test getting files per section
    print("\n5. Testing get_section_files performance...")
    start_time = time.time()
    files = improved_server._get_section_files_impl("api")
    end_time = time.time()
    print(f"   Get files time: {end_time - start_time:.4f} seconds")
    print(f"   Found {len(files)} files in 'api' section")
    
    # Restore original docs path
    improved_server.DOCS_BASE_PATH = original_docs_path
    if hasattr(improved_server, 'config'):
        improved_server.config.docs_base_path = original_docs_path
    
    # Clean up
    import shutil
    shutil.rmtree(temp_docs, ignore_errors=True)
    
    print(f"\nPerformance test completed!")
    print(f"The improved server includes:")
    print(f"- Caching for better repeated access performance")
    print(f"- Rate limiting to prevent abuse")
    print(f"- Optimized search algorithms")
    print(f"- Better error handling and logging")


if __name__ == "__main__":
    test_performance()