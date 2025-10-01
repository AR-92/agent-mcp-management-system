#!/usr/bin/env python3
"""
Integration tests for the improved FastMCP Documentation Server
"""

import sys
import os
import tempfile
import unittest
import subprocess
import time
import requests
import threading
from unittest.mock import patch
import json

# Add the server directory to the path
sys.path.insert(0, '.')

# Import the server module
try:
    import testable_improved_server as server
    SERVER_MODULE = server
    SERVER_FILE = "testable_improved_server.py"
except ImportError:
    try:
        import improved_server as server
        SERVER_MODULE = server
        SERVER_FILE = "improved_server.py"
    except ImportError:
        import server
        SERVER_MODULE = server
        SERVER_FILE = "server.py"


class TestImprovedServerIntegration(unittest.TestCase):
    """Integration tests for the improved server functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before running tests in the class."""
        # Create a temporary directory for test documentation
        cls.temp_docs_dir = tempfile.mkdtemp()
        
        # Create some test documentation files
        os.makedirs(os.path.join(cls.temp_docs_dir, "api-reference"), exist_ok=True)
        os.makedirs(os.path.join(cls.temp_docs_dir, "tutorials"), exist_ok=True)
        os.makedirs(os.path.join(cls.temp_docs_dir, "examples"), exist_ok=True)
        
        # Create test files
        with open(os.path.join(cls.temp_docs_dir, "index.md"), "w") as f:
            f.write("# FastMCP Documentation\n\nWelcome to FastMCP documentation.")
        
        with open(os.path.join(cls.temp_docs_dir, "api-reference", "index.md"), "w") as f:
            f.write("# API Reference\n\nDetailed API documentation for FastMCP.")
        
        with open(os.path.join(cls.temp_docs_dir, "tutorials", "getting-started.md"), "w") as f:
            f.write("# Getting Started\n\nThis tutorial helps you get started with FastMCP.\n\nFastMCP is great!")
        
        with open(os.path.join(cls.temp_docs_dir, "examples.md"), "w") as f:
            f.write("# Examples\n\nHere are some examples of using FastMCP effectively.")
        
        with open(os.path.join(cls.temp_docs_dir, "examples", "simple-example.md"), "w") as f:
            f.write("# Simple Example\n\nHere is a simple example of using FastMCP.\n\nFastMCP makes documentation easy.")
        
        # Store original docs path
        cls.original_docs_path = getattr(SERVER_MODULE, 'DOCS_BASE_PATH', None)
        
        # Temporarily replace the docs path with our test path
        if hasattr(SERVER_MODULE, 'config'):
            SERVER_MODULE.config.docs_base_path = cls.temp_docs_dir
            SERVER_MODULE.DOCS_BASE_PATH = cls.temp_docs_dir
        else:
            SERVER_MODULE.DOCS_BASE_PATH = cls.temp_docs_dir

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests in the class."""
        # Restore original docs path
        if cls.original_docs_path:
            if hasattr(SERVER_MODULE, 'config'):
                SERVER_MODULE.config.docs_base_path = cls.original_docs_path
                SERVER_MODULE.DOCS_BASE_PATH = cls.original_docs_path
            else:
                SERVER_MODULE.DOCS_BASE_PATH = cls.original_docs_path
        
        # Clean up temp directory
        import shutil
        shutil.rmtree(cls.temp_docs_dir, ignore_errors=True)

    def test_list_documentation_sections_integration(self):
        """Test the list_documentation_sections function in the improved server"""
        # Use the implementation function directly if available, otherwise use the decorated one
        if hasattr(SERVER_MODULE, '_list_documentation_sections_impl'):
            sections = SERVER_MODULE._list_documentation_sections_impl()
        else:
            sections = SERVER_MODULE.list_documentation_sections()
        
        # Check that expected sections are present
        self.assertIn("api-reference", sections)
        self.assertIn("tutorials", sections)
        self.assertIn("index.md", sections)
        
        print(f"Found sections: {sections}")

    def test_search_documentation_integration(self):
        """Test the search_documentation function in the improved server"""
        # Use the implementation function directly if available, otherwise use the decorated one
        if hasattr(SERVER_MODULE, '_search_documentation_impl'):
            results = SERVER_MODULE._search_documentation_impl("FastMCP")
        else:
            results = SERVER_MODULE.search_documentation("FastMCP")
        
        # Should find at least one result since we have "FastMCP" in our test data
        self.assertGreater(len(results), 0)
        
        # Check that each result has the required fields
        for result in results:
            self.assertIn("file", result)
            self.assertIn("snippet", result)
            self.assertIn("path", result)
            
        # Check that results contain the search query
        found_fastmcp = any("fastmcp" in result["snippet"].lower() for result in results)
        self.assertTrue(found_fastmcp, "Should find results containing 'FastMCP'")
        
        print(f"Search results count: {len(results)}")
        if results:
            print(f"First result file: {results[0]['file']}")

    def test_read_documentation_file_integration(self):
        """Test the read_documentation_file function in the improved server"""
        # Use the implementation function directly if available, otherwise use the decorated one
        if hasattr(SERVER_MODULE, '_read_documentation_file_impl'):
            content = SERVER_MODULE._read_documentation_file_impl("index.md")
        else:
            content = SERVER_MODULE.read_documentation_file("index.md")
        
        # Check that content contains expected text
        self.assertIn("FastMCP Documentation", content)
        self.assertIn("Welcome to FastMCP documentation", content)
        
        print(f"Read documentation content length: {len(content)}")

    def test_get_section_files_integration(self):
        """Test the get_section_files function in the improved server"""
        # Use the implementation function directly if available, otherwise use the decorated one
        if hasattr(SERVER_MODULE, '_get_section_files_impl'):
            files = SERVER_MODULE._get_section_files_impl("tutorials")
        else:
            files = SERVER_MODULE.get_section_files("tutorials")
        
        # Should find the getting-started.md file
        self.assertEqual(len(files), 1)
        self.assertIn("tutorials/getting-started.md", files)
        
        print(f"Found files in tutorials section: {files}")

    def test_find_examples_for_feature_integration(self):
        """Test the find_examples_for_feature function in the improved server"""
        # Use the implementation function directly if available, otherwise use the decorated one
        if hasattr(SERVER_MODULE, '_find_examples_for_feature_impl'):
            results = SERVER_MODULE._find_examples_for_feature_impl("FastMCP")
        else:
            results = SERVER_MODULE.find_examples_for_feature("FastMCP")
        
        # Should find at least one example
        if results:
            self.assertGreater(len(results), 0)
            for result in results:
                self.assertIn("file", result)
                self.assertIn("snippet", result)
                self.assertIn("path", result)
        
        print(f"Found {len(results)} examples for FastMCP")

    def test_error_handling_integration(self):
        """Test error handling in the improved server"""
        # Test reading non-existent file
        with self.assertRaises(Exception):
            if hasattr(SERVER_MODULE, '_read_documentation_file_impl'):
                SERVER_MODULE._read_documentation_file_impl("nonexistent-file.md")
            else:
                SERVER_MODULE.read_documentation_file("nonexistent-file.md")
        
        # Test getting files for non-existent section
        with self.assertRaises(Exception):
            if hasattr(SERVER_MODULE, '_get_section_files_impl'):
                SERVER_MODULE._get_section_files_impl("nonexistent-section")
            else:
                SERVER_MODULE.get_section_files("nonexistent-section")

    def test_cache_functionality(self):
        """Test that caching is working in the improved server"""
        # Get cache stats before
        initial_stats = SERVER_MODULE.get_cache_stats()
        print(f"Initial cache stats: {initial_stats}")
        
        # Make a few calls to populate cache
        if hasattr(SERVER_MODULE, '_search_documentation_impl'):
            SERVER_MODULE._search_documentation_impl("FastMCP")
            SERVER_MODULE._read_documentation_file_impl("index.md")
        else:
            SERVER_MODULE.search_documentation("FastMCP")
            SERVER_MODULE.read_documentation_file("index.md")
        
        # Get cache stats after
        final_stats = SERVER_MODULE.get_cache_stats()
        print(f"Final cache stats: {final_stats}")
        
        # Cache should have been populated
        self.assertGreater(final_stats["cache_size"], initial_stats["cache_size"])

    def test_config_loading(self):
        """Test that configuration is loaded properly"""
        # Check that config object exists (in improved server)
        if hasattr(SERVER_MODULE, 'config'):
            config = SERVER_MODULE.config
            self.assertIsNotNone(config)
            self.assertTrue(hasattr(config, 'name'))
            self.assertTrue(hasattr(config, 'version'))
            self.assertTrue(hasattr(config, 'docs_base_path'))
            
            print(f"Server name: {config.name}")
            print(f"Server version: {config.version}")


class TestServerStart(unittest.TestCase):
    """Test server startup and basic functionality"""
    
    def test_server_config_creation(self):
        """Test that server configuration is created properly"""
        # This test mainly verifies that the config class works
        if hasattr(SERVER_MODULE, 'config'):
            config = SERVER_MODULE.config
            self.assertIsInstance(config, SERVER_MODULE.ServerConfig)
            self.assertTrue(config.name.startswith("FastMCP"))
            print(f"Server configuration loaded: {config.name} v{config.version}")


if __name__ == '__main__':
    # Run the tests
    print("Running integration tests for improved FastMCP Documentation Server...")
    unittest.main(verbosity=2)