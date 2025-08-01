from flask import Flask, session, render_template, request, jsonify,redirect, url_for
import sqlite3
import logging
import traceback
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'hello'

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

import sqlite3

def init_db():
    with sqlite3.connect('restaurant.db') as conn:
        cursor = conn.cursor()

        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Items (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                image TEXT NOT NULL,
                stock INTEGER DEFAULT 0,
                category TEXT NOT NULL -- Added category column
            
            )
        ''')

        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                item_id INTEGER NOT NULL,
                UNIQUE(username, item_id),
                FOREIGN KEY (item_id) REFERENCES Items (id)
            )
        ''')

       

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                item_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                total_price REAL NOT NULL,
                location TEXT NOT NULL,
                contact TEXT NOT NULL,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
             CREATE TABLE IF NOT EXISTS Specials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT NOT NULL,
                price REAL NOT NULL,
                image TEXT 
           )
       ''')
        conn.commit()
    


init_db()


    
categories = {
    'breakfast': {
        'items': [
            (1, 'Podi dosa', 'Spice up your feed with a sprinkle of dosa', 200,'items/podi-dosa.jpg' ),
            (2, 'Omelette', 'Freshly made omelette with veggies', 180, 'items/omelette.jpg'),
            (3, 'Aloo Paratha', 'Whole wheat flatbread stuffed with spiced mashed potatoes.', 250, 'items/aloo_paratha.jpg'),
            (4, 'Idli', 'Soft steamed rice and lentil cakes, served with sambar and chutney.', 150, 'items/idli.jpg'),
            (5, 'Dosa', 'Thin, crispy rice and lentil crepes, served with chutney and sambar.', 180, 'items/dosa.jpg'),
            (6, 'Vada', 'Deep-fried lentil doughnuts, served with chutney and sambar.', 160, 'items/vada.jpg'),
            (7, 'Upma', 'Savory semolina porridge cooked with vegetables and spices.', 180, 'items/upma.jpg'),
            (8, 'Poha', 'Flattened rice cooked with onions, tomatoes, and spices.', 140, 'items/poha.jpg'),
            (9, 'Puri Bhaji', 'Fried puffed Indian bread served with spicy potato curry.', 200, 'items/puri_bhaji.jpg'),
            (10, 'Paratha', 'Flaky Indian flatbread served with butter and side curries.', 240, 'items/paratha.jpg'),
            (11, 'Methi Thepla', 'Flatbread made with fenugreek leaves and whole wheat flour.', 230, 'items/methi_thepla.jpg'),
            (12, 'Egg Curry', 'Spiced egg curry served with paratha or rice.', 280, 'items/egg_curry.jpg'),
            (13, 'Litti Chokha', 'Baked wheat balls stuffed with sattu (gram flour), served with mashed potatoes, brinjal, and tomato curry.', 260, 'items/litti_chokha.jpg'),
            (14, 'Masala Dosa', 'A variety of dosa filled with spiced mashed potatoes and served with chutney and sambar.', 200, 'items/masala_dosa.jpg'),
            (15, 'Shakarkandi Tikki', 'Sweet potato patties served with mint chutney.', 180, 'items/shakarkandi_tikki.jpg'),
            (16, 'Keema Pav', 'Spiced minced meat served with bread rolls.', 320, 'items/keema_pav.jpg'),
            (17, 'Aloo Tikki', 'Potatoes and spices patties served with tamarind and mint chutney.', 200, 'items/aloo_tikki.jpg'),
            (18, 'Pesarattu', 'Moong dal crepes served with ginger and coconut chutney.', 220, 'items/pesarattu.jpg'),
            (19, 'Surti Locho', 'Fermented chickpea flour pancake garnished with sweet chutney and sev.', 190, 'items/surti_locho.jpg'),
            (20, 'Vegetable Uttapam', 'Thick rice and lentil pancake topped with vegetables like onions, tomatoes, and green chilies.', 210, 'items/vegetable_uttapam.jpg')
        ],
        'background_image': 'backgrounds/breakfast-bg.jpg'
},
    'lunch': {
        'items': [
        (21, 'Butter Chicken', 'Rich and creamy tomato-based chicken curry.', 300, 'items/butter_chicken.jpg'),
        (22, 'Paneer Butter Masala', 'Soft paneer cubes cooked in tomato and butter sauce.', 270, 'items/paneer_butter_masala.jpg'),
        (23, 'Chole', 'Spicy chickpea curry cooked with aromatic Indian spices.', 250, 'items/chole.jpg'),
        (24, 'Dal Tadka', 'Lentils tempered with onions, garlic, and spices.', 220, 'items/dal_tadka.jpg'),
        (25, 'Baingan Bharta', 'Mashed roasted eggplant mixed with spices and served with bread.', 230, 'items/baingan_bharta.jpg'),
        (26, 'Aloo Gobi', 'Potato and cauliflower cooked with spices and herbs.', 210, 'items/aloo_gobi.jpg'),
        (27, 'Rajma', 'Red kidney beans cooked in a spiced tomato sauce.', 260, 'items/rajma.jpg'),
        (28, 'Bhindi Masala', 'Okra cooked with onions, tomatoes, and spices.', 240, 'items/bhindi_masala.jpg'),
        (29, 'Matar Paneer', 'Paneer and green peas cooked in a creamy tomato-based sauce.', 280, 'items/matar_paneer.jpg'),
        (30, 'Lal Maas', 'Spicy Rajasthani mutton curry.', 300, 'items/lal_maas.jpg'),
        (31, 'Kadai Paneer', 'Paneer cooked with bell peppers and a spiced gravy.', 270, 'items/kadai_paneer.jpg'),
        (32, 'Fish Curry', 'Spicy fish curry with coconut and tamarind base.', 280, 'items/fish_curry.jpg'),
        (33, 'Malai Kofta', 'Fried vegetable or paneer balls cooked in creamy gravy.', 290, 'items/malai_kofta.jpg'),
        (34, 'Sambar Rice', 'Rice cooked with sambar spices and vegetables.', 250, 'items/sambar_rice.jpg'),
        (35, 'Hyderabadi Biryani', 'Aromatic rice cooked with marinated meat, rich spices, and yogurt.', 320, 'items/hyderabadi_biryani.jpg'),
        (36, 'Solkadhi', 'Coconut-based Konkani drink, typically served with rice dishes.', 180, 'items/solkadhi.jpg'),
        (37, 'Kachori Sabzi', 'Fried puff pastry stuffed with spicy lentil filling, served with potato curry.', 250, 'items/kachori_sabzi.jpg'),
        (38, 'Kerala Fish Molee', 'Fish cooked in coconut milk with spices.', 310, 'items/kerala_fish_molee.jpg'),
        (39, 'Goan Pork Vindaloo', 'Pork cooked in a fiery vindaloo sauce with a blend of spices.', 320, 'items/goan_pork_vindaloo.jpg'),
        (40, 'Chingri Malai Curry', 'Prawns cooked in coconut milk and Bengali spices.', 330, 'items/chingri_malai_curry.jpg')
    ],
    'background_image': 'backgrounds/lunch-bg.jpg'
},
   'dinner': {
    'items': [
        (41, 'Steak', 'Tender steak cooked to perfection with sides.', 400, 'items/steak.jpg'),
        (42, 'Grilled Salmon', 'Salmon fillet grilled with herbs and spices.', 350, 'items/grilled_salmon.jpg'),
        (43, 'Chicken Alfredo', 'Creamy Alfredo sauce served over pasta with chicken.', 300, 'items/chicken_alfredo.jpg'),
        (44, 'Mushroom Risotto', 'Creamy risotto cooked with mushrooms and Parmesan.', 280, 'items/mushroom_risotto.jpg'),
        (45, 'Baked Ziti', 'Pasta baked with marinara sauce and cheese.', 270, 'items/baked_ziti.jpg'),
        (46, 'Vegetarian Lasagna', 'Layered pasta with vegetables, cheese, and marinara.', 320, 'items/vegetarian_lasagna.jpg'),
        (47, 'Lamb Rogan Josh', 'Slow-cooked lamb curry in rich, spiced gravy.', 370, 'items/lamb_rogan_josh.jpg'),
        (48, 'Tuna Steak', 'Grilled tuna steak served with a tangy lemon sauce.', 340, 'items/tuna_steak.jpg'),
        (49, 'Caesar Salad', 'Crispy romaine lettuce tossed with Caesar dressing and croutons.', 250, 'items/caesar_salad.jpg'),
        (50, 'Pad Thai', 'Stir-fried rice noodles with shrimp, peanuts, and lime.', 290, 'items/pad_thai.jpg'),
        (51, 'Butter Chicken', 'Creamy tomato-based chicken curry with butter and spices.', 360, 'items/butter_chicken.jpg'),
        (52, 'Vegetable Biryani', 'Fragrant rice cooked with mixed vegetables and spices.', 280, 'items/vegetable_biryani.jpg'),
        (53, 'Seafood Paella', 'Spanish-style rice dish with seafood, saffron, and vegetables.', 390, 'items/seafood_paella.jpg'),
        (54, 'Chicken Tikka Masala', 'Tandoori chicken cooked in creamy tomato sauce.', 350, 'items/chicken_tikka_masala.jpg'),
        (55, 'Prawn Curry', 'Prawns cooked in a flavorful coconut and spice gravy.', 380, 'items/prawn_curry.jpg'),
        (56, 'Mutton Seekh Kebabs', 'Spiced minced mutton skewers cooked over charcoal.', 320, 'items/mutton_seekh_kebabs.jpg'),
        (57, 'Fish Curry', 'Traditional Indian fish curry with a rich, spiced sauce.', 330, 'items/fish_curry.jpg'),
        (58, 'Chicken Shawarma', 'Grilled chicken wrapped in pita with tahini sauce.', 310, 'items/chicken_shawarma.jpg'),
        (59, 'Hakka Noodles', 'Stir-fried Chinese noodles with vegetables and sauces.', 270, 'items/hakka_noodles.jpg'),
        (60, 'Greek Moussaka', 'Layered eggplant and minced meat dish with béchamel sauce.', 350, 'items/greek_moussaka.jpg')
    ],
    'background_image': 'backgrounds/dinner-bg.jpg'
},
    'shakes': {
    'items': [
        (61, 'Chocolate Shake', 'Rich chocolate shake topped with whipped cream.', 150, 'items/chocolate_shake.jpg'),
        (62, 'Strawberry Shake', 'Fresh strawberry shake with a hint of vanilla.', 140, 'items/strawberry_shake.jpg'),
        (63, 'Banana Nut Shake', 'Creamy banana shake with nuts and honey.', 160, 'items/banana_nut_shake.jpg'),
        (64, 'Mango Shake', 'Refreshing mango shake with a dash of saffron.', 150, 'items/mango_shake.jpg'),
        (65, 'Coffee Shake', 'Strong coffee-infused shake with chocolate chips.', 170, 'items/coffee_shake.jpg'),
        (66, 'Vanilla Shake', 'Classic vanilla shake with a rich, creamy texture.', 140, 'items/vanilla_shake.jpg'),
        (67, 'Blueberry Shake', 'Smooth blueberry shake with a touch of yogurt.', 150, 'items/blueberry_shake.jpg'),
        (68, 'Pistachio Shake', 'Nutty pistachio shake with cream and nuts topping.', 180, 'items/pistachio_shake.jpg'),
        (69, 'Peach Shake', 'Sweet peach shake with a hint of citrus.', 160, 'items/peach_shake.jpg'),
        (70, 'Oreo Shake', 'Oreos blended into a rich milkshake with chocolate syrup.', 170, 'items/oreo_shake.jpg'),
        (71, 'Caramel Shake', 'Creamy caramel shake with a drizzle of caramel sauce.', 170, 'items/caramel_shake.jpg'),
        (72, 'Chocolate Banana Shake', 'Banana and chocolate blended into a luscious shake.', 160, 'items/chocolate_banana_shake.jpg'),
        (73, 'Rose Milk Shake', 'Fragrant rose syrup mixed with milk for a refreshing taste.', 140, 'items/rose_milk_shake.jpg'),
        (74, 'Gingerbread Shake', 'Gingerbread-flavored shake with spices and whipped cream.', 180, 'items/gingerbread_shake.jpg'),
        (75, 'Almond Shake', 'Nutty almond shake blended with milk and honey.', 170, 'items/almond_shake.jpg'),
        (76, 'Coconut Shake', 'Creamy coconut milk shake with grated coconut topping.', 150, 'items/coconut_shake.jpg'),
        (77, 'Chikoo Shake', 'Chikoo (Sapota) blended into a smooth, sweet shake.', 160, 'items/chikoo_shake.jpg'),
        (78, 'Tropical Fruit Shake', 'A blend of tropical fruits like pineapple, mango, and papaya.', 170, 'items/tropical_fruit_shake.jpg'),
        (79, 'Espresso Shake', 'Intense coffee flavor shake with a hint of chocolate.', 180, 'items/espresso_shake.jpg'),
        (80, 'Matcha Shake', 'Green tea-based shake with a rich matcha flavor.', 180, 'items/matcha_shake.jpg')
    ],
    'background_image': 'backgrounds/shakes-bg.jpg'
},
    'cool drinks': {
    'items': [
        (81, 'Lemon Mint Mojito', 'Refreshing mint and lemon cooler.', 120, 'items/lemon_mint_mojito.jpg'),
        (82, 'Cold Coffee', 'Chilled coffee with ice cream and whipped cream.', 140, 'items/cold_coffee.jpg'),
        (83, 'Iced Tea', 'Sweetened iced tea with mint and lemon.', 110, 'items/iced_tea.jpg'),
        (84, 'Fruit Punch', 'Fruity blend of juices with a hint of soda.', 130, 'items/fruit_punch.jpg'),
        (85, 'Virgin Mojito', 'Mint, lime, and soda served chilled.', 125, 'items/virgin_mojito.jpg'),
        (86, 'Berry Smoothie', 'Berry smoothie with a mix of fresh berries.', 140, 'items/berry_smoothie.jpg'),
        (87, 'Mango Lassi', 'Traditional mango yogurt drink with cardamom.', 150, 'items/mango_lassi.jpg'),
        (88, 'Guava Cooler', 'Chilled guava drink with lemon and mint.', 130, 'items/guava_cooler.jpg'),
        (89, 'Apple Cider', 'Sparkling apple cider with cinnamon.', 150, 'items/apple_cider.jpg'),
        (90, 'Cucumber Cooler', 'Cool cucumber drink with lemon and mint.', 120, 'items/cucumber_cooler.jpg'),
        (91, 'Pineapple Coconut Cooler', 'Tropical pineapple with coconut water and mint.', 140, 'items/pineapple_coconut_cooler.jpg'),
        (92, 'Tamarind Drink', 'Tangy tamarind cooler with sugar and spices.', 130, 'items/tamarind_drink.jpg'),
        (93, 'Peach Iced Tea', 'Peach-infused iced tea with a sweet flavor.', 140, 'items/peach_iced_tea.jpg'),
        (94, 'Strawberry Lemonade', 'Sweet strawberry lemonade with fresh lemon slices.', 140, 'items/strawberry_lemonade.jpg'),
        (95, 'Lychee Iced Tea', 'Refreshing lychee iced tea with mint.', 130, 'items/lychee_iced_tea.jpg'),
        (96, 'Ginger Ale', 'Sparkling ginger ale with a spicy kick.', 120, 'items/ginger_ale.jpg'),
        (97, 'Passion Fruit Cooler', 'Exotic passion fruit drink with a hint of vanilla.', 140, 'items/passion_fruit_cooler.jpg'),
        (98, 'Orange Mojito', 'Refreshing orange and mint cooler.', 125, 'items/orange_mojito.jpg'),
        (99, 'Coconut Water', 'Chilled coconut water served with a splash of lime.', 100, 'items/coconut_water.jpg'),
        (100, 'Ginger Lemon Punch', 'Spicy ginger punch with fresh lemon.', 140, 'items/ginger_lemon_punch.jpg')
    ],
    'background_image': 'backgrounds/cool_drinks-bg.jpg'
},
    'fresh juice': {
    'items': [
         (101, 'Orange Juice', 'Freshly squeezed orange juice.', 100, 'items/orange_juice.jpg'),
        (102, 'Apple Juice', 'Refreshing apple juice served cold.', 90, 'items/apple_juice.jpg'),
        (103, 'Pineapple Juice', 'Tropical pineapple juice with a sweet flavor.', 110, 'items/pineapple_juice.jpg'),
        (104, 'Watermelon Juice', 'Cool watermelon juice with mint garnish.', 120, 'items/watermelon_juice.jpg'),
        (105, 'Ginger Lemon Juice', 'Spicy ginger lemon juice for a refreshing experience.', 130, 'items/ginger_lemon_juice.jpg'),
        (106, 'Carrot Juice', 'Fresh carrot juice with a hint of orange.', 100, 'items/carrot_juice.jpg'),
        (107, 'Beetroot Juice', 'Nutritious beetroot juice with a slight earthy taste.', 110, 'items/beetroot_juice.jpg'),
        (108, 'Guava Juice', 'Sweet and tangy guava juice with a citrusy twist.', 130, 'items/guava_juice.jpg'),
        (109, 'Mango Juice', 'Smooth mango juice with a refreshing touch.', 120, 'items/mango_juice.jpg'),
        (110, 'Pomegranate Juice', 'Rich pomegranate juice with a sweet and tangy flavor.', 140, 'items/pomegranate_juice.jpg'),
        (111, 'Lemon Mint Juice', 'Cool lemon and mint juice with a slight sweetness.', 110, 'items/lemon_mint_juice.jpg'),
        (112, 'Apple Carrot Juice', 'Healthy blend of apple and carrot juice.', 120, 'items/apple_carrot_juice.jpg'),
        (113, 'Strawberry Banana Juice', 'Creamy strawberry and banana juice blend.', 130, 'items/strawberry_banana_juice.jpg'),
        (114, 'Papaya Juice', 'Tropical papaya juice with a sweet, smooth taste.', 140, 'items/papaya_juice.jpg'),
        (115, 'Cucumber Mint Juice', 'Cool cucumber juice with a refreshing mint flavor.', 110, 'items/cucumber_mint_juice.jpg'),
        (116, 'Tamarind Juice', 'Tangy tamarind juice with a hint of spice.', 130, 'items/tamarind_juice.jpg'),
        (117, 'Kiwi Juice', 'Exotic kiwi juice with a tangy, sweet flavor.', 140, 'items/kiwi_juice.jpg'),
        (118, 'Lychee Juice', 'Sweet lychee juice with a delicate floral aroma.', 130, 'items/lychee_juice.jpg'),
        (119, 'Watermelon Mint Juice', 'Refreshing watermelon juice with a cool mint twist.', 120, 'items/watermelon_mint_juice.jpg'),
        (120, 'Passion Fruit Juice', 'Exotic passion fruit juice with a tangy flavor.', 140, 'items/passion_fruit_juice.jpg')
    ],
    'background_image': 'backgrounds/fresh_juices-bg.jpg'
},
    'snacks': {
    'items': [
        (121, 'Samosa', 'Crispy pastry filled with spiced potatoes and peas.', 100, 'items/samosa.jpg'),
        (122, 'Vada Pav', 'Spicy potato fritters in a soft bun, served with chutney.', 120, 'items/vada_pav.jpg'),
        (123, 'Aloo Tikki', 'Pan-fried mashed potato patties with spices.', 150, 'items/aloo_tikki.jpg'),
        (124, 'Pani Puri', 'Puffed wheat balls filled with tangy water, potatoes, and chickpeas.', 80, 'items/pani_puri.jpg'),
        (125, 'Bhel Puri', 'Crispy puffed rice mixed with tangy chutneys, vegetables, and sev.', 120, 'items/bhel_puri.jpg'),
        (126, 'Dhokla', 'Steamed fermented rice and chickpea cake, served with chutney.', 140, 'items/dhokla.jpg'),
        (127, 'Papdi Chaat', 'Crispy flatbreads topped with chutneys, yogurt, and spices.', 130, 'items/papdi_chaat.jpg'),
        (128, 'Mirchi Bajji', 'Stuffed and deep-fried green chilies, served with chutney.', 160, 'items/mirchi_bajji.jpg'),
        (129, 'Aloo Bonda', 'Spiced mashed potatoes coated in a chickpea batter, fried.', 140, 'items/aloo_bonda.jpg'),
        (130, 'Gujarati Khandvi', 'Steamed gram flour rolls, garnished with coconut and spices.', 150, 'items/khandvi.jpg'),
        (131, 'Kesari Bath', 'Sweet semolina pudding flavored with saffron and dry fruits.', 170, 'items/kesari_bath.jpg'),
        (132, 'Banana Chips', 'Crispy fried banana slices flavored with spices.', 120, 'items/banana_chips.jpg'),
        (133, 'Chana Masala', 'Spiced chickpeas cooked in a rich tomato-based gravy.', 180, 'items/chana_masala.jpg'),
        (134, 'Rawa Idli', 'Steamed rice and semolina cakes served with chutney and sambar.', 160, 'items/rawa_idli.jpg'),
        (135, 'Papad', 'Crispy fried lentil wafer, served with a variety of accompaniments.', 100, 'items/papad.jpg'),
        (136, 'Methi Thepla', 'Flatbread made with fenugreek leaves and whole wheat flour.', 180, 'items/methi_thepla.jpg'),
        (137, 'Cheese Pav Bhaji', 'Spiced mashed vegetables served with buttered pav.', 200, 'items/cheese_pav_bhaji.jpg'),
        (138, 'Bhajiya', 'Deep-fried vegetable fritters served with chutney.', 150, 'items/bhajiya.jpg'),
        (139, 'Paneer Pakora', 'Spiced paneer slices coated in chickpea flour batter, deep-fried.', 170, 'items/paneer_pakora.jpg'),
        (140, 'Moong Dal Chilla', 'Thin lentil pancakes served with chutney.', 150, 'items/moong_dal_chilla.jpg'),
        (141, 'Kachori', 'Spicy lentil-stuffed deep-fried pastry, served with chutney.', 150, 'items/kachori.jpg'),
        (142, 'Gujrati Sev Usal', 'Steamed gram flour noodles mixed with spiced curry.', 160, 'items/sev_usal.jpg'),
        (143, 'Aloo Chaat', 'Spiced mashed potatoes with tangy chutneys and spices.', 140, 'items/aloo_chaat.jpg'),
        (144, 'Punugulu', 'Deep-fried batter cakes served with chutney.', 150, 'items/punugulu.jpg'),
        (145, 'Kala Chana Chaat', 'Spiced black chickpeas served with chutney and onions.', 160, 'items/kala_chana_chaat.jpg'),
    ],
    'background_image': 'backgrounds/indian_snacks-bg.jpg'
},

    'western dishes': {
    'items': [
        (146, 'Burgers', 'Juicy beef or chicken burger with fries and sauce.', 250, 'items/burger.jpg'),
        (147, 'Pasta Primavera', 'Pasta with mixed vegetables in a creamy sauce.', 260, 'items/pasta_primavera.jpg'),
        (148, 'Grilled Chicken Sandwich', 'Grilled chicken with lettuce, tomato, and mayo on a bun.', 220, 'items/grilled_chicken_sandwich.jpg'),
        (149, 'Fish and Chips', 'Crispy fried fish served with French fries.', 280, 'items/fish_and_chips.jpg'),
        (150, 'Veggie Burger', 'Vegetable patty burger with cheese, lettuce, and sauce.', 240, 'items/veggie_burger.jpg'),
        (151, 'Caesar Salad', 'Crispy romaine lettuce tossed with Caesar dressing and croutons.', 250, 'items/caesar_salad.jpg'),
        (152, 'Spaghetti Bolognese', 'Spaghetti with a rich meat-based sauce.', 280, 'items/spaghetti_bolognese.jpg'),
        (153, 'Quiche Lorraine', 'Savory pastry with bacon, eggs, and cheese.', 260, 'items/quiche_lorraine.jpg'),
        (154, 'Vegetable Risotto', 'Creamy risotto cooked with a variety of vegetables.', 270, 'items/vegetable_risotto.jpg'),
        (155, 'Beef Stroganoff', 'Beef cooked in a creamy, tangy sauce served over pasta.', 300, 'items/beef_stroganoff.jpg'),
        (156, 'Chicken Parmesan', 'Breaded chicken topped with marinara sauce and cheese.', 290, 'items/chicken_parmesan.jpg'),
        (157, 'Seafood Linguine', 'Pasta with shrimp, clams, and white wine sauce.', 310, 'items/seafood_linguine.jpg'),
        (158, 'Stuffed Bell Peppers', 'Bell peppers stuffed with rice, cheese, and herbs.', 270, 'items/stuffed_bell_peppers.jpg'),
        (159, 'Chicken Piccata', 'Breaded chicken breast with capers and lemon sauce.', 280, 'items/chicken_piccata.jpg'),
        (160, 'Pulled Pork Sandwich', 'Slow-cooked pulled pork in a bun with BBQ sauce.', 270, 'items/pulled_pork_sandwich.jpg'),
        (161, 'Garlic Butter Shrimp', 'Shrimp cooked in garlic butter sauce with herbs.', 280, 'items/garlic_butter_shrimp.jpg'),
        (162, 'Macaroni and Cheese', 'Classic pasta baked with creamy cheese sauce.', 240, 'items/macaroni_cheese.jpg'),
        (163, 'Beef Tacos', 'Soft shell tacos filled with seasoned beef and toppings.', 250, 'items/beef_tacos.jpg'),
        (164, 'Chicken Tortilla Soup', 'Hearty chicken soup with tortillas and cheese.', 260, 'items/chicken_tortilla_soup.jpg'),
        (165, 'Baked Macaroni', 'Macaroni baked with cheese and a touch of spices.', 230, 'items/baked_macaroni.jpg')
    ],
    'background_image': 'backgrounds/western_dishes-bg.jpg'
}
}
special_dishes = [
    {"name": "Spicy Chicken Wings", "description": "Crispy wings tossed in hot sauce.", "price": 299, "image": "chicken_wings.jpg"},
    {"name": "Garlic Butter Chicken", "description": "Succulent chicken cooked in garlic butter sauce.", "price": 349, "image": "garlic_butter_chicken.jpg"},
    {"name": "Honey BBQ Chicken", "description": "Sweet and smoky BBQ chicken.", "price": 329, "image": "honey_bbq_chicken.jpg"},
    {"name": "Lemon Herb Chicken", "description": "Zesty lemon and herb-marinated chicken.", "price": 399, "image": "lemon_herb_chicken.jpg"},
    {"name": "Grilled Chicken", "description": "Perfectly grilled chicken.", "price": 379, "image": "grilled_chicken.jpg"},
    {"name": "Chicken Alfredo", "description": "Creamy Alfredo pasta with grilled chicken.", "price": 499, "image": "chicken_alfredo.jpg"},
    {"name": "Teriyaki Chicken", "description": "Savory grilled chicken in teriyaki glaze.", "price": 419, "image": "teriyaki_chicken.jpg"},
    {"name": "Chicken Tikka Masala", "description": "Authentic Indian-style chicken curry.", "price": 459, "image": "chicken_tikka_masala.jpg"},
    {"name": "Fried Chicken Bucket", "description": "Golden, crispy fried chicken pieces.", "price": 699, "image": "fried_chicken_bucket.jpg"},
    {"name": "Chicken Caesar Salad", "description": "Fresh salad with grilled chicken and Caesar dressing.", "price": 349, "image": "chicken_caesar_salad.jpg"},
    {"name": "Chicken Korma", "description": "Rich and creamy chicken korma.", "price": 399, "image": "chicken_korma.jpg"},
    {"name": "Peri Peri Grilled Chicken", "description": "Spicy grilled chicken with peri peri sauce.", "price": 449, "image": "peri_peri_chicken.jpg"},
    {"name": "Chicken Biryani", "description": "Flavorful basmati rice and tender chicken.", "price": 349, "image": "chicken_biryani.jpg"},
    {"name": "Mughlai Chicken", "description": "Luxurious Mughlai-style chicken curry.", "price": 479, "image": "mughlai_chicken.jpg"},
    {"name": "Chicken Seekh Kebabs", "description": "Juicy skewered chicken kebabs.", "price": 299, "image": "chicken_seekh_kebabs.jpg"},
]
def insert_special_dishes():
    try:
        with sqlite3.connect('restaurant.db', timeout=10) as conn:
            cursor = conn.cursor()

            # Clear the Specials table before inserting new data
            cursor.execute('DELETE FROM Specials')

            # Insert each special dish into the Specials table
            for dish in special_dishes:
                cursor.execute('''
                    INSERT INTO Specials (name, description, price, image)
                    VALUES (?, ?, ?, ?)
                ''', (dish['name'], dish['description'], dish['price'], dish['image']))
            
            conn.commit()
            print("Special dishes inserted successfully.")
    except sqlite3.Error as e:
        print(f"Error inserting special dishes: {e}")

# Call the function to insert the special dishes into the Specials table
insert_special_dishes() 



def populate_items_table(categories):
    """Populate the Items table with data from the categories dictionary."""
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()

    # Insert items from categories into the Items table
    for category in categories.values():
        for item in category['items']:
            cursor.execute('''
                INSERT OR IGNORE INTO Items (id, name, description, price, image)
                VALUES (?, ?, ?, ?, ?)
            ''', item)

    conn.commit()
    conn.close()


def is_item_in_favorites(item_id, user_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Favorites WHERE item_id = ? AND user_id = ?", (item_id, user_id))
        return cursor.fetchone() is not None


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/menu/<category>')
def menu(category):
    print("Category:", category)  
    if category in categories:
        items = categories[category]['items']
        print("Items:", items)  
        return render_template(
            'category_view.html',
            items=items,
            background_image=categories[category]['background_image'],
            category=category.capitalize(),
            username=session.get('username') 
        )
    else:
        return "Category not found", 404


@app.route('/login', methods=['GET', 'POST'])
def login():
    from flask import redirect, url_for  

    if request.method == 'POST':
        username = request.form['username']
        role = request.form['role']

        
        session['username'] = username
        session['role'] = role

        if role == 'manager':
            password = request.form['password']
            if password == 'restaurant manager':
                return redirect(url_for('manager_dashboard', username=username))
            else:
                return render_template('login.html', error="Invalid password for manager.")
        elif role == 'user':
            return redirect(url_for('user_dashboard', username=username))
        else:
            return render_template('login.html', error="Invalid role selected.")

    return render_template('login.html')

@app.route('/favorites/<username>')
def favorites(username):
    try:
        conn = sqlite3.connect('restaurant.db')
        cursor = conn.cursor()

        
        cursor.execute('''
            SELECT items.id, items.name, items.description, items.price, items.image, items.stock
            FROM favorites
            JOIN items ON favorites.item_id = items.id
            WHERE favorites.username = ?
        ''', (username,))
        
        favorite_items = cursor.fetchall()
        conn.close()

      
        return render_template('favorites.html', username=username, favorite_items=favorite_items)
    except Exception as e:
        logging.error(f"Error fetching favorites for {username}: {e}")
        return jsonify({"message": "Error fetching favorites.", "error": str(e)}), 500





@app.route('/user_dashboard/<username>')
def user_dashboard(username):
    categories = {
        'breakfast': 'images/breakfast.jpg',
        'lunch': 'images/lunch.jpg',
        'dinner': 'images/dinner.jpg',
        'shakes': 'images/shakes.jpg',
        'cool drinks': 'images/cool-drinks.jpg',
        'fresh juice': 'images/fresh-juice.jpg',
        'western dishes': 'images/western-dishes.jpg',
        'snacks': 'images/snacks.jpg',
    }

    try:
        conn = sqlite3.connect('restaurant.db')
        cursor = conn.cursor()

        
        cursor.execute('''
            SELECT items.id, items.name, items.description, items.price, items.image
            FROM Favorites
            JOIN Items ON Favorites.item_id = Items.id
            WHERE Favorites.username = ?
        ''', (username,))
        
        favorite_items = cursor.fetchall()
        conn.close()

        return render_template('user_dashboard.html', 
                               username=username, 
                               categories=categories, 
                               favorites=favorite_items)
    except Exception as e:
        logging.error(f"Error fetching favorites for dashboard: {e}")
        return jsonify({"message": "Error fetching favorites.", "error": str(e)}), 500

@app.route('/manager_dashboard/<username>')
def manager_dashboard(username):
    try:
        categories = {
            'breakfast': 'images/breakfast.jpg',
            'lunch': 'images/lunch.jpg',
            'dinner': 'images/dinner.jpg',
            'shakes': 'images/shakes.jpg',
            'cool drinks': 'images/cool-drinks.jpg',
            'fresh juice': 'images/fresh-juice.jpg',
            'western dishes': 'images/western-dishes.jpg',
            'snacks': 'images/snacks.jpg',
        }
        
        return render_template('manager_dashboard.html', username=username, categories=categories)

    except Exception as e:
        logging.error(f"Error fetching categories for manager dashboard: {e}")
        return jsonify({"message": "Error fetching categories.", "error": str(e)}), 500


@app.route('/manager_category_view/<username>/<category>')
def manager_category_view(username, category):
    conn = None
    try:
        conn = sqlite3.connect('restaurant.db')  
        category_data = categories.get(category, None)
        
        if category_data is None:
            raise ValueError(f"Category '{category}' not found.")

        items = category_data['items']
        
    except Exception as e:
        logging.error(f"Error fetching items for category {category}: {e}")
        return jsonify({"message": "Error fetching items.", "error": str(e)}), 500
    finally:
        if conn:
            conn.close() 

    return render_template('manager_category_view.html', username=username, category=category, items=items)


@app.route('/add_new_dishes')
def add_new_dishes():
    try:
       
        conn = sqlite3.connect('restaurant.db')
        cursor = conn.cursor()

        

        cursor.execute('''
            INSERT INTO Items (name, description, price, image)
            VALUES (?, ?, ?, ?)
        ''', (new_dish_name, new_dish_description, new_dish_price, new_dish_image))

        conn.commit()
        
    except Exception as e:
        logging.error(f"Database connection error: {e}")
       
        return jsonify({"message": "Error adding new dish.", "error": str(e)}), 500
    
    finally:
        if conn:
            conn.close()

    return "Add New Dishes"

@app.route('/update_item/<int:item_id>', methods=['GET', 'POST'])
def update_item(item_id):
    try:
        conn = sqlite3.connect('restaurant.db')
        cursor = conn.cursor()

        if request.method == 'POST':
            
            new_name = request.form.get('name')
            new_description = request.form.get('description')
            new_price = request.form.get('price')
            new_image = request.form.get('image')
            new_stock = request.form.get('stock')

            cursor.execute('''
                UPDATE Items
                SET name = ?, description = ?, price = ?, image = ?, stock = ?
                WHERE id = ?
            ''', (new_name, new_description, new_price, new_image, new_stock, item_id))

            conn.commit()
            return redirect(url_for('manager_category_view', username='karthiga', category='breakfast'))

        else:
            
            cursor.execute('SELECT name, description, price, image, stock FROM Items WHERE id = ?', (item_id,))
            item = cursor.fetchone()

            if not item:
                return jsonify({"message": "Item not found."}), 404

            # Item details
            item_data = {
                "name": item[0],
                "description": item[1],
                "price": item[2],
                "image": item[3],
                "stock": item[4],
            }

    except Exception as e:
        logging.error(f"Error fetching or updating item {item_id}: {e}")
        return jsonify({"message": "Error processing request.", "error": str(e)}), 500

    finally:
        if conn:
            conn.close()

    return render_template('update_item.html', item=item_data)

@app.route('/special_dishes/<username>')
def special_dishes(username):
    try:
        conn = sqlite3.connect('restaurant.db')
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM Specials')
        dishes = cursor.fetchall()
        conn.close()

        if not dishes:
            return "No special dishes available", 404

        dishes = [
            {
                "id": dish[0],
                "name": dish[1],
                "description": dish[2],
                "price": dish[3],
                "image": dish[4]
            } for dish in dishes
        ]
        
        return render_template('special_dishes.html', username=username, dishes=dishes)

    except Exception as e:
        return f"An error occurred: {str(e)}", 500


@app.route('/order/<username>/<dish_id>', methods=['GET', 'POST'])
def order(username,dish_id):
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Specials WHERE id = ?', (dish_id,))
    dish = cursor.fetchone()
    conn.close()

    error = None  # To store error messages

    if request.method == 'POST':
        username = request.form['username']
        contact = request.form['contact']
        location = request.form['location']
        try:
            quantity = int(request.form['quantity'])
        except ValueError:
            quantity = 0  # Default to 0 if invalid input

        if quantity < 1:
            error = "Please select a quantity of 1 or more to place an order."
        else:
            total_price = quantity * dish[3]  # Calculate total price

            # Insert the order into the Orders table
            try:
                with sqlite3.connect('restaurant.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO Orders (username, item_name, quantity, total_price, location, contact)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (username, dish[1], quantity, total_price, location, contact))
                    conn.commit()
                return redirect(url_for('order_confirmation', order_id=cursor.lastrowid))
            except sqlite3.Error as e:
                print(f"Error inserting order: {e}")
                error = "An error occurred while placing the order. Please try again."

    return render_template('order_form.html', dish=dish, error=error, item_id=dish_id)


@app.route('/order_confirmation/<int:order_id>')
def order_confirmation(order_id):
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Orders WHERE id = ?', (order_id,))
    order = cursor.fetchone()
    conn.close()

    return render_template('order_confirmation.html', order=order)




@app.route('/add_to_favorites/<username>/<int:item_id>', methods=['POST'])
def add_to_favorites(username, item_id):
    try:
        with sqlite3.connect('restaurant.db') as conn:
            cursor = conn.cursor()
            
            
            cursor.execute('''
                INSERT INTO Favorites (username, item_id)
                VALUES (?, ?)
            ''', (username, item_id))
            conn.commit()
        
        return jsonify({"success": True, "message": "Item added to favorites successfully."}), 200
    except sqlite3.IntegrityError:
       
        return jsonify({"success": False, "message": "Item already in favorites."}), 400
    except sqlite3.Error as e:
        
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500
    except Exception as e:
        
        return jsonify({"success": False, "message": "An unexpected error occurred.", "error": str(e)}), 500



@app.route('/favorites/<username>', methods=['GET'])
def view_favorites(username):
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT items.id, items.name, items.description, items.price, items.image_path
                FROM favorites
                JOIN items ON favorites.item_id = items.id
                WHERE favorites.username = ?
            ''', (username,))
            favorite_items = cursor.fetchall()

        return render_template('favorites.html', username=username, favorite_items=favorite_items)

    except Exception as e:
        logging.error(f"Error retrieving favorites for {username}: {e}", exc_info=True)
        return jsonify({"message": "Error retrieving favorites", "error": str(e)}), 500

