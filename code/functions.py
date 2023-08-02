import io
import json
import os
import geocoder
import requests
from bs4 import BeautifulSoup
from PIL import Image
from customtkinter import CTkImage
import cairosvg
# import fitz
# from svglib.svglib import svg2rlg
# import textwrap
# from reportlab.graphics import renderPDF

g = geocoder.ip('me')
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
}
path_ = 'data.json'


class jsonHandling:
    def __init__(self):
        if not os.path.exists(path_):
            with open(path_, 'w', encoding='utf8') as f:
                json.dump({}, f, ensure_ascii=False, indent=4)

    def get_categories(self):
        with open(path_, 'r+', encoding='utf8') as f:
            data = json.load(f)
        return data

    def get_category_items(self, c_name: str, query: str = None):
        with open(path_, 'r+', encoding='utf8') as f:
            data = json.load(f)

        if c_name in data.keys():
            if query:
                result = {}
                for key, value in data[c_name].items():
                    if query in key or query in value:
                        result[key] = value
                return result

            return data[c_name]
        else:
            return None

    def edit_category_item(self, c_name: str, old_key: str, new_key: str, new_value: str = ''):
        with open(path_, 'r+', encoding='utf8') as f:
            data = json.load(f)

        if c_name in data.keys():
            del data[c_name][old_key]
            data[c_name][new_key] = new_value


        with open(path_, 'w', encoding='utf8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def add_category(self, c_name: str):
        with open(path_, 'r+', encoding='utf8') as f:
            data = json.load(f)

        if c_name not in data.keys():
            data[c_name] = {}
        else:
            return False

        with open(path_, 'w', encoding='utf8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        return True

    def add_category_item(self, c_name: str, frst_item: str, second_item: str = ''):
        with open(path_, 'r+', encoding='utf8') as f:
            data = json.load(f)

        if c_name in data.keys():
            data[c_name][frst_item] = second_item

        with open(path_, 'w', encoding='utf8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def delete_category_item(self, c_name: str, frst_item: str):
        with open(path_, 'r+', encoding='utf8') as f:
            data = json.load(f)

        if c_name in data.keys() and frst_item in data[c_name].keys():
            del data[c_name][frst_item]

        with open(path_, 'w', encoding='utf8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def delete_category(self, c_name: str):
        with open(path_, 'r+', encoding='utf8') as f:
            data = json.load(f)

        if c_name in data:
            del data[c_name]

        with open(path_, 'w', encoding='utf8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)


def get_location():
    g = geocoder.ip('me')
    return g.latlng


def get_current_weather():
    try:
        lat, lon = get_location()
        answ = requests.get(f'https://www.accuweather.com/en/search-locations?query={lat}%2C+{lon}', headers=headers, timeout=5)
        soup = BeautifulSoup(answ.content, 'html.parser')
        if soup and soup.select_one('div.temp') and soup.select_one('svg.weather-icon'):
            icon = str(soup.select_one('svg.weather-icon')).replace('viewbox', 'viewBox')
            temperature = soup.select_one('div.temp').text
            return temperature, icon
        else:
            return '?°C', None
    except:
        return '?°C', None

def svg_to_ctk_image(svg, x=30, y=30):
    icon = io.BytesIO()

    cairosvg.svg2png(bytestring=svg, write_to=icon)

    image = Image.open(icon)
    return CTkImage(image, size=(x, y))

'''def svg_to_ctk_image(svg, x=30, y=30):
    icon_pdf = io.BytesIO()

    w = svg2rlg(io.StringIO(textwrap.dedent(svg)))
    renderPDF.drawToFile(w, icon_pdf)

    doc = fitz.Document(stream=icon_pdf)
    pix = doc.load_page(0).get_pixmap(alpha=True, dpi=300)
    icon = io.BytesIO(pix.tobytes(output='png'))

    image = Image.open(icon)
    return CTkImage(image, size=(x, y))'''


def do_popup(event, frame):
    try:
        frame.tk_popup(event.x_root, event.y_root)
    finally:
        frame.grab_release()

def play_copied_successfully_animation(entry):
    def smooth_gradient(entry):
        start_color = "#343638"
        end_color = "#565b5e"
        delay = 2  # Задержка в миллисекундах между обновлениями цвета
        steps = 3  # Количество шагов анимации

        r1, g1, b1 = int(start_color[1:3], 16), int(start_color[3:5], 16), int(start_color[5:7], 16)
        r2, g2, b2 = int(end_color[1:3], 16), int(end_color[3:5], 16), int(end_color[5:7], 16)

        for i in range(steps):
            # Вычисляем текущий цвет в шаге анимации
            r = int(r1 + (i * (r2 - r1) / (steps - 1)))
            g = int(g1 + (i * (g2 - g1) / (steps - 1)))
            b = int(b1 + (i * (b2 - b1) / (steps - 1)))

            # Конвертируем RGB в формат #RRGGBB
            color = "#{:02x}{:02x}{:02x}".format(r, g, b)

            # Устанавливаем цвет фона для виджета Entry
            entry.configure(fg_color=color)

            # Ожидаем заданную задержку перед обновлением цвета
            entry.update()
            entry.after(delay)

        # После завершения анимации, меняем направление градиента и вызываем функцию еще раз
        smooth_gradient_reverse(entry)

    def smooth_gradient_reverse(entry):
        start_color = "#565b5e"
        end_color = "#343638"
        delay = 50  # Задержка в миллисекундах между обновлениями цвета
        steps = 20  # Количество шагов анимации

        r1, g1, b1 = int(start_color[1:3], 16), int(start_color[3:5], 16), int(start_color[5:7], 16)
        r2, g2, b2 = int(end_color[1:3], 16), int(end_color[3:5], 16), int(end_color[5:7], 16)

        for i in range(steps):
            # Вычисляем текущий цвет в шаге анимации
            r = int(r1 + (i * (r2 - r1) / (steps - 1)))
            g = int(g1 + (i * (g2 - g1) / (steps - 1)))
            b = int(b1 + (i * (b2 - b1) / (steps - 1)))

            # Конвертируем RGB в формат #RRGGBB
            color = "#{:02x}{:02x}{:02x}".format(r, g, b)

            # Устанавливаем цвет фона для виджета Entry
            entry.configure(fg_color=color)

            # Ожидаем заданную задержку перед обновлением цвета
            entry.update()
            entry.after(delay)

    smooth_gradient(entry)
