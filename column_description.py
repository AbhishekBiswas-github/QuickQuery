"""
column_description.py
======================
Semantic column descriptions for every column across all 8 tables of the ecommerce_db database.
 
Key format:  "table_name.column_name"  →  human-readable description string
 
How it is used:
    mysql_connection.py → get_schemas() calls get_description() for each
    column while building the schema metadata that gets embedded into
    Pinecone. These descriptions tell the LLM the *purpose* of each column
    (not just its name and type), which significantly improves SQL generation
    accuracy — especially for columns with ambiguous names like
    'status', 'is_active', 'total_amount', etc.
 
How to extend:
    If you add a new table or column to ecommerce_db, add a correspondingentry here in the format 
    "table_name.column_name": "description".
    Re-run vector_db_config.py afterwards to rebuild the Pinecone index with the updated descriptions.
 
Tables covered (93 entries total):
    1. customers       (13 columns)
    2. categories      ( 8 columns)
    3. products        (19 columns)
    4. addresses       (13 columns)
    5. orders          (20 columns)
    6. order_items     ( 9 columns)
    7. product_reviews (11 columns)
    8. coupons         (13 columns)
"""



# ---------------------------------------------------------------------------
# Column descriptions dictionary
# ---------------------------------------------------------------------------
 
# Maps "table_name.column_name" → plain-English description.
# Consumed by get_description() below and indirectly by get_schemas() in mysql_connection.py.
COLUMN_DESCRIPTIONS: dict[str, str] = {

    # =========================================================
    # TABLE 1: customers
    # =========================================================
    "customers.customer_id":    "Auto-incremented unique identifier for each customer account",
    "customers.first_name":     "Customer's legal first (given) name",
    "customers.last_name":      "Customer's legal last (family) name",
    "customers.email":          "Customer's unique email address used for login and communications",
    "customers.phone":          "Customer's contact phone number including country code",
    "customers.password_hash":  "Bcrypt-hashed password string — never used in queries or exposed in results",
    "customers.gender":         "Customer's self-reported gender: M, F, Other, or Prefer not to say",
    "customers.date_of_birth":  "Customer's date of birth — used for age verification and birthday promotions",
    "customers.is_active":      "Account status flag: 1 means the account is active, 0 means it is deactivated or banned",
    "customers.email_verified": "Email verification flag: 1 means the customer confirmed their email address, 0 means unverified",
    "customers.loyalty_points": "Accumulated reward points the customer has earned through purchases — redeemable for discounts",
    "customers.created_at":     "Timestamp when the customer account was first created",
    "customers.updated_at":     "Timestamp of the most recent update to the customer record",

    # =========================================================
    # TABLE 2: categories
    # =========================================================
    "categories.category_id":   "Auto-incremented unique identifier for each product category",
    "categories.parent_id":     "References category_id of the parent category — NULL means this is a top-level root category",
    "categories.name":          "Display name of the category shown to customers (e.g. Electronics, Smartphones, Laptops)",
    "categories.slug":          "URL-friendly lowercase hyphenated version of the category name used in web routes",
    "categories.description":   "Short human-readable description of what products belong to this category",
    "categories.is_active":     "Visibility flag: 1 means the category is shown on the storefront, 0 means it is hidden",
    "categories.display_order": "Integer controlling the sort order in which this category appears in navigation menus",
    "categories.created_at":    "Timestamp when the category was created",

    # =========================================================
    # TABLE 3: products
    # =========================================================
    "products.product_id":          "Auto-incremented unique identifier for each product listing",
    "products.category_id":         "Foreign key referencing the category this product belongs to",
    "products.sku":                  "Stock Keeping Unit — a unique alphanumeric code identifying this exact product variant",
    "products.name":                 "Full display name of the product shown to customers on listing and detail pages",
    "products.description":          "Long-form product description with features, specs, and marketing copy",
    "products.brand":                "Manufacturer or brand name of the product (e.g. Apple, Nike, Sony)",
    "products.price":                "Current selling price of the product in USD that customers pay at checkout",
    "products.compare_at_price":     "Original or RRP price shown as a crossed-out reference — used to display a discount; NULL if no discount",
    "products.cost_price":           "Internal purchase or manufacturing cost of the product — used to calculate profit margin",
    "products.stock_quantity":       "Current number of units available in inventory for purchase",
    "products.low_stock_threshold":  "Minimum stock level that triggers a low-stock alert to the operations team",
    "products.weight_kg":            "Physical weight of the product in kilograms — used to calculate shipping costs",
    "products.is_active":            "Listing status: 1 means the product is visible and purchasable, 0 means it is unlisted",
    "products.is_featured":          "Promotional flag: 1 means the product appears in featured sections on the homepage",
    "products.rating_avg":           "Average customer review rating from 1.00 to 5.00 calculated from all approved reviews",
    "products.rating_count":         "Total number of approved customer reviews submitted for this product",
    "products.tags":                 "Comma-separated keyword tags used for internal search and filtering (e.g. apple,iphone,5g)",
    "products.created_at":           "Timestamp when the product listing was first created",
    "products.updated_at":           "Timestamp of the most recent update to the product record",

    # =========================================================
    # TABLE 4: addresses
    # =========================================================
    "addresses.address_id":    "Auto-incremented unique identifier for each saved address record",
    "addresses.customer_id":   "Foreign key referencing the customer who owns this address",
    "addresses.address_type":  "Purpose of this address: shipping means delivery only, billing means payment only, both means used for both",
    "addresses.is_default":    "Default address flag: 1 means this is the customer's primary address pre-selected at checkout",
    "addresses.full_name":     "Full recipient name to print on the shipping label",
    "addresses.phone":         "Contact phone number for the delivery courier to use if needed",
    "addresses.address_line1": "Primary street address including house number and street name",
    "addresses.address_line2": "Optional secondary address line for apartment number, suite, floor, or building name",
    "addresses.city":          "City or town of the delivery address",
    "addresses.state":         "State or province of the delivery address",
    "addresses.postal_code":   "ZIP or postal code of the delivery address",
    "addresses.country_code":  "ISO 3166-1 Alpha-2 two-letter country code (e.g. US, CA, GB)",
    "addresses.created_at":    "Timestamp when this address was saved to the customer account",

    # =========================================================
    # TABLE 5: orders
    # =========================================================
    "orders.order_id":             "Auto-incremented unique identifier for each order placed",
    "orders.customer_id":          "Foreign key referencing the customer who placed this order",
    "orders.shipping_address_id":  "Foreign key referencing the address record where the order should be delivered",
    "orders.billing_address_id":   "Foreign key referencing the address record used for payment billing",
    "orders.order_number":         "Human-readable unique order reference code shown to customers (e.g. ORD-2024-000001)",
    "orders.status":               "Current fulfillment status of the order: pending, confirmed, processing, shipped, delivered, cancelled, refunded, or on_hold",
    "orders.payment_status":       "Current payment status of the order: unpaid, paid, partially_paid, refunded, or failed",
    "orders.payment_method":       "Payment method used at checkout: credit_card, debit_card, paypal, apple_pay, google_pay, bank_transfer, or cod (cash on delivery)",
    "orders.subtotal":             "Sum of all order item line totals before applying any discounts, shipping, or tax",
    "orders.discount_amount":      "Total monetary discount deducted from the subtotal via coupon codes or promotions",
    "orders.shipping_cost":        "Shipping fee charged to the customer for delivery of this order",
    "orders.tax_amount":           "Sales tax or VAT charged on this order",
    "orders.total_amount":         "Final amount charged to the customer: subtotal minus discount plus shipping plus tax",
    "orders.coupon_code":          "Coupon or promo code applied to this order at checkout — NULL if no coupon was used",
    "orders.notes":                "Optional internal or customer-facing notes attached to the order",
    "orders.shipped_at":           "Timestamp when the order was dispatched from the warehouse — NULL if not yet shipped",
    "orders.delivered_at":         "Timestamp when the order was confirmed as delivered to the customer — NULL if not yet delivered",
    "orders.cancelled_at":         "Timestamp when the order was cancelled — NULL if the order was not cancelled",
    "orders.created_at":           "Timestamp when the order was originally placed by the customer",
    "orders.updated_at":           "Timestamp of the most recent update to the order record",

    # =========================================================
    # TABLE 6: order_items
    # =========================================================
    "order_items.order_item_id": "Auto-incremented unique identifier for each line item within an order",
    "order_items.order_id":      "Foreign key referencing the parent order this line item belongs to",
    "order_items.product_id":    "Foreign key referencing the product that was purchased in this line item",
    "order_items.sku_snapshot":  "Snapshot of the product SKU at the time of purchase — preserved in case the product SKU is later changed",
    "order_items.name_snapshot": "Snapshot of the product name at the time of purchase — preserved in case the product name is later changed",
    "order_items.unit_price":    "Price per single unit of the product at the time of purchase",
    "order_items.quantity":      "Number of units of this product purchased in this line item",
    "order_items.discount_pct":  "Percentage discount applied to this specific line item (e.g. 10.00 means 10% off)",
    "order_items.line_total":    "Final total for this line item: unit_price multiplied by quantity after applying the line-level discount",

    # =========================================================
    # TABLE 7: product_reviews
    # =========================================================
    "product_reviews.review_id":     "Auto-incremented unique identifier for each product review",
    "product_reviews.product_id":    "Foreign key referencing the product being reviewed",
    "product_reviews.customer_id":   "Foreign key referencing the customer who wrote this review",
    "product_reviews.order_id":      "Foreign key referencing the order that included this product — used to mark the review as a verified purchase; NULL if not verified",
    "product_reviews.rating":        "Numeric star rating given by the customer from 1 (worst) to 5 (best)",
    "product_reviews.title":         "Short headline or summary title of the review written by the customer",
    "product_reviews.body":          "Full detailed text of the customer's review",
    "product_reviews.is_verified":   "Verified purchase flag: 1 means the reviewer actually bought the product via a linked order",
    "product_reviews.is_approved":   "Moderation flag: 1 means the review passed moderation and is publicly visible, 0 means it is hidden",
    "product_reviews.helpful_votes": "Number of other customers who marked this review as helpful",
    "product_reviews.created_at":    "Timestamp when the review was submitted",

    # =========================================================
    # TABLE 8: coupons
    # =========================================================
    "coupons.coupon_id":       "Auto-incremented unique identifier for each coupon",
    "coupons.code":            "Unique alphanumeric coupon code that customers enter at checkout (e.g. SAVE10, BLACKFRI25)",
    "coupons.description":     "Human-readable explanation of what the coupon offers and any conditions",
    "coupons.discount_type":   "Type of discount: percentage deducts a percent of the order total, fixed_amount deducts a flat dollar amount, free_shipping waives the shipping fee",
    "coupons.discount_value":  "Magnitude of the discount — a percentage value (e.g. 20.00 for 20%) or a flat dollar amount (e.g. 50.00 for $50 off)",
    "coupons.min_order_value": "Minimum order subtotal in USD required before this coupon can be applied — 0.00 means no minimum",
    "coupons.max_uses":        "Maximum total number of times this coupon can be redeemed across all customers — NULL means unlimited uses",
    "coupons.used_count":      "Running count of how many times this coupon has been successfully redeemed so far",
    "coupons.per_user_limit":  "Maximum number of times a single customer is allowed to use this coupon",
    "coupons.is_active":       "Availability flag: 1 means the coupon is currently active and can be used, 0 means it is disabled",
    "coupons.starts_at":       "Datetime from which this coupon becomes valid and can be applied at checkout",
    "coupons.expires_at":      "Datetime after which this coupon is no longer valid — NULL means it never expires",
    "coupons.created_at":      "Timestamp when this coupon was created in the system",
}


# ---------------------------------------------------------------------------
# Public helper
# ---------------------------------------------------------------------------
 
def get_description(table_name: str, column_name: str) -> str:
    """
    Look up the semantic description for a given table/column pair.
 
    Centralises the fallback message in one place — if the description
    is missing (e.g. a new column was added but not yet documented),
    a consistent fallback string is returned instead of scattering
    .get() calls with inline defaults across the codebase.
 
    Args:
        table_name:  The table the column belongs to (e.g. "orders").
        column_name: The column to look up (e.g. "total_amount").
 
    Returns:
        The human-readable description string, or a standard fallback
        message if no entry exists for this table/column pair.
 
    Example:
        >>> get_description("orders", "total_amount")
        'Final amount charged to the customer: subtotal minus discount plus shipping plus tax'
 
        >>> get_description("orders", "unknown_col")
        'No description available'
    """
    return COLUMN_DESCRIPTIONS.get(
        f"{table_name}.{column_name}",
        "No description available"
    )
