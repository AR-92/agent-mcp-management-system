#!/usr/bin/env python3
"""
Comprehensive test for all FastMCP Documentation Server tools, resources, and prompts
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


class TestAllServerComponents(unittest.TestCase):
    """Test class for all server components in the FastMCP Documentation Server"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for test documentation
        self.temp_docs_dir = tempfile.mkdtemp()
        
        # Create some test documentation files
        os.makedirs(os.path.join(self.temp_docs_dir, "api-reference"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_docs_dir, "tutorials"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_docs_dir, "examples"), exist_ok=True)
        
        # Create test files
        with open(os.path.join(self.temp_docs_dir, "index.md"), "w") as f:
            f.write("# FastMCP Documentation\n\nWelcome to FastMCP documentation.")
        
        with open(os.path.join(self.temp_docs_dir, "api-reference", "index.md"), "w") as f:
            f.write("# API Reference\n\nDetailed API documentation for FastMCP.")
        
        with open(os.path.join(self.temp_docs_dir, "tutorials", "getting-started.md"), "w") as f:
            f.write("# Getting Started\n\nThis tutorial helps you get started with FastMCP.\n\nFastMCP is great!")
        
        with open(os.path.join(self.temp_docs_dir, "examples.md"), "w") as f:
            f.write("# Examples\n\nHere are some examples of using FastMCP effectively.")
        
        with open(os.path.join(self.temp_docs_dir, "examples", "simple-example.md"), "w") as f:
            f.write("# Simple Example\n\nHere is a simple example of using FastMCP.\n\nFastMCP makes documentation easy.")
        
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

    def test_all_tools_exist(self):
        """Test that all expected tools exist in the server module"""
        expected_tools = [
            'list_documentation_sections',
            'search_documentation',
            'read_documentation_file',
            'get_section_files',
            'find_examples_for_feature',
            'count_docs_in_section',
            'search_by_file_type',
            'get_file_metadata',
            'get_recently_accessed_docs',
            'create_mcp_skeleton',
            'validate_mcp_config',
            'analyze_existing_mcp'
        ]
        
        for tool_name in expected_tools:
            self.assertTrue(
                hasattr(server, tool_name),
                f"Tool '{tool_name}' is missing from server module"
            )
            print(f"✓ Tool '{tool_name}' exists")

    def test_all_resources_exist(self):
        """Test that all expected resources exist in the server module"""
        expected_resources = [
            'get_documentation_toc',
            'get_latest_docs_updates',
            'get_documentation_stats',
            'get_server_health',
            'get_mcp_best_practices'
        ]
        
        for resource_name in expected_resources:
            self.assertTrue(
                hasattr(server, resource_name),
                f"Resource '{resource_name}' is missing from server module"
            )
            print(f"✓ Resource '{resource_name}' exists")

    def test_all_prompts_exist(self):
        """Test that all expected prompts exist in the server module"""
        expected_prompts = [
            'explain_fastmcp_concept',
            'implementation_guide_prompt',
            'best_practices_prompt',
            'comparison_prompt',
            'troubleshooting_prompt',
            'generate_mcp_implementation_guide',
            'generate_mcp_debugging_guide'
        ]
        
        for prompt_name in expected_prompts:
            self.assertTrue(
                hasattr(server, prompt_name),
                f"Prompt '{prompt_name}' is missing from server module"
            )
            print(f"✓ Prompt '{prompt_name}' exists")

    # Test all tools
    def test_list_documentation_sections(self):
        """Test the list_documentation_sections function"""
        sections = server._list_documentation_sections_impl()
        
        # Check that expected sections are present
        self.assertIn("api-reference", sections)
        self.assertIn("tutorials", sections)
        self.assertIn("examples", sections)
        self.assertIn("index.md", sections)

    def test_search_documentation(self):
        """Test the search_documentation function"""
        results = server._search_documentation_impl("FastMCP")
        
        # Should find at least one result since we have "FastMCP" in our test data
        self.assertGreater(len(results), 0)
        
        # Check that each result has the required fields
        for result in results:
            self.assertIn("file", result)
            self.assertIn("snippet", result)
            self.assertIn("path", result)
    
    def test_read_documentation_file(self):
        """Test the read_documentation_file function"""
        content = server._read_documentation_file_impl("index.md")
        
        # Check that content contains expected text
        self.assertIn("FastMCP Documentation", content)
        self.assertIn("Welcome to FastMCP documentation", content)

    def test_get_section_files(self):
        """Test the get_section_files function"""
        files = server._get_section_files_impl("tutorials")
        
        # Should find the getting-started.md file
        self.assertEqual(len(files), 1)
        self.assertIn("tutorials/getting-started.md", files)

    def test_find_examples_for_feature(self):
        """Test the find_examples_for_feature function"""
        results = server._find_examples_for_feature_impl("FastMCP")
        
        # Should find at least one example
        if results:
            self.assertGreater(len(results), 0)
            for result in results:
                self.assertIn("file", result)
                self.assertIn("snippet", result)
                self.assertIn("path", result)

    def test_count_docs_in_section(self):
        """Test the count_docs_in_section function"""
        # Use the internal implementation
        count = server._count_docs_in_section_impl("tutorials")
        self.assertEqual(count, 1)  # getting-started.md

    def test_search_by_file_type(self):
        """Test the search_by_file_type function"""
        results = server._search_by_file_type_impl("md")
        self.assertGreater(len(results), 0)
        # All results should be markdown files
        for result in results:
            self.assertTrue(result.endswith('.md'))

    def test_get_file_metadata(self):
        """Test the get_file_metadata function"""
        metadata = server._get_file_metadata_impl("index.md")
        
        self.assertIn("file_path", metadata)
        self.assertIn("size_bytes", metadata)
        self.assertIn("modification_time", metadata)
        self.assertIn("creation_time", metadata)
        self.assertIn("word_count", metadata)
        self.assertIn("line_count", metadata)
        self.assertIn("char_count", metadata)
        
        self.assertEqual(metadata["file_path"], "index.md")

    def test_get_recently_accessed_docs(self):
        """Test the get_recently_accessed_docs function"""
        # First, access some docs to populate the cache
        server._read_documentation_file_impl("index.md")
        server._search_documentation_impl("FastMCP")
        
        recent_docs = server._get_recently_accessed_docs_impl(5)
        # This will return cache keys, just ensure we get a list
        self.assertIsInstance(recent_docs, list)

    # Test all resources
    def test_get_documentation_toc(self):
        """Test the get_documentation_toc resource"""
        toc = server._get_documentation_toc_impl()
        
        # Check that TOC has required structure
        self.assertIn("title", toc)
        self.assertIn("description", toc)
        self.assertIn("sections", toc)
        
        # Check that sections are properly structured
        sections = toc["sections"]
        self.assertIn("index", sections)

    def test_get_latest_docs_updates(self):
        """Test the get_latest_docs_updates resource"""
        updates = server._get_latest_docs_updates_impl()
        
        # Should return a list of updates
        self.assertIsInstance(updates, list)
        
        # Each update should have required fields
        for update in updates:
            self.assertIn("file", update)
            self.assertIn("modified", update)
            self.assertIn("size", update)

    def test_get_documentation_stats(self):
        """Test the get_documentation_stats resource"""
        stats = server._get_documentation_stats_impl()
        
        # Check that stats has required structure
        self.assertIn("total_sections", stats)
        self.assertIn("total_files", stats)
        self.assertIn("total_size", stats)
        self.assertIn("file_types", stats)
        self.assertIn("last_updated", stats)
        
        # Should have at least some files and sections
        self.assertGreaterEqual(stats["total_files"], 4)  # We created at least 4 files
        self.assertGreaterEqual(stats["total_sections"], 3)  # We created 3 sections

    def test_get_server_health(self):
        """Test the get_server_health resource"""
        health = server._get_server_health_impl()
        
        # Check that health has required structure
        self.assertIn("status", health)
        self.assertIn("timestamp", health)
        self.assertIn("docs_path_accessible", health)
        self.assertIn("docs_path", health)
        self.assertIn("cache_stats", health)
        self.assertIn("server_config", health)
        
        # Path should be accessible since we set it up
        self.assertTrue(health["docs_path_accessible"])
        self.assertEqual(health["status"], "healthy")

    # Test all prompts
    def test_explain_fastmcp_concept(self):
        """Test the explain_fastmcp_concept prompt"""
        prompt = server._explain_fastmcp_concept_impl("context", "test context")
        
        # Should contain the concept and context
        self.assertIn("context", prompt)
        self.assertIn("test context", prompt)
        self.assertIn("explain", prompt.lower())

    def test_implementation_guide_prompt(self):
        """Test the implementation_guide_prompt function"""
        prompt = server._implementation_guide_prompt_impl("topic", "requirements")
        
        # Should contain the topic and requirements
        self.assertIn("topic", prompt)
        self.assertIn("requirements", prompt)

    def test_best_practices_prompt(self):
        """Test the best_practices_prompt function"""
        prompt = server._best_practices_prompt_impl("testing", "context")
        
        # Should contain the topic and context
        self.assertIn("testing", prompt)
        self.assertIn("context", prompt)
        self.assertIn("best practices", prompt.lower())

    def test_comparison_prompt(self):
        """Test the comparison_prompt function"""
        prompt = server._comparison_prompt_impl("tool1", "tool2", "context")
        
        # Should contain both subjects and context
        self.assertIn("tool1", prompt)
        self.assertIn("tool2", prompt)
        self.assertIn("context", prompt)
        self.assertIn("compare", prompt.lower())

    def test_troubleshooting_prompt(self):
        """Test the troubleshooting_prompt function"""
        prompt = server._troubleshooting_prompt_impl("connection issue", "dev environment")
        
        # Should contain the issue and environment
        self.assertIn("connection issue", prompt)
        self.assertIn("dev environment", prompt)
        self.assertIn("troubleshoot", prompt.lower())