def find_item_by_id(item_id):
    for cat_items in categories.values():
        for item in cat_items['items']:
            if item[0] == item_id:
                return item
    return None




@app.route('/past_orders/<username>')
def past_orders(username):
    with sqlite3.connect('restaurant.db') as conn:
        cursor = conn.cursor()

        
        cursor.execute('''
            SELECT item_name, quantity, total_price, order_date
            FROM Orders
            WHERE username = ?
            ORDER BY order_date DESC
        ''', (username,))
        orders = cursor.fetchall()

    return render_template('past_orders.html', username=username, orders=orders)

@app.route('/category_view/<username>/<category>', methods=['GET'])
def category_view(username, category):
    try:
        conn = sqlite3.connect('restaurant.db')
        cursor = conn.cursor()

        
        cursor.execute('SELECT id, name, description, price, image, stock FROM Items WHERE category = ?', (category,))
        items = cursor.fetchall()

        conn.close()

    except Exception as e:
        logging.error(f"Error fetching items for category {category}: {e}")
        return jsonify({"message": "Error fetching items.", "error": str(e)}), 500

    return render_template('category_view.html', username=username, category=category, items=items)
@app.route('/remove_from_favorites/<username>/<int:item_id>', methods=['POST'])
def remove_from_favorites(username, item_id):
    try:
        conn = sqlite3.connect('restaurant.db')
        cursor = conn.cursor()

       
        cursor.execute('''
            DELETE FROM Favorites
            WHERE username = ? AND item_id = ?
        ''', (username, item_id))

        conn.commit()

        if cursor.rowcount > 0:
            return redirect(url_for('favorites', username=username))  
        else:
            return redirect(url_for('favorites', username=username, error="Item not found in favorites."))  
    except sqlite3.Error as e:
        return redirect(url_for('favorites', username=username, error="An error occurred while removing the item."))  
    finally:
        conn.close()

