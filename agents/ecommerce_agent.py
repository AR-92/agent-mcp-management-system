"""
E-commerce Operations Agent using Strands Agents SDK

This agent uses the WooCommerce MCP to manage online store operations.
"""

from strandsagents import Agent
from typing import Dict, Any, List
import json
from datetime import datetime


def list_store_products(
    status: str = "publish", 
    limit: int = 20, 
    offset: int = 0,
    category: str = None
) -> List[Dict[str, Any]]:
    """
    List products in the WooCommerce store.
    
    Args:
        status: Status of products to list (publish, draft, pending, etc.)
        limit: Maximum number of products to return
        offset: Offset for pagination
        category: Optional category to filter by
        
    Returns:
        List of dictionaries containing product information
    """
    # This would connect to the WooCommerce MCP server in a real implementation
    return [
        {
            "id": f"prod_{i}",
            "name": f"Product {i}",
            "slug": f"product-{i}",
            "price": f"{25.99 + (i * 5.00):.2f}",
            "regular_price": f"{29.99 + (i * 5.00):.2f}",
            "status": "publish",
            "stock_quantity": 100 - (i * 5),
            "categories": [{"id": 1, "name": "Uncategorized"}],
            "date_created": (datetime.now() - timedelta(days=i*2)).isoformat(),
            "featured": i == 1
        }
        for i in range(1 + offset, limit + 1 + offset)
    ]