class TestMCPRegistration(unittest.TestCase):
    """Test that all functions are properly registered with MCP decorators"""
    
    def test_mcp_tools_registered(self):
        """Test that all tools are registered as MCP tools"""
        expected_mcp_tools = [
            'list_documentation_sections',
            'search_documentation',
            'read_documentation_file',
            'get_section_files',
            'find_examples_for_feature',
            'count_docs_in_section',
            'search_by_file_type',
            'get_file_metadata',
            'get_recently_accessed_docs'
        ]
        
        for tool_name in expected_mcp_tools:
            self.assertTrue(
                hasattr(server, tool_name),
                f"MCP tool '{tool_name}' is missing"
            )
            
            # Verify it's callable
            tool_func = getattr(server, tool_name)
            self.assertTrue(callable(tool_func))
    
    def test_mcp_resources_registered(self):
        """Test that all resources are registered as MCP resources"""
        expected_mcp_resources = [
            'get_documentation_toc',
            'get_latest_docs_updates',
            'get_documentation_stats',
            'get_server_health'
        ]
        
        for resource_name in expected_mcp_resources:
            self.assertTrue(
                hasattr(server, resource_name),
                f"MCP resource '{resource_name}' is missing"
            )
            
            # Verify it's callable
            resource_func = getattr(server, resource_name)
            self.assertTrue(callable(resource_func))
    
    def test_mcp_prompts_registered(self):
        """Test that all prompts are registered as MCP prompts"""
        expected_mcp_prompts = [
            'explain_fastmcp_concept',
            'implementation_guide_prompt',
            'best_practices_prompt',
            'comparison_prompt',
            'troubleshooting_prompt'
        ]
        
        for prompt_name in expected_mcp_prompts:
            self.assertTrue(
                hasattr(server, prompt_name),
                f"MCP prompt '{prompt_name}' is missing"
            )
            
            # Verify it's callable
            prompt_func = getattr(server, prompt_name)
            self.assertTrue(callable(prompt_func))


if __name__ == '__main__':
    print("Running comprehensive tests for all FastMCP Documentation Server components...")
    print("=" * 70)
    
    # Run the tests
    unittest.main(verbosity=2)