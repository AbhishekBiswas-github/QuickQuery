-- ============================================================
--  E-COMMERCE DATABASE  |  TABLE 7: product_reviews
--                       |  TABLE 8: coupons
--  Depends on: customers, products, orders
-- ============================================================

USE ecommerce_db;

-- -----------------------------------------------------------
-- TABLE 7: product_reviews
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS product_reviews (
    review_id     INT          UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    product_id    INT          UNSIGNED NOT NULL,
    customer_id   INT          UNSIGNED NOT NULL,
    order_id      INT          UNSIGNED DEFAULT NULL COMMENT 'Verified purchase reference',
    rating        TINYINT      NOT NULL CHECK (rating BETWEEN 1 AND 5),
    title         VARCHAR(150) DEFAULT NULL,
    body          TEXT         DEFAULT NULL,
    is_verified   TINYINT(1)   NOT NULL DEFAULT 0 COMMENT '1 = verified purchase',
    is_approved   TINYINT(1)   NOT NULL DEFAULT 1,
    helpful_votes INT          UNSIGNED NOT NULL DEFAULT 0,
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_review_product
        FOREIGN KEY (product_id)  REFERENCES products (product_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_review_customer
        FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_review_order
        FOREIGN KEY (order_id)    REFERENCES orders (order_id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    UNIQUE KEY uq_customer_product (customer_id, product_id),
    INDEX idx_product  (product_id),
    INDEX idx_rating   (rating),
    INDEX idx_approved (is_approved)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------
-- SAMPLE DATA — 50 reviews
-- -----------------------------------------------------------
INSERT INTO product_reviews
  (product_id, customer_id, order_id, rating, title, body, is_verified, is_approved, helpful_votes)
VALUES
-- Smartphones
( 1,  1,  1, 5,'Absolutely stunning phone',        'Camera quality is unbelievable and battery lasts all day. Best purchase I have ever made.',                     1,1, 42),
( 2,  6,  5, 5,'Flagship performance all round',   'The S-Pen is a game changer. Screen is gorgeous and the AI features are genuinely useful day to day.',          1,1, 38),
( 3, 14, 13, 5,'Best Android experience out there','Clean software, excellent cameras and fast updates. Pixel truly sets the Android standard.',                     1,1, 29),
( 4, 21, 20, 4,'Great value flagship phone',       'Very fast with Snapdragon 8 Gen 3 and 100W charging is brilliant. Slight camera lag at night but overall awesome.',1,1,14),
( 5, 37, 36, 4,'Xiaomi keeps impressing me',       'Leica cameras are excellent and the processor handles everything. Build quality feels premium at this price.',    1,1, 11),
-- Laptops
( 6, 10,  9, 5,'A laptop for the ages',            'M3 Pro chip handles everything I throw at it. 18 hours of real-world battery is no exaggeration. Worth every cent.',1,1,95),
( 7, 36, 35, 5,'Dell XPS never disappoints',       'OLED screen is breathtaking and it runs cool under sustained load. Keyboard feel is top tier for typing.',       1,1, 61),
( 8, 45, 44, 4,'Solid mid-range powerhouse',       'Touch screen is very responsive and OLED colors really pop. Battery life could be a bit longer but acceptable.', 1,1, 23),
( 9, 29, 28, 5,'ThinkPad reliability is real',     'Travel extensively for work. This laptop survived three drops and two years of heavy use. Best keyboard around.', 1,1, 77),
(10, 28, 27, 4,'Asus delivers great value',        'OLED panel is gorgeous and performance is strong. Fan noise under load is the only minor downside.',              1,1, 18),
-- Tablets
(11, 13, 12, 5,'iPad Pro sets the benchmark',      'M4 chip, stunning display and Apple Pencil precision make this the best tablet money can buy right now.',        1,1, 55),
(12, 16, 15, 4,'Premium Android tablet experience','Gorgeous AMOLED and smooth 120Hz refresh. Samsung DeX mode is a productivity boost. Pricey though.',             1,1, 31),
(13, 46, 56, 4,'Surprisingly capable budget tab',  'Perfect for my kids. Built tough and parental controls are easy to set up. Not blazing fast but does the job.',  1,1, 18),
-- Audio
(14,  2,  2, 5,'Best noise cancelling ever made',  'Completely silences the airplane cabin. 30-hour battery. Wear for hours with zero ear fatigue. Absolutely brilliant.',1,1,110),
(15, 24, 23, 5,'Bose never lets me down',          'QuietComfort lives up to its name. Warm detailed sound. My essential work-from-home companion every day.',        1,1, 86),
(16,  7,  6, 5,'AirPods Pro are pure magic',       'Spatial audio and ANC together are just magic. Fit is perfect and call quality is crystal clear outdoors.',      1,1, 74),
(17, 11, 10, 5,'Flip 6 is a party starter',        'Connected to two phones simultaneously, waterproof tested in the pool, incredible volume for the compact size.', 1,1, 49),
(18, 35, 34, 4,'Sony earbuds rival the best',      'ANC is nearly as good as the over-ear model. Fit is secure and sound is detailed. Battery case is slim.',        1,1, 32),
-- Cameras
(19, 19, 18, 5,'Sony Alpha is simply unbeatable',  'A7M5 autofocus is insane tracking birds in flight effortlessly. Color science is world class. My forever camera.',1,1, 63),
(20,  4,  4, 5,'Canon color science is pure art',  'R6 Mark II Eye AF is flawless for portraiture. Dynamic range impressed me and build quality is very robust.',    1,1, 47),
(21, 28, 27, 5,'GoPro for the true adventurers',   'Night mode finally works brilliantly. HyperSmooth 6.0 makes mountain bike footage look truly cinematic.',        1,1, 35),
-- Smart Home
(22, 12, 11, 4,'Alexa on my bedside table',        'Compact with great sound for its size. Alexa routines save me loads of time each morning getting ready.',        1,1, 22),
(23, 25, 24, 5,'Nest thermostat pays for itself',  'Cut my heating bill by 23 percent in the first two months. Easy app and a genuinely beautiful design.',          1,1, 58),
(24, 37, 36, 5,'Philips Hue changes everything',   'Waking up to a sunrise alarm scene every morning has been life-changing. Color accuracy is always spot on.',     1,1, 41),
-- Mens Clothing
(25,  3,  3, 4,'Levi 501 never goes out of style', 'Fits true to size and denim quality is noticeably better than cheaper brands. Slight stiffness at first wash.',  1,1, 27),
(26, 17, 16, 5,'Nike Dri-FIT is my gym staple',    'Wore this every other day for six months. Still holds its shape and wicks sweat perfectly. Buying three more.',  1,1, 33),
(27, 15, 14, 4,'Cozy and well-made Adidas hoodie', 'Super soft fleece, warm but not too stifling. Smart pocket design. Sizing runs slightly large so size down.',    1,1, 19),
(28, 16, 15, 4,'Classic Ralph Lauren polo shirt',  'Fabric feels genuinely premium and the fit is tailored without being tight. A true wardrobe essential piece.',   1,1, 24),
-- Womens Clothing
(29, 34, 33, 4,'Zara midi dress summer winner',    'Beautiful floral pattern and flattering wrap cut. Material is light and breathable. Runs small so size up one.', 1,1, 16),
(30, 12, 11, 3,'H&M crop top decent for price',    'Good basic staple at this price point. Fabric is thin but wears well. Color is accurate to the website photos.',1,1,  8),
(31, 38, 38, 5,'Lululemon worth every penny',      'Buttery soft material that holds shape after 50 washes. Best leggings I have ever owned, full stop.',            1,1, 88),
(32, 33, 32, 4,'Free People blazer is gorgeous',   'Stunning color and relaxed fit. Works dressed up or casually. Fabric quality is excellent for the price paid.',  1,1, 21),
-- Footwear
(33,  8,  7, 5,'Air Max 270 all day comfort',      'Cushioning is insane for long city walks. My back stopped aching after switching from my old trainers to these.',1,1, 53),
(34,  9,  8, 5,'Stan Smith the timeless classic',  'Clean design pairs with everything. Leather is supple right out of the box. I now own four pairs in different colors.',1,1,67),
(35, 26, 25, 5,'Timberlands are built for life',   'Had these five years and still completely waterproof after heavy use. The yellow boot is an icon for good reason.',1,1,79),
(36, 30, 29, 4,'Dr Martens worth the investment',  'Took about two weeks to break in but now completely comfortable. Build quality is exceptional and they look great.',1,1,44),
-- Furniture
(37, 27, 26, 5,'Herman Miller changed my back',    'Spent years dealing with back pain. Two months in the Aeron and I am a different person. Worth saving up for.',  1,1,102),
(38, 19, 18, 4,'Sony camera arrived well packed',  'Order was fulfilled quickly and the camera body was very well protected in transit. Great buying experience.',    1,1,  5),
(39,  3,  3, 4,'Instant Pot is a lifesaver',       'Meal prepping on Sunday is now four times faster. The yogurt mode is a hidden gem. Cannot imagine cooking without it.',1,1,91),
-- Kitchen
(40, 22, 21, 5,'Ninja Air Fryer daily driver',     'Crispy wings, roasted veggies, reheated pizza - this thing does it all brilliantly. Easy to clean and very compact.',1,1,84),
(41, 29, 28, 5,'Vitamix is a professional tool',   'Built like an absolute tank. Smoothies are perfectly silky. Variable speed gives real precise control. Forever appliance.',1,1,70),
(42, 40, 40, 4,'KitchenAid toaster looks stunning','Gorgeous design that elevates the whole kitchen. Toasts perfectly and evenly. Wish the slots were slightly wider.',1,1,29),
-- Fitness
(43, 34, 33, 5,'Bowflex dumbbells save huge space','Replaced an entire rack in my garage gym. Quick adjustment and very solid build. Best fitness investment I made.', 1,1, 59),
(44, 31, 30, 4,'Peloton community keeps me going', 'Live classes and instructor motivation are genuinely addictive. Bike is solid and quiet. Subscription cost adds up.',1,1,44),
(45, 32, 31, 5,'Manduka mat for serious yogis',    'Dense, grippy and does not bunch or slide. I practice six days a week and after two years it still looks brand new.',1,1,36),
(46, 42, 41, 4,'NordicTrack solid home treadmill', 'iFit integration is seamless and the belt is wide and very quiet. Takes two people to assemble but well worth it.',1,1,25),
-- Outdoor
(47, 28, 27, 5,'Coleman tent for weekend warriors','Set up solo in eight minutes. Weathered a heavy rain storm without a single drip inside. Outstanding value buy.',  1,1, 43),
(48, 40, 39, 4,'Black Diamond poles are solid',    'Lightweight, lock quickly and comfortable cork grips. Helped enormously on steep alpine descents. Recommended.',  1,1, 17),
-- Books
(49,  1,  1, 5,'Atomic Habits changed my life',   'Practical, science-backed advice wrapped in great storytelling. I re-read it every single year. A must-own.',      1,1,200),
(51,  3,  3, 5,'Sapiens is genuinely mind-expanding','Harari challenges every assumption about civilization. Required reading for every curious human being alive.',   1,1,178),
(53, 49, 47, 5,'Dune is a true sci-fi masterpiece','Herbert built an entire universe of staggering depth. Themes of ecology, power and religion are more relevant than ever.',1,1,130);

DESCRIBE TABLE product_reviews;
INSERT INTO product_reviews
  (product_id, customer_id, order_id, rating, title, body,
   is_verified, is_approved, helpful_votes, created_at)
VALUES
(54,56,NULL,1,'Does not work well','Would definitely recommend to friends and family.',1,1,48,'2025-03-05 05:57:00'),
(8,48,NULL,5,'Worth every penny','Quality matches the product description well.',1,0,35,'2024-05-24 22:57:00'),
(43,83,NULL,5,'Best purchase ever','Noticed a slight issue but customer service resolved it quickly.',0,1,42,'2022-05-04 08:52:00'),
(17,46,NULL,5,'Worth every penny','Setup was straightforward and took only minutes.',1,1,62,'2022-08-11 04:34:00'),
(50,111,NULL,5,'Best purchase ever','Arrived well packaged with no damage at all.',1,1,9,'2022-05-25 18:46:00'),
(17,115,NULL,5,'Worth every penny','Works exactly as advertised, no issues so far.',1,1,4,'2024-03-10 08:09:00'),
(45,85,NULL,2,'Slightly disappointed','A bit pricey but the quality justifies the cost.',1,1,61,'2024-06-12 12:54:00'),
(47,18,NULL,4,'Really impressed','Fits perfectly and is very comfortable.',0,1,61,'2022-09-06 18:34:00'),
(23,86,NULL,4,'Works perfectly','Delivery was fast and packaging was excellent.',1,0,11,'2024-01-19 17:54:00'),
(22,21,NULL,3,'Okay for the price','Setup was straightforward and took only minutes.',1,1,49,'2023-01-27 09:44:00'),
(25,28,NULL,4,'Good quality overall','Exceeded my initial expectations on quality.',1,1,94,'2023-01-24 04:02:00'),
(13,7,NULL,4,'Solid product','Exceeded my initial expectations on quality.',1,1,82,'2023-09-23 15:34:00'),
(54,116,NULL,1,'Very disappointed','Delivery was fast and packaging was excellent.',1,1,92,'2022-03-29 12:07:00'),
(14,134,NULL,4,'Great value','Purchased as a gift and the recipient loved it.',1,1,94,'2022-10-17 15:41:00'),
(2,121,NULL,2,'Slightly disappointed','Build quality feels solid and durable.',1,1,22,'2022-04-13 09:52:00'),
(51,25,NULL,4,'Great value','Purchased as a gift and the recipient loved it.',1,1,14,'2024-10-15 19:51:00'),
(40,57,NULL,5,'Outstanding quality','Performance is consistently smooth and reliable.',1,1,94,'2024-04-03 10:07:00'),
(44,148,NULL,4,'Good quality overall','Setup was straightforward and took only minutes.',0,1,42,'2022-05-10 03:17:00'),
(10,107,NULL,5,'Five stars all day','Good product but took a while to get used to.',1,1,74,'2022-03-25 04:06:00'),
(51,97,NULL,3,'Decent product','Exceeded my initial expectations on quality.',1,1,118,'2022-07-02 22:41:00'),
(38,73,NULL,5,'Worth every penny','Works exactly as advertised, no issues so far.',1,1,66,'2024-07-11 13:15:00'),
(12,10,NULL,4,'Very satisfied','Runs quietly and efficiently in daily use.',0,1,100,'2023-09-09 11:26:00'),
(1,143,NULL,5,'Best purchase ever','A bit pricey but the quality justifies the cost.',0,1,110,'2025-01-10 16:14:00'),
(30,54,NULL,5,'Outstanding quality','Would definitely recommend to friends and family.',0,1,116,'2024-08-29 15:11:00'),
(11,12,NULL,5,'Five stars all day','Using it daily for the past few weeks with no problems.',1,1,78,'2024-07-17 01:06:00'),
(48,14,NULL,2,'Some issues','Great value for the price point.',0,1,14,'2022-05-26 07:46:00'),
(29,149,NULL,5,'Outstanding quality','The design is sleek and modern looking.',1,1,29,'2022-07-20 07:47:00'),
(27,52,NULL,5,'Outstanding quality','Quality matches the product description well.',1,1,113,'2024-06-11 04:13:00'),
(40,117,NULL,5,'Five stars all day','Works exactly as advertised, no issues so far.',1,1,45,'2023-07-07 06:21:00'),
(9,9,NULL,4,'Really impressed','Noticed a slight issue but customer service resolved it quickly.',1,1,58,'2024-05-06 05:48:00'),
(22,57,NULL,2,'Some issues','Runs quietly and efficiently in daily use.',0,1,70,'2023-04-16 02:26:00'),
(55,134,NULL,4,'Solid product','Purchased as a gift and the recipient loved it.',1,1,1,'2024-05-26 23:55:00'),
(16,64,NULL,5,'Outstanding quality','Purchased as a gift and the recipient loved it.',0,0,114,'2022-01-11 13:02:00'),
(3,121,NULL,4,'Really impressed','Performance is consistently smooth and reliable.',1,1,102,'2022-07-20 14:31:00'),
(16,22,NULL,4,'Really impressed','Performance is consistently smooth and reliable.',0,1,37,'2023-05-05 20:05:00'),
(2,123,NULL,4,'Great value','Arrived well packaged with no damage at all.',0,1,3,'2024-07-20 14:49:00'),
(9,104,NULL,5,'Five stars all day','Arrived well packaged with no damage at all.',1,1,80,'2022-05-25 12:57:00'),
(45,86,NULL,4,'Would buy again','Performance is consistently smooth and reliable.',0,1,78,'2025-01-15 18:50:00'),
(14,21,NULL,4,'Good quality overall','Delivery was fast and packaging was excellent.',1,0,46,'2022-04-16 03:24:00'),
(24,120,NULL,4,'Good quality overall','Battery life is impressive for extended use.',1,1,8,'2025-02-22 22:49:00'),
(14,36,NULL,1,'Poor quality','Good product but took a while to get used to.',1,1,120,'2025-04-03 22:13:00'),
(49,58,NULL,5,'Cannot recommend enough','A bit pricey but the quality justifies the cost.',1,1,8,'2024-02-03 11:28:00'),
(32,129,NULL,4,'Very happy with this','Exceeded my initial expectations on quality.',1,1,68,'2023-08-22 14:39:00'),
(24,17,NULL,5,'Worth every penny','Quality matches the product description well.',1,1,36,'2022-06-07 03:10:00'),
(18,29,NULL,4,'Very satisfied','Works exactly as advertised, no issues so far.',0,1,80,'2022-02-16 09:26:00'),
(44,139,NULL,2,'Minor problems','Battery life is impressive for extended use.',1,1,2,'2023-08-21 06:04:00'),
(2,60,NULL,3,'Nothing special','Performance is consistently smooth and reliable.',1,1,100,'2023-10-31 15:37:00'),
(43,136,NULL,3,'Fair enough','Arrived well packaged with no damage at all.',1,1,101,'2023-09-20 05:50:00'),
(17,59,NULL,4,'Would buy again','Delivery was fast and packaging was excellent.',1,1,21,'2022-11-26 22:34:00'),
(19,47,NULL,1,'Would not recommend','Great value for the price point.',1,1,40,'2025-03-22 04:28:00'),
(17,95,NULL,5,'Absolutely love it','The design is sleek and modern looking.',0,1,57,'2025-01-10 05:34:00'),
(20,32,NULL,2,'Has drawbacks','Exceeded my initial expectations on quality.',0,0,118,'2023-10-18 04:00:00'),
(48,140,NULL,1,'Terrible experience','Using it daily for the past few weeks with no problems.',1,1,120,'2025-03-20 21:09:00'),
(52,145,NULL,4,'Very satisfied','The design is sleek and modern looking.',1,1,115,'2022-03-24 04:43:00'),
(20,7,NULL,5,'Outstanding quality','Arrived well packaged with no damage at all.',1,1,77,'2023-02-04 18:33:00'),
(15,72,NULL,5,'Best purchase ever','Good product but took a while to get used to.',0,1,11,'2024-11-14 12:12:00'),
(32,82,NULL,4,'Really impressed','Battery life is impressive for extended use.',1,1,54,'2024-01-28 12:23:00'),
(1,73,NULL,5,'Cannot recommend enough','Arrived well packaged with no damage at all.',0,1,93,'2024-06-28 23:26:00'),
(52,114,NULL,5,'Blown away','Performance is consistently smooth and reliable.',1,1,11,'2022-10-22 06:19:00'),
(31,135,NULL,1,'Does not work well','Purchased as a gift and the recipient loved it.',0,1,52,'2023-07-14 13:11:00'),
(36,119,NULL,4,'Great value','Setup was straightforward and took only minutes.',1,1,70,'2024-10-01 01:52:00'),
(53,78,NULL,3,'Okay for the price','Exceeded my initial expectations on quality.',1,1,3,'2022-01-06 04:16:00'),
(20,121,NULL,5,'Cannot recommend enough','Performance is consistently smooth and reliable.',1,0,82,'2023-05-17 00:07:00'),
(49,71,NULL,4,'Very happy with this','Runs quietly and efficiently in daily use.',1,1,72,'2024-06-12 08:40:00'),
(44,122,NULL,1,'Does not work well','Battery life is impressive for extended use.',1,1,108,'2023-06-16 05:37:00'),
(4,38,NULL,5,'Exceeded expectations','Battery life is impressive for extended use.',1,1,53,'2023-12-31 01:18:00'),
(19,136,NULL,4,'Very happy with this','A bit pricey but the quality justifies the cost.',1,1,97,'2022-07-13 19:48:00'),
(11,140,NULL,5,'Five stars all day','Using it daily for the past few weeks with no problems.',1,1,46,'2022-07-16 17:37:00'),
(23,37,NULL,5,'Cannot recommend enough','Battery life is impressive for extended use.',0,1,117,'2022-11-30 03:13:00'),
(10,129,NULL,5,'Outstanding quality','Good product but took a while to get used to.',1,1,67,'2024-12-25 22:35:00'),
(45,30,NULL,5,'Best purchase ever','Would definitely recommend to friends and family.',0,0,61,'2023-12-15 09:44:00'),
(24,36,NULL,3,'Nothing special','Great value for the price point.',1,1,104,'2022-08-31 07:08:00'),
(55,37,NULL,4,'Would buy again','Works exactly as advertised, no issues so far.',1,0,54,'2022-08-17 02:01:00'),
(50,124,NULL,3,'Decent product','Setup was straightforward and took only minutes.',1,1,65,'2025-04-29 01:30:00'),
(8,65,NULL,5,'Cannot recommend enough','Really happy with this purchase overall.',0,1,117,'2023-02-25 18:57:00'),
(13,48,NULL,4,'Really impressed','Quality matches the product description well.',1,1,35,'2025-04-02 11:22:00'),
(11,129,NULL,3,'Mixed feelings','A bit pricey but the quality justifies the cost.',1,1,74,'2022-01-29 16:13:00'),
(46,50,NULL,1,'Would not recommend','Good product but took a while to get used to.',1,1,118,'2023-03-15 16:54:00'),
(46,122,NULL,5,'Exceeded expectations','Arrived well packaged with no damage at all.',1,1,106,'2023-12-28 12:27:00'),
(14,132,NULL,5,'Best purchase ever','The design is sleek and modern looking.',1,1,17,'2024-10-12 11:45:00'),
(19,143,NULL,4,'Very happy with this','The design is sleek and modern looking.',1,1,58,'2023-10-01 21:53:00'),
(29,58,NULL,4,'Would buy again','Performance is consistently smooth and reliable.',1,1,107,'2024-09-01 21:23:00'),
(12,4,NULL,1,'Not worth it','Would definitely recommend to friends and family.',1,1,86,'2022-06-24 03:09:00'),
(26,103,NULL,4,'Very happy with this','Great value for the price point.',1,0,43,'2023-02-15 19:54:00'),
(26,32,NULL,5,'Blown away','Exceeded my initial expectations on quality.',1,1,74,'2025-04-30 08:48:00'),
(51,103,NULL,5,'Blown away','Exceeded my initial expectations on quality.',1,1,58,'2022-08-10 03:16:00'),
(32,128,NULL,5,'Exceeded expectations','Really happy with this purchase overall.',1,1,8,'2024-10-17 21:01:00'),
(12,98,NULL,4,'Good quality overall','Works exactly as advertised, no issues so far.',1,1,97,'2022-06-06 21:48:00'),
(34,127,NULL,3,'Mixed feelings','Using it daily for the past few weeks with no problems.',1,1,33,'2025-01-15 10:51:00'),
(35,140,NULL,5,'Absolutely love it','Performance is consistently smooth and reliable.',0,1,57,'2023-10-07 12:28:00'),
(30,10,NULL,5,'Cannot recommend enough','Great value for the price point.',1,1,91,'2024-03-07 15:48:00'),
(8,146,NULL,4,'Very satisfied','Exceeded my initial expectations on quality.',1,1,7,'2024-03-12 08:31:00'),
(38,97,NULL,4,'Good quality overall','Using it daily for the past few weeks with no problems.',1,1,5,'2022-09-20 11:22:00'),
(52,150,NULL,5,'Five stars all day','Fits perfectly and is very comfortable.',1,1,45,'2024-04-23 11:03:00'),
(43,63,NULL,5,'Cannot recommend enough','Purchased as a gift and the recipient loved it.',1,1,111,'2023-09-17 03:21:00'),
(11,6,NULL,4,'Really impressed','Arrived well packaged with no damage at all.',1,1,65,'2024-05-12 08:01:00'),
(45,121,NULL,4,'Good quality overall','Fits perfectly and is very comfortable.',1,1,12,'2024-09-27 03:44:00'),
(44,53,NULL,5,'Five stars all day','Great value for the price point.',1,1,55,'2023-02-18 15:40:00'),
(55,20,NULL,3,'Mixed feelings','Using it daily for the past few weeks with no problems.',1,1,73,'2024-04-03 07:39:00'),
(48,24,NULL,4,'Very happy with this','Purchased as a gift and the recipient loved it.',1,1,102,'2024-12-23 15:27:00'),
(14,89,NULL,3,'Okay for the price','A bit pricey but the quality justifies the cost.',0,1,69,'2023-10-04 06:26:00'),
(26,65,NULL,4,'Very satisfied','Good product but took a while to get used to.',1,1,90,'2024-11-23 05:36:00'),
(32,55,NULL,4,'Very satisfied','Noticed a slight issue but customer service resolved it quickly.',0,1,78,'2024-06-07 18:46:00'),
(41,16,NULL,4,'Good quality overall','Arrived well packaged with no damage at all.',1,1,87,'2023-09-07 13:26:00'),
(21,17,NULL,4,'Works perfectly','Noticed a slight issue but customer service resolved it quickly.',0,1,32,'2023-04-29 12:15:00'),
(8,39,NULL,5,'Outstanding quality','Using it daily for the past few weeks with no problems.',1,1,55,'2024-05-14 20:57:00'),
(3,52,NULL,5,'Exceeded expectations','Really happy with this purchase overall.',1,1,84,'2025-02-01 05:41:00'),
(55,11,NULL,1,'Not worth it','Really happy with this purchase overall.',1,1,40,'2023-09-03 02:57:00'),
(27,94,NULL,4,'Very happy with this','Fits perfectly and is very comfortable.',0,1,17,'2023-04-29 03:36:00'),
(48,129,NULL,2,'Could be improved','Exceeded my initial expectations on quality.',0,1,15,'2023-10-04 10:53:00'),
(38,100,NULL,3,'Mixed feelings','Performance is consistently smooth and reliable.',1,1,27,'2023-07-17 14:26:00'),
(17,15,NULL,4,'Good quality overall','Would definitely recommend to friends and family.',1,1,87,'2023-05-20 08:56:00'),
(51,38,NULL,5,'Five stars all day','Using it daily for the past few weeks with no problems.',1,0,77,'2022-03-13 23:42:00'),
(52,14,NULL,4,'Solid product','Noticed a slight issue but customer service resolved it quickly.',1,1,89,'2024-01-14 21:07:00'),
(35,61,NULL,3,'Gets the job done','Really happy with this purchase overall.',0,1,117,'2023-06-08 09:05:00'),
(53,61,NULL,5,'Exceeded expectations','Arrived well packaged with no damage at all.',1,1,98,'2024-04-12 01:17:00'),
(6,126,NULL,4,'Works perfectly','The design is sleek and modern looking.',1,1,104,'2022-07-25 05:44:00'),
(17,130,NULL,5,'Blown away','Runs quietly and efficiently in daily use.',1,1,41,'2024-07-17 22:01:00'),
(49,14,NULL,4,'Great value','Arrived well packaged with no damage at all.',0,1,51,'2023-02-14 20:19:00'),
(21,148,NULL,5,'Exceeded expectations','Build quality feels solid and durable.',1,0,106,'2022-09-24 19:43:00');



-- -----------------------------------------------------------
-- TABLE 8: coupons
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS coupons (
    coupon_id       INT           UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    code            VARCHAR(30)   NOT NULL UNIQUE,
    description     VARCHAR(200)  DEFAULT NULL,
    discount_type   ENUM('percentage','fixed_amount','free_shipping') NOT NULL,
    discount_value  DECIMAL(10,2) NOT NULL COMMENT 'Percent or flat dollar off',
    min_order_value DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    max_uses        INT           DEFAULT NULL COMMENT 'NULL = unlimited uses',
    used_count      INT           NOT NULL DEFAULT 0,
    per_user_limit  TINYINT       NOT NULL DEFAULT 1,
    is_active       TINYINT(1)    NOT NULL DEFAULT 1,
    starts_at       DATETIME      NOT NULL,
    expires_at      DATETIME      DEFAULT NULL,
    created_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_code    (code),
    INDEX idx_active  (is_active),
    INDEX idx_expires (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------
-- SAMPLE DATA — 22 coupons
-- -----------------------------------------------------------
INSERT INTO coupons
  (code, description, discount_type, discount_value,
   min_order_value, max_uses, used_count, per_user_limit,
   is_active, starts_at, expires_at)
VALUES
('WELCOME10', '10% off for new customers',                   'percentage',  10.00,   0.00,  NULL,  1523,1,1,'2024-01-01', NULL),
('SAVE10',    '$10 off any order over $50',                  'fixed_amount',10.00,  50.00,  5000,   412,1,1,'2024-01-01','2024-12-31'),
('NEWUSER',   '5% off first order for new signups',          'percentage',   5.00,   0.00,  NULL,   988,1,1,'2024-01-01', NULL),
('FRANK50',   '$50 loyalty reward for Frank Miller',         'fixed_amount',50.00, 200.00,     1,     1,1,0,'2024-01-10','2024-02-10'),
('RACHEL30',  '$30 VIP loyalty reward for Rachel Robinson',  'fixed_amount',30.00, 300.00,     1,     1,1,0,'2024-02-01','2024-03-01'),
('SAVE25',    '$25 off orders over $200',                    'fixed_amount',25.00, 200.00,  2000,   318,1,1,'2024-01-01','2024-12-31'),
('VIP100',    '$100 off for VIP members on orders over $500','fixed_amount',100.00,500.00,   500,    87,1,1,'2024-01-01','2024-12-31'),
('JULIA40',   '$40 loyalty reward for Julia Gonzalez',       'fixed_amount',40.00, 400.00,     1,     1,1,0,'2024-03-01','2024-04-01'),
('TOM75',     '$75 platinum loyalty reward for Tom Parker',  'fixed_amount',75.00, 750.00,     1,     1,1,0,'2024-04-01','2024-05-01'),
('XAVIER50',  '$50 loyalty reward for Xavier Stewart',       'fixed_amount',50.00, 400.00,     1,     1,1,0,'2024-04-01','2024-05-01'),
('FREESHIP',  'Free shipping on all orders sitewide',        'free_shipping', 0.00,  0.00,  NULL,  2341,3,1,'2024-01-01', NULL),
('SUMMER20',  '20% off sitewide summer sale',                'percentage',  20.00, 100.00, 10000,   760,1,1,'2024-06-01','2024-08-31'),
('FLASH15',   '15% off flash sale - 24 hours only',          'percentage',  15.00,  50.00,  1000,   999,1,0,'2024-03-15','2024-03-16'),
('BACKTOSCHOOL','Back to school 12% off electronics',        'percentage',  12.00, 150.00,  3000,   445,2,1,'2024-08-01','2024-09-15'),
('BLACKFRI25','Black Friday 25% off everything sitewide',    'percentage',  25.00,   0.00,  NULL, 14320,5,1,'2024-11-29','2024-11-30'),
('CYBER20',   'Cyber Monday 20% off all tech products',      'percentage',  20.00,   0.00,  NULL,  8750,3,1,'2024-12-02','2024-12-02'),
('HOLIDAY15', 'Holiday season 15% off sitewide',             'percentage',  15.00,   0.00,  NULL,  5120,2,1,'2024-12-10','2024-12-25'),
('NEWYEAR10', 'New Year 10% off all orders',                 'percentage',  10.00,   0.00,  NULL,  3200,1,1,'2025-01-01','2025-01-07'),
('LOYALTY500','8% off when you have 500+ loyalty points',    'percentage',   8.00, 100.00,   200,    34,1,1,'2024-01-01', NULL),
('REFER20',   '$20 off for referring a friend to the store', 'fixed_amount',20.00,  50.00,  NULL,   892,1,1,'2024-01-01', NULL),
('APP10',     '10% off when ordering via mobile app',        'percentage',  10.00,   0.00,  NULL,  4210,3,1,'2024-01-01', NULL),
('BIRTHDAY15','15% off on your birthday month',              'percentage',  15.00,   0.00,  NULL,  1876,1,1,'2024-01-01', NULL);

-- -----------------------------------------------------------
-- VERIFICATION
-- -----------------------------------------------------------
SELECT COUNT(*) AS total_reviews FROM product_reviews;
SELECT COUNT(*) AS total_coupons FROM coupons;

-- Average rating per product category
SELECT c.name AS category,
       ROUND(AVG(r.rating), 2)  AS avg_rating,
       COUNT(r.review_id)       AS review_count
FROM product_reviews r
JOIN products  p ON p.product_id  = r.product_id
JOIN categories c ON c.category_id = p.category_id
WHERE r.is_approved = 1
GROUP BY c.category_id, c.name
ORDER BY avg_rating DESC;

-- Top 5 most helpful reviews
SELECT p.name AS product, r.title, r.rating, r.helpful_votes
FROM product_reviews r
JOIN products p ON p.product_id = r.product_id
ORDER BY r.helpful_votes DESC
LIMIT 5;

-- Active coupons with remaining uses
SELECT code, discount_type, discount_value,
       used_count,
       IF(max_uses IS NULL, 'Unlimited', CAST(max_uses - used_count AS CHAR)) AS remaining_uses,
       expires_at
FROM coupons
WHERE is_active = 1
ORDER BY used_count DESC;