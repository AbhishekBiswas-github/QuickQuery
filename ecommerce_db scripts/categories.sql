-- ============================================================
--  E-COMMERCE DATABASE  |  TABLE 2: categories
--  Self-referencing parent/child hierarchy
-- ============================================================

USE ecommerce_db;

CREATE TABLE IF NOT EXISTS categories (
    category_id   INT          UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    parent_id     INT          UNSIGNED DEFAULT NULL,
    name          VARCHAR(100) NOT NULL,
    slug          VARCHAR(110) NOT NULL UNIQUE,
    description   TEXT         DEFAULT NULL,
    is_active     TINYINT(1)   NOT NULL DEFAULT 1,
    display_order INT          NOT NULL DEFAULT 0,
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_category_parent
        FOREIGN KEY (parent_id) REFERENCES categories (category_id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    INDEX idx_parent (parent_id),
    INDEX idx_slug   (slug)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------
-- Root categories (parent_id = NULL)
-- -----------------------------------------------------------
INSERT INTO categories (category_id, parent_id, name, slug, description, is_active, display_order) VALUES
(1, NULL, 'Electronics',       'electronics',       'All electronic devices and accessories',     1, 1),
(2, NULL, 'Clothing',          'clothing',          'Apparel for men, women and kids',            1, 2),
(3, NULL, 'Home & Garden',     'home-garden',       'Furniture, decor, and outdoor items',        1, 3),
(4, NULL, 'Sports & Outdoors', 'sports-outdoors',   'Equipment and gear for active lifestyles',   1, 4),
(5, NULL, 'Books & Media',     'books-media',       'Books, music, movies and digital media',     1, 5),
(6, NULL, 'Beauty & Health',   'beauty-health',     'Skincare, makeup, and wellness products',    1, 6),
(7, NULL, 'Toys & Games',      'toys-games',        'Toys, games and entertainment for all ages', 1, 7),
(8, NULL, 'Automotive',        'automotive',        'Car parts, accessories and tools',           1, 8);

-- -----------------------------------------------------------
-- Sub-categories
-- -----------------------------------------------------------
INSERT INTO categories (parent_id, name, slug, description, is_active, display_order) VALUES
-- Electronics children
(1, 'Smartphones',      'smartphones',       'Mobile phones and smartphones',              1, 1),  -- id 9
(1, 'Laptops',          'laptops',           'Notebooks, ultrabooks and gaming laptops',   1, 2),  -- id 10
(1, 'Tablets',          'tablets',           'iPads, Android tablets and e-readers',       1, 3),  -- id 11
(1, 'Audio',            'audio',             'Headphones, speakers and earbuds',           1, 4),  -- id 12
(1, 'Cameras',          'cameras',           'DSLRs, mirrorless and action cameras',       1, 5),  -- id 13
(1, 'Smart Home',       'smart-home',        'Smart speakers, plugs and automation',       1, 6),  -- id 14
-- Clothing children
(2, 'Mens Clothing',    'mens-clothing',     'T-shirts, jeans, jackets for men',           1, 1),  -- id 15
(2, 'Womens Clothing',  'womens-clothing',   'Dresses, tops and skirts for women',         1, 2),  -- id 16
(2, 'Kids Clothing',    'kids-clothing',     'Clothes for toddlers and children',          1, 3),  -- id 17
(2, 'Footwear',         'footwear',          'Shoes, boots and sandals for all',           1, 4),  -- id 18
-- Home & Garden children
(3, 'Furniture',        'furniture',         'Sofas, beds, tables and chairs',             1, 1),  -- id 19
(3, 'Kitchen & Dining', 'kitchen-dining',    'Cookware, utensils and appliances',          1, 2),  -- id 20
(3, 'Bedding & Bath',   'bedding-bath',      'Sheets, towels and bathroom accessories',    1, 3),  -- id 21
-- Sports children
(4, 'Fitness Equipment','fitness-equipment', 'Gym machines, weights and mats',             1, 1),  -- id 22
(4, 'Outdoor Sports',   'outdoor-sports',    'Camping, hiking and cycling gear',           1, 2),  -- id 23
-- Books children
(5, 'Fiction',          'fiction-books',     'Novels, thrillers and literary fiction',     1, 1),  -- id 24
(5, 'Non-Fiction',      'non-fiction-books', 'Business, science and self-help books',      1, 2),  -- id 25
(5, 'Textbooks',        'textbooks',         'Academic and professional textbooks',        1, 3);  -- id 26

SELECT COUNT(*) AS total_categories FROM categories;