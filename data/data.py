MENU_BTNS = {key: value for key, value in [
    ('cuisine', 'Cuisine'),
    ('calories', 'Calories'),
    ('productList', 'Product list'),
    ('dish', 'Dish'),
    ('getRecipe', 'Get recipe'),
    ('clear', 'Clear selected')
]}


CUISINES = {
    'italian': {
        'name': 'Italian',
        'call_key': 'italian_c',
        'description': 'Known for dishes like pizza, pasta, risotto, and gelato.'
    },
    'chinese': {
        'name': 'Chinese',
        'call_key': 'chinese_c',
        'description': 'Famous for its diverse regional styles, including Cantonese, Sichuan, and Beijing cuisine, with dishes like stir-fries, dumplings, and Peking duck.'
    },
    'indian': {
        'name': 'Indian',
        'call_key': 'indian_c',
        'description': 'Offers a wide variety of flavors and spices, with popular dishes such as curry, biryani, samosas, and naan bread.'
    },
    'japanese': {
        'name': 'Japanese',
        'call_key': 'japanese_c',
        'description': 'Features sushi, sashimi, ramen, tempura, and other dishes that highlight fresh ingredients and delicate flavors.'
    },
    'mexican': {
        'name': 'Mexican',
        'call_key': 'mexican_c',
        'description': 'Known for its vibrant and bold flavors, including dishes like tacos, enchiladas, guacamole, and salsa.'
    },
    'french': {
        'name': 'French',
        'call_key': 'french_c',
        'description': 'Renowned for its sophistication and elegance, with dishes like coq au vin, escargots, croissants, and crème brûlée.'
    },
    'thai': {
        'name': 'Thai',
        'call_key': 'thai_c',
        'description': 'Offers a balance of sweet, spicy, sour, and salty flavors, with popular dishes like pad Thai, green curry, and tom yum soup.'
    },
    'spanish': {
        'name': 'Spanish',
        'call_key': 'spanish_c',
        'description': 'Highlights tapas, paella, chorizo, and dishes that incorporate ingredients like olive oil, garlic, and saffron.'
    },
    'lebanese': {
        'name': 'Lebanese',
        'call_key': 'lebanese_c',
        'description': 'Features dishes such as hummus, falafel, kebabs, and tabbouleh, with an emphasis on fresh ingredients and aromatic spices.'
    },
    'greek': {
        'name': 'Greek',
        'call_key': 'greek_c',
        'description': 'Known for dishes like moussaka, souvlaki, spanakopita, and tzatziki, with Mediterranean flavors and ingredients like olive oil, feta cheese, and olives.'
    },
    'ukrainian': {
        'name': 'Ukrainian',
        'call_key': 'ukrainian_c',
        'description': 'Offers traditional dishes such as borscht, varenyky (dumplings), holubtsi (cabbage rolls).'
    }
}


def get_all_cuisine_call_keys():
    return list(CUISINES.keys())
