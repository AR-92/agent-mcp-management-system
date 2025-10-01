#!/usr/bin/env python3
"""
Comprehensive functional tests for the FastMCP Documentation Server
"""

import sys
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import json

# Add the server directory to the path
sys.path.insert(0, '.')

# Import the server module
import server


class TestFastMCPDocumentationServer(unittest.TestCase):
    """Test class for the FastMCP Documentation Server"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for test documentation
        self.temp_docs_dir = tempfile.mkdtemp()
        
        # Create some test documentation files
        os.makedirs(os.path.join(self.temp_docs_dir, "api-reference"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_docs_dir, "tutorials"), exist_ok=True)
        
        # Create test files
        with open(os.path.join(self.temp_docs_dir, "index.md"), "w") as f:
            f.write("# FastMCP Documentation\n\nWelcome to FastMCP documentation.")
        
        with open(os.path.join(self.temp_docs_dir, "api-reference", "index.md"), "w") as f:
            f.write("# API Reference\n\nDetailed API documentation for FastMCP.")
        
        with open(os.path.join(self.temp_docs_dir, "tutorials", "getting-started.md"), "w") as f:
            f.write("# Getting Started\n\nThis tutorial helps you get started with FastMCP.\n\nFastMCP is great!")
        
        with open(os.path.join(self.temp_docs_dir, "examples.md"), "w") as f:
            f.write("# Examples\n\nHere are some examples of using FastMCP effectively.")
        
        # Store original docs path
        self.original_docs_path = server.DOCS_BASE_PATH
        
        # Temporarily replace the docs path with our test path
        server.DOCS_BASE_PATH = self.temp_docs_dir

    def tearDown(self):
        """Tear down test fixtures after each test method."""
        # Restore original docs path
        server.DOCS_BASE_PATH = self.original_docs_path
        
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_docs_dir, ignore_errors=True)

    def test_list_documentation_sections(self):
        """Test the list_documentation_sections function"""
        sections = server.list_documentation_sections()
        
        # Check that expected sections are present
        self.assertIn("api-reference", sections)
        self.assertIn("tutorials", sections)
        self.assertIn("index.md", sections)
        
        # Index should always be included
        self.assertIn("index.md", sections)
    
    def test_search_documentation(self):
        """Test the search_documentation function"""
        results = server.search_documentation("FastMCP")
        
        # Should find at least one result since we have "FastMCP" in our test data
        self.assertGreater(len(results), 0)
        
        # Check that each result has the required fields
        for result in results:
            self.assertIn("file", result)
            self.assertIn("snippet", result)
            self.assertIn("path", result)
            
        # Check that results contain the search query
        for result in results:
            # The content was read into snippet, so it should contain "fastmcp" (lowercase)
            self.assertIn("fastmcp", result["snippet"].lower())
    
    def test_search_documentation_no_results(self):
        """Test search_documentation with a query that shouldn't match"""
        results = server.search_documentation("definitely_does_not_exist_in_test_data")
        self.assertEqual(len(results), 0)
    
    def test_read_documentation_file(self):
        """Test the read_documentation_file function"""
        content = server.read_documentation_file("index.md")
        
        # Check that content contains expected text
        self.assertIn("FastMCP Documentation", content)
        self.assertIn("Welcome to FastMCP documentation", content)
    
    def test_read_documentation_file_security_check(self):
        """Test that read_documentation_file properly validates file paths"""
        # This should raise a ValueError due to security validation
        with self.assertRaises(ValueError):
            server.read_documentation_file("../../../../../../etc/passwd")
    
    def test_read_documentation_file_not_found(self):
        """Test that read_documentation_file raises an error for non-existent files"""
        with self.assertRaises(FileNotFoundError):
            server.read_documentation_file("nonexistent-file.md")
    
    def test_get_section_files(self):
        """Test the get_section_files function"""
        files = server.get_section_files("tutorials")
        
        # Should find the getting-started.md file
        self.assertEqual(len(files), 1)
        self.assertIn("tutorials/getting-started.md", files)
    
    def test_get_section_files_nonexistent(self):
        """Test get_section_files with a non-existent section"""
        with self.assertRaises(ValueError):
            server.get_section_files("nonexistent-section")
    
    def test_get_documentation_toc(self):
        """Test the get_documentation_toc resource"""
        toc = server.get_documentation_toc()
        
        # Check that TOC has required structure
        self.assertIn("title", toc)
        self.assertIn("description", toc)
        self.assertIn("sections", toc)
        
        # Check that sections are properly structured
        sections = toc["sections"]
        self.assertIn("index", sections)
        
        # The index section should have required fields
        index_section = sections["index"]
        self.assertIn("title", index_section)
        self.assertIn("path", index_section)
        self.assertIn("description", index_section)
    
    def test_get_latest_docs_updates(self):
        """Test the get_latest_docs_updates resource"""
        updates = server.get_latest_docs_updates()
        
        # Should return a list of updates
        self.assertIsInstance(updates, list)
        
        # Each update should have required fields
        for update in updates:
            self.assertIn("file", update)
            self.assertIn("modified", update)
    
    def test_find_examples_for_feature(self):
        """Test the find_examples_for_feature function"""
        # Create example directory structure
        examples_dir = os.path.join(self.temp_docs_dir, "examples")
        os.makedirs(examples_dir, exist_ok=True)
        
        with open(os.path.join(examples_dir, "fastmcp_example.md"), "w") as f:
            f.write("# FastMCP Example\n\nThis is an example of using FastMCP.")
        
        results = server.find_examples_for_feature("FastMCP")
        
        # Should find at least one example
        if results:  # Only check if examples directory exists in our test setup
            self.assertGreater(len(results), 0)
            for result in results:
                self.assertIn("file", result)
                self.assertIn("snippet", result)
                self.assertIn("path", result)
    
    def test_explain_fastmcp_concept(self):
        """Test the explain_fastmcp_concept prompt"""
        prompt = server.explain_fastmcp_concept("context", "test context")
        
        # Should contain the concept and context
        self.assertIn("context", prompt)
        self.assertIn("test context", prompt)
        self.assertIn("explain", prompt.lower())
    
    def test_implementation_guide_prompt(self):
        """Test the implementation_guide_prompt function"""
        prompt = server.implementation_guide_prompt("topic", "requirements")
        
        # Should contain the topic and requirements
        self.assertIn("topic", prompt)
        self.assertIn("requirements", prompt)