def get_product_details(product_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific product.
    
    Args:
        product_id: ID of the product to get details for
        
    Returns:
        Dictionary containing detailed product information
    """
    # This would connect to the WooCommerce MCP server in a real implementation
    return {
        "id": product_id,
        "name": f"Product {product_id}",
        "slug": f"product-{product_id}",
        "permalink": f"https://example.com/product/{product_id}",
        "date_created": (datetime.now() - timedelta(days=5)).isoformat(),
        "date_modified": datetime.now().isoformat(),
        "type": "simple",
        "status": "publish",
        "featured": False,
        "catalog_visibility": "visible",
        "description": f"Description for product {product_id}",
        "short_description": f"Short description for product {product_id}",
        "sku": f"SKU-{product_id}",
        "price": "29.99",
        "regular_price": "34.99",
        "sale_price": "",
        "date_on_sale_from": "",
        "date_on_sale_to": "",
        "on_sale": False,
        "total_sales": 150,
        "virtual": False,
        "downloadable": False,
        "downloads": [],
        "download_limit": -1,
        "download_expiry": -1,
        "external_url": "",
        "button_text": "",
        "tax_status": "taxable",
        "tax_class": "",
        "manage_stock": True,
        "stock_quantity": 50,
        "stock_status": "instock",
        "backorders": "no",
        "backorders_allowed": False,
        "backordered": False,
        "sold_individually": False,
        "weight": "1.5",
        "dimensions": {
            "length": "10",
            "width": "8",
            "height": "6"
        },
        "shipping_class": "",
        "shipping_class_id": 0,
        "reviews_allowed": True,
        "average_rating": "4.5",
        "rating_count": 25,
        "related_ids": [26, 27, 28, 29, 30],
        "upsell_ids": [],
        "cross_sell_ids": [],
        "parent_id": 0,
        "purchase_note": "",
        "categories": [
            {
                "id": 9,
                "name": "Clothing",
                "slug": "clothing"
            }
        ],
        "tags": [],
        "images": [
            {
                "id": 70,
                "date_created": "2023-01-10T15:21:39",
                "date_created_gmt": "2023-01-10T15:21:39",
                "date_modified": "2023-01-10T15:21:39",
                "date_modified_gmt": "2023-01-10T15:21:39",
                "src": "https://example.com/image.jpg",
                "name": "Image",
                "alt": "Image"
            }
        ],
        "attributes": [],
        "default_attributes": [],
        "variations": [],
        "grouped_products": [],
        "menu_order": 0,
        "meta_data": [],
        "brands": []
    }


def create_order(
    customer_id: str,
    line_items: List[Dict[str, Any]],
    billing_address: Dict[str, str],
    shipping_address: Dict[str, str],
    payment_method: str = "stripe",
    status: str = "pending"
) -> Dict[str, Any]:
    """
    Create a new order in the WooCommerce store.
    
    Args:
        customer_id: ID of the customer placing the order
        line_items: List of items in the order with product_id and quantity
        billing_address: Billing address information
        shipping_address: Shipping address information
        payment_method: Payment method for the order
        status: Initial status of the order
        
    Returns:
        Dictionary containing the created order information
    """
    # This would connect to the WooCommerce MCP server in a real implementation
    total = sum(item['quantity'] * float(item.get('price', 10)) for item in line_items)
    return {
        "status": "created",
        "order_id": f"order_{customer_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "customer_id": customer_id,
        "line_items": line_items,
        "total": f"{total:.2f}",
        "payment_method": payment_method,
        "status": status,
        "date_created": datetime.now().isoformat()
    }


def list_store_orders(
    status: str = "any", 
    limit: int = 20, 
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    List orders in the WooCommerce store.
    
    Args:
        status: Status of orders to list (any, pending, processing, completed, etc.)
        limit: Maximum number of orders to return
        offset: Offset for pagination
        
    Returns:
        List of dictionaries containing order information
    """
    # This would connect to the WooCommerce MCP server in a real implementation
    return [
        {
            "id": f"order_{i}",
            "status": "completed" if i % 4 == 0 else "processing" if i % 4 == 1 else "pending",
            "customer_id": f"cust_{i % 10}",
            "date_created": (datetime.now() - timedelta(days=i)).isoformat(),
            "total": f"{99.99 + (i * 10.00):.2f}",
            "currency": "USD",
            "payment_method": "stripe",
            "billing": {
                "first_name": f"Customer {i}",
                "last_name": f"LastName {i}",
                "address_1": f"{i*100} Main St",
                "city": "City",
                "state": "ST",
                "postcode": "12345",
                "country": "US",
                "email": f"customer{i}@example.com",
                "phone": "+1-555-000-0000"
            },
            "shipping": {
                "first_name": f"Customer {i}",
                "last_name": f"LastName {i}",
                "address_1": f"{i*100} Main St",
                "city": "City",
                "state": "ST",
                "postcode": "12345",
                "country": "US"
            }
        }
        for i in range(1 + offset, limit + 1 + offset)
    ]


def update_product_inventory(
    product_id: str, 
    stock_quantity: int, 
    operation: str = "set"
) -> Dict[str, Any]:
    """
    Update inventory for a specific product.
    
    Args:
        product_id: ID of the product to update
        stock_quantity: New stock quantity or quantity to add/subtract
        operation: Operation to perform ('set', 'add', 'subtract')
        
    Returns:
        Dictionary containing the inventory update result
    """
    # This would connect to the WooCommerce MCP server in a real implementation
    return {
        "status": "updated",
        "product_id": product_id,
        "new_stock_quantity": stock_quantity,
        "operation": operation,
        "timestamp": datetime.now().isoformat()
    }


def get_store_analytics(
    period: str = "month",
    start_date: str = None,
    end_date: str = None
) -> Dict[str, Any]:
    """
    Get store analytics and performance metrics.
    
    Args:
        period: Time period for analytics ('day', 'week', 'month', 'year')
        start_date: Start date for custom period
        end_date: End date for custom period
        
    Returns:
        Dictionary containing store analytics
    """
    # This would connect to the WooCommerce MCP server in a real implementation
    return {
        "period": period,
        "start_date": start_date or (datetime.now() - timedelta(days=30)).isoformat(),
        "end_date": end_date or datetime.now().isoformat(),
        "metrics": {
            "total_sales": 12450.75,
            "orders_count": 87,
            "average_order_value": 143.11,
            "conversion_rate": 2.3,
            "unique_visitors": 3421,
            "items_sold": 156
        }
    }


# Create an e-commerce operations agent
agent = Agent(
    system_prompt="You are an e-commerce operations assistant for WooCommerce stores. You can list and manage products, create and track orders, update inventory, and provide store analytics. When asked about store operations, provide accurate and helpful information about product management, order processing, and inventory control."
)


def setup_ecommerce_agent():
    """Set up the e-commerce operations agent with tools."""
    try:
        agent.add_tool(list_store_products)
        agent.add_tool(get_product_details)
        agent.add_tool(create_order)
        agent.add_tool(list_store_orders)
        agent.add_tool(update_product_inventory)
        agent.add_tool(get_store_analytics)
        print("E-commerce operations tools successfully registered with the agent.")
        return True
    except AttributeError as e:
        print(f"Note: Tool registration API may vary depending on the specific Strands implementation. Error: {e}")
        return False


def run_ecommerce_agent(user_input: str):
    """
    Run the e-commerce operations agent with the given user input.
    
    Args:
        user_input: The input from the user
        
    Returns:
        The agent's response
    """
    try:
        response = agent.run(user_input)
        return response
    except ImportError:
        # If strandsagents is not available, return a simulated response
        return f"Simulated response: E-commerce operations agent. You requested: '{user_input}'"
    except Exception as e:
        return f"Error processing your request: {str(e)}"


def main():
    """Main function to run the e-commerce operations agent."""
    # Set up tools
    tools_setup = setup_ecommerce_agent()
    
    print("E-commerce Operations Agent")
    print("This agent can:")
    print("- List store products (e.g., 'list all products')")
    print("- Get product details (e.g., 'show details for product 123')")
    print("- Create orders (e.g., 'create order for customer 456')")
    print("- List store orders (e.g., 'show recent orders')")
    print("- Update inventory (e.g., 'update inventory for product 123')")
    print("- Get store analytics (e.g., 'show store analytics')")
    print("Type 'quit' to exit.\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Agent: Goodbye! E-commerce operations assistant signing off.")
            break
            
        response = run_ecommerce_agent(user_input)
        print(f"Agent: {response}\n")


if __name__ == "__main__":
    main()