@app.route('/confirm_order/<username>/<int:item_id>', methods=['GET'])
def confirm_order(username, item_id):
    quantity = int(request.args.get('quantity', 1))  

   
    with sqlite3.connect('restaurant.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT name, price FROM Items WHERE id = ?', (item_id,))
        item = cursor.fetchone()

    if not item:
        return "Item not found", 404

    item_name, price = item
    total_price = quantity * price

    return render_template('confirm_order.html', username=username, item_id=item_id, 
                           item_name=item_name, price=price, quantity=quantity, total_price=total_price)

from flask import render_template

@app.route('/place_order/<username>/<int:item_id>', methods=['POST'])
def place_order(username, item_id):
    location = request.form['location']
    contact = request.form['contact']
    quantity = request.form.get('quantity', 1, type=int)

    # Fetch item details
    with sqlite3.connect('restaurant.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT name, price FROM Items WHERE id = ?', (item_id,))
        item = cursor.fetchone()

    if not item:
        return "Item not found", 404

    item_name, price = item
    total_price = quantity * price
    order_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Insert the order into the database
    with sqlite3.connect('restaurant.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Orders (username, item_name, quantity, total_price, location, contact, order_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (username, item_name, quantity, total_price, location, contact, order_date))
        conn.commit()

    # Render the order confirmation page
    return render_template('place_order.html', username=username, item_name=item_name, 
                           price=price, quantity=quantity, total_price=total_price, 
                           location=location, contact=contact, order_date=order_date)




def get_user_favorites(username):
    with sqlite3.connect('restaurant.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT item_id FROM favorites WHERE username = ?', (username,))
        return [row[0] for row in cursor.fetchall()]



@app.route('/favorites/<username>')
def user_favorites(username):
    try:
        with sqlite3.connect('restaurant.db') as conn:  
            cursor = conn.cursor()
            cursor.execute('''
                SELECT items.id, items.name, items.description, items.price, items.image_path
                FROM favorites
                JOIN items ON favorites.item_id = items.id
                WHERE favorites.username = ?
            ''', (username,))
            favorite_items = cursor.fetchall()

           
            logging.debug(f"Favorite items for {username}: {favorite_items}")

        if not favorite_items:
            logging.info(f"No favorite items found for user: {username}")

        return render_template('favorites.html', username=username, favorite_items=favorite_items)

    except Exception as e:
        logging.error(f"Error fetching favorites for {username}: {e}")
        return jsonify({"message": "Error fetching favorites.", "error": str(e)}), 500


@app.route('/items', methods=['GET'])
def get_items():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description, price, image_path, category FROM Items")
        items = cursor.fetchall()
        return jsonify(items)

@app.route('/favorites', methods=['GET'])
def get_favorites():
    user_id = session.get('user_id')  
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT Items.id, Items.name, Items.price, Items.category, Items.image_path FROM Favorites JOIN Items ON Favorites.item_id = Items.id WHERE Favorites.user_id = ?", (user_id,))
        favorites = cursor.fetchall()
        return jsonify(favorites)



@app.route('/logout')
def logout():
    session.clear()  
    return redirect(url_for('login'))


init_db()


populate_items_table(categories)


if __name__ == '__main__':
    app.run(debug=True)
