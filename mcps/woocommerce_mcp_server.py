#!/usr/bin/env python3
"""
WooCommerce MCP Server

Provides access to WooCommerce functionality for LLMs through MCP protocol.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any
import asyncio


# Initialize the MCP server
mcp = FastMCP(
    name="WooCommerce MCP Server",
    instructions="Provides access to WooCommerce functionality including product management, order processing, and store operations",
    version="1.0.0"
)


# Tools
@mcp.tool
def list_products(
    status: str = "publish", 
    limit: int = 20, 
    offset: int = 0,
    category: str = None
) -> List[Dict[str, Any]]:
    """
    List products in the WooCommerce store
    """
    # This would connect to WooCommerce API in a real implementation
    return [
        {
            "id": f"prod_{i}",
            "name": f"Product {i}",
            "slug": f"product-{i}",
            "type": "simple",
            "status": status,
            "price": f"{29.99 + i * 5.00}",
            "regular_price": f"{39.99 + i * 5.00}",
            "description": f"Description for product {i}",
            "short_description": f"Short desc for product {i}",
            "sku": f"SKU-{i:04d}",
            "stock_quantity": 100 - i * 2,
            "manage_stock": True,
            "categories": [{"id": 1, "name": "Uncategorized"}],
            "images": [{"src": f"https://example.com/images/prod_{i}.jpg"}]
        }
        for i in range(limit)
    ]


@mcp.tool
def get_product(product_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific product
    """
    return {
        "id": product_id,
        "name": f"Product {product_id}",
        "slug": f"product-{product_id}",
        "type": "simple",
        "status": "publish",
        "price": "29.99",
        "regular_price": "39.99",
        "description": f"Detailed description for product {product_id}",
        "short_description": f"Short description for product {product_id}",
        "sku": f"SKU-{product_id[-4:]}",
        "stock_quantity": 150,
        "manage_stock": True,
        "categories": [{"id": 1, "name": "Uncategorized"}],
        "images": [{"src": f"https://example.com/images/{product_id}.jpg"}],
        "date_created": "2023-01-01T10:00:00Z",
        "date_modified": "2023-01-15T15:30:00Z"
    }


@mcp.tool
def create_product(
    name: str, 
    description: str, 
    price: float, 
    regular_price: float = None,
    sku: str = None,
    stock_quantity: int = 0,
    categories: List[str] = None
) -> Dict[str, Any]:
    """
    Create a new product in the WooCommerce store
    """
    if regular_price is None:
        regular_price = price * 1.2
    
    return {
        "status": "created",
        "product_id": "new_prod_id",
        "message": f"Product '{name}' created successfully",
        "url": f"https://example.com/product/{name.lower().replace(' ', '-')}"
    }


@mcp.tool
def update_product(
    product_id: str,
    name: str = None,
    description: str = None,
    price: float = None,
    stock_quantity: int = None
) -> Dict[str, str]:
    """
    Update an existing product in the WooCommerce store
    """
    return {
        "status": "updated",
        "message": f"Product {product_id} updated successfully"
    }


@mcp.tool
def list_orders(
    status: str = "any", 
    limit: int = 20, 
    offset: int = 0,
    date_after: str = None
) -> List[Dict[str, Any]]:
    """
    List orders in the WooCommerce store
    """
    return [
        {
            "id": f"order_{i}",
            "status": "completed" if i % 3 != 0 else "processing",
            "customer_id": f"cust_{i % 5}",
            "date_created": f"2023-01-{10+i:02d}T09:30:00Z",
            "total": f"{99.99 + i * 10.00}",
            "currency": "USD",
            "customer_name": f"Customer {i}",
            "customer_email": f"customer{i}@example.com",
            "line_items": [
                {
                    "id": 1,
                    "name": f"Product {i}",
                    "product_id": f"prod_{i}",
                    "quantity": 1,
                    "total": f"{99.99 + i * 10.00}"
                }
            ]
        }
        for i in range(limit)
    ]


