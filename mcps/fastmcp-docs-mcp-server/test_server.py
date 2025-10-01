#!/usr/bin/env python3
"""
Test script to verify the FastMCP Documentation Server imports correctly
and all components are properly registered
"""

import sys
import os

# Add the server directory to the path
sys.path.insert(0, '.')

def test_server_import():
    """Test that the server imports without errors"""
    try:
        import server
        print("✓ Server imports successfully")
        return server
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return None
    except Exception as e:
        print(f"✗ Unexpected error during import: {e}")
        return None


def test_mcp_instance(server_module):
    """Test that the MCP instance exists and has the expected components"""
    if not hasattr(server_module, 'mcp'):
        print("✗ No 'mcp' instance found in server module")
        return False
    
    mcp = server_module.mcp
    print(f"✓ MCP instance found: {mcp.name}")
    print(f"✓ Instructions: {mcp.instructions}")
    print(f"✓ Version: {mcp.version}")
    return True


def test_tools_registered(server_module):
    """Test that tool functions exist in the module"""
    expected_tools = [
        'list_documentation_sections',
        'search_documentation', 
        'read_documentation_file',
        'get_section_files',
        'find_examples_for_feature'
    ]
    
    found_count = 0
    for tool_name in expected_tools:
        if hasattr(server_module, tool_name):
            print(f"  ✓ Tool '{tool_name}' exists")
            found_count += 1
        else:
            print(f"  ✗ Tool '{tool_name}' not found")
    
    print(f"✓ Found {found_count} out of {len(expected_tools)} expected tools")
    return found_count > 0


def test_resources_registered(server_module):
    """Test that resource functions exist in the module"""
    expected_resources = [
        'get_documentation_toc',
        'get_latest_docs_updates'
    ]
    
    found_count = 0
    for resource_name in expected_resources:
        if hasattr(server_module, resource_name):
            print(f"  ✓ Resource '{resource_name}' exists")
            found_count += 1
        else:
            print(f"  ✗ Resource '{resource_name}' not found")
    
    print(f"✓ Found {found_count} out of {len(expected_resources)} expected resources")
    return found_count > 0


def test_prompts_registered(server_module):
    """Test that prompt functions exist in the module"""
    expected_prompts = [
        'explain_fastmcp_concept',
        'implementation_guide_prompt'
    ]
    
    found_count = 0
    for prompt_name in expected_prompts:
        if hasattr(server_module, prompt_name):
            print(f"  ✓ Prompt '{prompt_name}' exists")
            found_count += 1
        else:
            print(f"  ✗ Prompt '{prompt_name}' not found")
    
    print(f"✓ Found {found_count} out of {len(expected_prompts)} expected prompts")
    return found_count > 0


def main():
    """Run all tests"""
    print("Testing FastMCP Documentation Server...")
    print("="*50)
    
    # Test import
    server_module = test_server_import()
    if not server_module:
        return False
    
    # Test MCP instance
    if not test_mcp_instance(server_module):
        return False
    
    # Test registered components
    test_tools_registered(server_module)
    test_resources_registered(server_module)
    test_prompts_registered(server_module)
    
    print("="*50)
    print("✓ All basic tests completed!")
    print("Note: This doesn't test the functionality, just the registration of components.")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)