-- ============================================================
--  E-COMMERCE DATABASE  |  TABLE 3: products
--  Depends on: categories
-- ============================================================

USE ecommerce_db;

CREATE TABLE IF NOT EXISTS products (
    product_id          INT           UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    category_id         INT           UNSIGNED NOT NULL,
    sku                 VARCHAR(60)   NOT NULL UNIQUE,
    name                VARCHAR(200)  NOT NULL,
    description         TEXT          DEFAULT NULL,
    brand               VARCHAR(80)   DEFAULT NULL,
    price               DECIMAL(10,2) NOT NULL,
    compare_at_price    DECIMAL(10,2) DEFAULT NULL  COMMENT 'Original price before discount',
    cost_price          DECIMAL(10,2) DEFAULT NULL  COMMENT 'Purchase / manufacturing cost',
    stock_quantity      INT           NOT NULL DEFAULT 0,
    low_stock_threshold INT           NOT NULL DEFAULT 10,
    weight_kg           DECIMAL(6,3)  DEFAULT NULL,
    is_active           TINYINT(1)    NOT NULL DEFAULT 1,
    is_featured         TINYINT(1)    NOT NULL DEFAULT 0,
    rating_avg          DECIMAL(3,2)  DEFAULT NULL,
    rating_count        INT           UNSIGNED NOT NULL DEFAULT 0,
    tags                VARCHAR(255)  DEFAULT NULL,
    created_at          DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_product_category
        FOREIGN KEY (category_id) REFERENCES categories (category_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_category    (category_id),
    INDEX idx_sku         (sku),
    INDEX idx_brand       (brand),
    INDEX idx_price       (price),
    INDEX idx_active_feat (is_active, is_featured)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------
-- SAMPLE DATA — 60 products
-- cat IDs: 9=Smartphones 10=Laptops 11=Tablets 12=Audio
--          13=Cameras 14=SmartHome 15=Mens 16=Womens
--          18=Footwear 19=Furniture 20=Kitchen
--          22=Fitness 23=Outdoor 24=Fiction 25=Non-Fiction
-- -----------------------------------------------------------
INSERT INTO products
  (category_id, sku, name, brand, price, compare_at_price, cost_price,
   stock_quantity, low_stock_threshold, weight_kg, is_active, is_featured,
   rating_avg, rating_count, tags)
VALUES
-- Smartphones
( 9,'SPH-APLIP15PM', 'Apple iPhone 15 Pro Max 256GB',          'Apple',      1199.99,    NULL, 750.00,  320,15,0.221,1,1,4.80, 4821,'apple,iphone,5g,flagship'),
( 9,'SPH-SAM-S24U',  'Samsung Galaxy S24 Ultra 512GB',         'Samsung',     999.99, 1199.99, 580.00,  410,15,0.232,1,1,4.72, 3254,'samsung,android,s-pen,5g'),
( 9,'SPH-GPX8P',     'Google Pixel 8 Pro 256GB',               'Google',      799.99,  999.99, 460.00,  195,10,0.213,1,0,4.65, 1872,'google,pixel,ai,android'),
( 9,'SPH-OP12',      'OnePlus 12 256GB',                       'OnePlus',     599.99,  699.99, 340.00,  280,10,0.220,1,0,4.55,  987,'oneplus,fast-charge,android'),
( 9,'SPH-XIMI14P',   'Xiaomi 14 Pro 512GB',                    'Xiaomi',      649.99,  749.99, 360.00,  150,10,0.223,1,0,4.50,  654,'xiaomi,android,leica'),
-- Laptops
(10,'LPT-APLMBPM3',  'Apple MacBook Pro 14 M3 Pro',            'Apple',      1999.99,    NULL,1200.00,   90, 5,1.610,1,1,4.88, 2310,'apple,macbook,m3,laptop'),
(10,'LPT-DLX15G9',   'Dell XPS 15 Intel Core i9',              'Dell',       1499.99, 1799.99, 880.00,  140, 8,1.860,1,1,4.60, 1540,'dell,xps,intel,laptop'),
(10,'LPT-HPENV16',   'HP Envy 16 Touch OLED',                  'HP',          999.99, 1199.99, 580.00,  175,10,2.100,1,0,4.42,  890,'hp,envy,touch,oled'),
(10,'LPT-LNV5P',     'Lenovo ThinkPad X1 Carbon Gen 11',       'Lenovo',     1349.99,    NULL, 780.00,  110, 8,1.120,1,0,4.70, 1120,'lenovo,thinkpad,business'),
(10,'LPT-ASUZF15',   'Asus ZenBook Pro 15 OLED',               'Asus',        899.99, 1099.99, 520.00,  200,10,1.800,1,0,4.38,  760,'asus,zenbook,oled,laptop'),
-- Tablets
(11,'TAB-APLIPADP13','Apple iPad Pro 13 M4 Wi-Fi 256GB',       'Apple',      1099.99,    NULL, 640.00,  130, 8,0.579,1,1,4.82, 1920,'apple,ipad,m4,tablet'),
(11,'TAB-SAMSGT9P',  'Samsung Galaxy Tab S9 Plus',             'Samsung',     699.99,  899.99, 400.00,  165,10,0.581,1,0,4.55,  870,'samsung,android,tablet'),
(11,'TAB-KNDFIRE11', 'Amazon Kindle Fire HD 11',               'Amazon',      149.99,  199.99,  70.00,  500,20,0.465,1,0,4.10, 3200,'amazon,kindle,budget,tablet'),
-- Audio
(12,'AUD-SNYWH1000X5','Sony WH-1000XM5 Wireless Headphones',   'Sony',        349.99,  399.99, 180.00,  420,20,0.250,1,1,4.75, 6710,'sony,noise-cancel,headphones'),
(12,'AUD-BOSE700',   'Bose QuietComfort 45 Headphones',        'Bose',        279.99,  329.99, 145.00,  300,15,0.238,1,0,4.68, 4230,'bose,noise-cancel,headphones'),
(12,'AUD-APL3RDGEN', 'Apple AirPods Pro 3rd Gen',              'Apple',       249.99,  279.99, 130.00,  680,25,0.051,1,1,4.72, 8920,'apple,airpods,earbuds,anc'),
(12,'AUD-JBLFP6',    'JBL Flip 6 Portable Speaker',            'JBL',          99.99,  129.99,  45.00,  750,30,0.550,1,0,4.60, 5100,'jbl,bluetooth,speaker'),
(12,'AUD-SNYWF1000XM5','Sony WF-1000XM5 Earbuds',             'Sony',        249.99,  279.99, 120.00,  350,20,0.056,1,0,4.70, 3840,'sony,earbuds,anc,wireless'),
-- Cameras
(13,'CAM-SNZA7M5',   'Sony Alpha A7 Mark V Mirrorless',        'Sony',       2799.99,    NULL,1600.00,   45, 5,0.587,1,1,4.85,  820,'sony,mirrorless,full-frame'),
(13,'CAM-CANR6M2',   'Canon EOS R6 Mark II',                   'Canon',      2299.99,    NULL,1350.00,   60, 5,0.588,1,0,4.78,  640,'canon,mirrorless,camera'),
(13,'CAM-GOPROH12',  'GoPro HERO12 Black',                     'GoPro',       349.99,  399.99, 170.00,  380,20,0.154,1,0,4.55, 2980,'gopro,action-cam,4k,waterproof'),
-- Smart Home
(14,'SMH-AMZECHO4',  'Amazon Echo Dot 5th Gen',                'Amazon',       49.99,   59.99,  20.00, 1200,50,0.304,1,0,4.45,12400,'amazon,echo,alexa'),
(14,'SMH-GGNEST3',   'Google Nest Thermostat',                 'Google',      129.99,  149.99,  58.00,  430,20,0.210,1,1,4.60, 3810,'google,nest,thermostat'),
(14,'SMH-PHIHUE4PK', 'Philips Hue White and Color 4-Pack',     'Philips',      99.99,  119.99,  45.00,  560,25,0.380,1,0,4.65, 6200,'philips,hue,smart-bulb,rgb'),
-- Mens Clothing
(15,'CLM-LEVIS501',  'Levis 501 Original Jeans W32 L32',       'Levis',        69.99,   89.99,  28.00,  900,30,0.700,1,0,4.50, 7800,'levis,jeans,denim,mens'),
(15,'CLM-NIKDRYFIT', 'Nike Dri-FIT Training T-Shirt L',        'Nike',         34.99,   44.99,  13.00, 1500,50,0.200,1,1,4.40, 5600,'nike,dri-fit,tshirt,mens'),
(15,'CLM-ADIHOODIE', 'Adidas Essentials Fleece Hoodie',        'Adidas',       54.99,   69.99,  22.00, 1100,40,0.600,1,0,4.35, 3200,'adidas,hoodie,fleece,mens'),
(15,'CLM-RALPHPOLO', 'Ralph Lauren Classic Polo Shirt M',      'Ralph Lauren', 89.99,    NULL,  35.00,  450,20,0.250,1,0,4.55, 2100,'ralph-lauren,polo,shirt,mens'),
-- Womens Clothing
(16,'CLW-ZARAFLORAL','Zara Floral Wrap Midi Dress S',          'Zara',         59.99,   79.99,  22.00,  380,15,0.320,1,1,4.30, 1840,'zara,dress,floral,womens'),
(16,'CLW-HMBASIC',   'HM Basic Slim Crop Top M Black',         'HM',           19.99,   24.99,   7.00, 1200,40,0.150,1,0,4.15, 2900,'hm,crop-top,basic,womens'),
(16,'CLW-LULUYOGA',  'Lululemon Align Pant 28 Black',          'Lululemon',    98.99,  118.00,  40.00,  520,20,0.250,1,1,4.70, 6400,'lululemon,leggings,yoga,womens'),
(16,'CLW-FREEBLAZE', 'Free People Beach Blazer Blue',          'Free People',  89.99,    NULL,  36.00,  180,10,0.450,1,0,4.40,  760,'free-people,blazer,womens'),
-- Footwear
(18,'SHO-NKAIR270',  'Nike Air Max 270 White US10',            'Nike',        149.99,  169.99,  60.00,  550,20,0.800,1,1,4.60, 4320,'nike,air-max,sneakers'),
(18,'SHO-ADSTAN',    'Adidas Stan Smith White US9',            'Adidas',       89.99,  109.99,  35.00,  680,25,0.700,1,0,4.55, 5100,'adidas,stan-smith,sneakers'),
(18,'SHO-TIMSBT',    'Timberland 6 Inch Premium Boot Brown',   'Timberland',  179.99,    NULL,  72.00,  320,15,1.300,1,0,4.65, 2800,'timberland,boots,leather'),
(18,'SHO-DRMRT',     'Dr Martens 1460 Black Leather',          'Dr Martens',  159.99,    NULL,  65.00,  280,15,1.200,1,0,4.72, 3900,'doc-martens,boots,leather'),
-- Furniture
(19,'FRN-IKEASOFA',  'IKEA KIVIK 3-Seat Sofa Gray',            'IKEA',        599.99,  749.99, 280.00,   65, 5,52.00,1,0,4.20, 1240,'ikea,sofa,living-room'),
(19,'FRN-HERMANM',   'Herman Miller Aeron Chair Black',        'Herman Miller',1395.00, NULL,  700.00,   40, 3,18.60,1,1,4.85,  980,'herman-miller,ergonomic,office'),
(19,'FRN-WAYFBED',   'Wayfair Upholstered King Bed Grey',      'Wayfair',     499.99,  649.99, 210.00,   80, 5,45.00,1,0,4.25,  870,'wayfair,bed,king,bedroom'),
-- Kitchen
(20,'KIT-INSTPOT7Q', 'Instant Pot Duo 7-in-1 7Qt',             'Instant Pot',  99.99,  129.99,  42.00,  780,30,5.180,1,1,4.72,18500,'instant-pot,pressure-cooker'),
(20,'KIT-KITTOAST',  'KitchenAid 2-Slice Toaster Empire',      'KitchenAid',   79.99,   99.99,  30.00,  420,20,1.450,1,0,4.48, 3100,'kitchenaid,toaster,kitchen'),
(20,'KIT-NNJAFRY',   'Ninja AF101 Air Fryer 4Qt',              'Ninja',        99.99,  119.99,  42.00,  860,30,3.175,1,1,4.68,24700,'ninja,air-fryer,kitchen'),
(20,'KIT-VITAMXA',   'Vitamix A3500 Ascent Blender',           'Vitamix',     549.99,  649.99, 270.00,  190,10,5.310,1,0,4.80, 4200,'vitamix,blender,professional'),
-- Fitness
(22,'FIT-BOWFLX552', 'Bowflex SelectTech 552 Dumbbells',       'Bowflex',     349.99,  429.99, 165.00,  220,10,22.70,1,1,4.75, 8800,'bowflex,dumbbells,adjustable'),
(22,'FIT-PELRIDER',  'Peloton Bike Plus Exercise Bike',         'Peloton',    1995.00,    NULL,1050.00,   30, 3,57.20,1,1,4.55, 3200,'peloton,exercise-bike,fitness'),
(22,'FIT-YOMAT6MM',  'Manduka PRO Yoga Mat 6mm',               'Manduka',      99.99,  120.00,  38.00,  680,25, 3.10,1,0,4.70, 6400,'manduka,yoga-mat,fitness'),
(22,'FIT-TRDMND',    'NordicTrack T 6.5 Si Treadmill',         'NordicTrack', 699.99,  899.99, 350.00,   45, 5,90.70,1,0,4.32, 1450,'nordictrack,treadmill,cardio'),
-- Outdoor Sports
(23,'OUT-COLEMANTNC','Coleman Sundome 2-Person Tent',           'Coleman',      74.99,   99.99,  30.00,  430,20, 2.40,1,0,4.42, 7200,'coleman,tent,camping,outdoor'),
(23,'OUT-TREKPOLE',  'Black Diamond Trail Sport Trekking Poles','Black Diamond',79.99,   NULL,  32.00,  280,15, 0.54,1,0,4.55, 1800,'black-diamond,trekking,hiking'),
-- Books Fiction
(24,'BKF-ATOMHAB',   'Atomic Habits by James Clear',           'Penguin',      16.99,   27.99,   5.50, 2500,50, 0.29,1,1,4.82,52000,'habits,self-help,bestseller'),
(24,'BKF-4HRWRK',    'The 4-Hour Workweek by Tim Ferriss',     'Crown',        18.99,   26.99,   6.00, 1800,40, 0.34,1,0,4.48,28000,'productivity,business'),
(24,'BKF-SAPIENS',   'Sapiens A Brief History by Harari',      'Harper',       17.99,   24.99,   5.80, 2200,50, 0.38,1,1,4.68,41000,'history,non-fiction,bestseller'),
-- Non-Fiction / Classic Fiction
(25,'BKN-CTCHFIRE',  'Catching Fire by Suzanne Collins',       'Scholastic',   14.99,   18.99,   4.50, 3200,60, 0.37,1,0,4.65,38000,'ya,fiction,dystopia'),
(25,'BKN-1984',      '1984 by George Orwell Penguin Edition',  'Penguin',      12.99,   15.99,   4.00, 4100,80, 0.26,1,1,4.72,95000,'orwell,classic,dystopia'),
(25,'BKN-DUNE',      'Dune by Frank Herbert Deluxe Edition',   'Ace Books',    21.99,   28.99,   7.50, 1900,40, 0.57,1,0,4.78,67000,'herbert,sci-fi,dune,classic');

SELECT * FROM products;