@mcp.tool
def get_order(order_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific order
    """
    return {
        "id": order_id,
        "status": "processing",
        "customer_id": "cust_1",
        "date_created": "2023-01-15T10:30:00Z",
        "total": "149.99",
        "currency": "USD",
        "customer_name": "John Doe",
        "customer_email": "john.doe@example.com",
        "billing": {
            "first_name": "John",
            "last_name": "Doe",
            "address_1": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "postcode": "12345",
            "country": "US",
            "email": "john.doe@example.com",
            "phone": "(555) 123-4567"
        },
        "shipping": {
            "first_name": "John",
            "last_name": "Doe",
            "address_1": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "postcode": "12345",
            "country": "US"
        },
        "line_items": [
            {
                "id": 1,
                "name": "Premium Product",
                "product_id": "prod_1",
                "quantity": 1,
                "total": "149.99"
            }
        ]
    }


@mcp.tool
def create_order(
    customer_id: str,
    line_items: List[Dict[str, Any]],
    billing_info: Dict[str, str],
    shipping_info: Dict[str, str] = None
) -> Dict[str, Any]:
    """
    Create a new order in WooCommerce
    """
    return {
        "status": "created",
        "order_id": "new_order_id",
        "message": "Order created successfully",
        "total": "149.99"
    }


@mcp.tool
def search_products(query: str) -> List[Dict[str, Any]]:
    """
    Search for products in the WooCommerce store
    """
    return [
        {
            "id": f"search_result_{i}",
            "name": f"Search result {i} for '{query}'",
            "slug": f"search-result-{i}-{query.replace(' ', '-')}",
            "price": f"{19.99 + i * 5.00}",
            "sku": f"SR-{query[:3]}-{i:03d}",
            "categories": [{"id": 1, "name": "Search Results"}]
        }
        for i in range(10)
    ]


@mcp.tool
def get_store_stats() -> Dict[str, Any]:
    """
    Get overall store statistics
    """
    return {
        "total_sales": 24567.89,
        "total_orders": 125,
        "total_customers": 89,
        "average_order_value": 196.54,
        "date_range": "2023-01-01 to 2023-01-31"
    }


# Resources
@mcp.resource("http://woocommerce-mcp-server.local/status")
def get_woocommerce_status() -> Dict[str, Any]:
    """
    Get the status of the WooCommerce MCP server
    """
    return {
        "status": "connected",
        "store_url": "https://example.com",
        "server_time": asyncio.get_event_loop().time(),
        "connected": True,
        "woocommerce_version": "7.0.0",
        "api_version": "wc/v3"
    }


@mcp.resource("http://woocommerce-mcp-server.local/settings")
def get_store_settings() -> Dict[str, Any]:
    """
    Get WooCommerce store settings
    """
    return {
        "store_name": "Example Store",
        "store_description": "This is an example WooCommerce store",
        "currency": "USD",
        "currency_symbol": "$",
        "weight_unit": "kg",
        "dimension_unit": "cm",
        "base_location": "US",
        "default_customer_address": "base",
        "enable_reviews": True,
        "enable_coupons": True
    }


@mcp.resource("http://woocommerce-mcp-server.local/payment-methods")
def get_payment_methods() -> List[Dict[str, str]]:
    """
    Get available payment methods
    """
    return [
        {"id": "bacs", "title": "Direct bank transfer", "enabled": True},
        {"id": "cheque", "title": "Check payments", "enabled": False},
        {"id": "cod", "title": "Cash on delivery", "enabled": True},
        {"id": "paypal", "title": "PayPal", "enabled": True}
    ]


# Prompts
@mcp.prompt("/woocommerce-product-description")
def product_description_prompt(
    product_name: str, 
    product_category: str,
    target_audience: str,
    context: str = ""
) -> str:
    """
    Generate a prompt for creating a product description
    """
    return f"""
Create a compelling product description for: {product_name}
Category: {product_category}
Target Audience: {target_audience}
Context: {context}

Focus on benefits, features, and why the customer should buy this product.
"""


@mcp.prompt("/woocommerce-marketing-email")
def marketing_email_prompt(
    product_ids: List[str], 
    email_type: str,
    target_segment: str,
    context: str = ""
) -> str:
    """
    Generate a prompt for creating a marketing email
    """
    return f"""
Create a marketing email for products: {product_ids}
Type: {email_type} (e.g., promotional, new arrival, abandoned cart)
Target Segment: {target_segment}
Context: {context}

Include compelling subject line, body content, and call-to-action.
"""


@mcp.prompt("/woocommerce-inventory-plan")
def inventory_plan_prompt(
    category: str, 
    seasonality: str,
    sales_velocity: str,
    context: str = ""
) -> str:
    """
    Generate a prompt for planning inventory
    """
    return f"""
Plan inventory for category: {category}
Seasonality: {seasonality}
Sales Velocity: {sales_velocity}
Context: {context}

Consider reorder points, seasonal demand, and storage constraints.
"""


@mcp.prompt("/woocommerce-sales-analysis")
def sales_analysis_prompt(
    time_period: str, 
    metrics: List[str],
    context: str = ""
) -> str:
    """
    Generate a prompt for analyzing WooCommerce sales
    """
    return f"""
Analyze WooCommerce sales for: {time_period}
Metrics: {metrics}
Context: {context}

Identify trends, best-selling products, customer behavior, and optimization opportunities.
"""


if __name__ == "__main__":
    # Use stdio transport for MCP server (proper MCP protocol communication)
    asyncio.run(mcp.run_stdio_async())