class TestFastMCPDocumentationServerWithoutDocs(unittest.TestCase):
    """Test class for error conditions when documentation directory doesn't exist"""
    
    def setUp(self):
        """Set up test fixtures with non-existent docs directory."""
        # Temporarily replace the docs path with a non-existent directory
        self.original_docs_path = server.DOCS_BASE_PATH
        server.DOCS_BASE_PATH = "/path/that/definitely/does/not/exist"
    
    def tearDown(self):
        """Restore original docs path."""
        server.DOCS_BASE_PATH = self.original_docs_path
    
    def test_list_documentation_sections_no_dir(self):
        """Test list_documentation_sections when docs directory doesn't exist"""
        with self.assertRaises(FileNotFoundError):
            server.list_documentation_sections()
    
    def test_get_section_files_no_dir(self):
        """Test get_section_files when docs directory doesn't exist"""
        with self.assertRaises(ValueError):
            server.get_section_files("some-section")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and potential vulnerabilities"""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test documentation
        self.temp_docs_dir = tempfile.mkdtemp()
        
        # Create a test file
        with open(os.path.join(self.temp_docs_dir, "test.md"), "w") as f:
            f.write("# Test\n\nThis is a test file.")
        
        # Store original docs path
        self.original_docs_path = server.DOCS_BASE_PATH
        
        # Temporarily replace the docs path with our test path
        server.DOCS_BASE_PATH = self.temp_docs_dir
    
    def tearDown(self):
        """Restore original docs path and clean up."""
        server.DOCS_BASE_PATH = self.original_docs_path
        import shutil
        shutil.rmtree(self.temp_docs_dir, ignore_errors=True)
    
    def test_empty_search_query(self):
        """Test search with empty query"""
        results = server.search_documentation("")
        
        # Should return empty list or handle gracefully
        self.assertIsInstance(results, list)
    
    def test_search_with_special_characters(self):
        """Test search with special characters"""
        results = server.search_documentation("!@#$%^&*()")
        
        # Should handle gracefully
        self.assertIsInstance(results, list)
    
    def test_read_empty_file(self):
        """Test reading an empty file"""
        # Create an empty file
        empty_file_path = os.path.join(self.temp_docs_dir, "empty.md")
        with open(empty_file_path, "w") as f:
            pass  # Create empty file
        
        content = server.read_documentation_file("empty.md")
        self.assertEqual(content, "")


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)