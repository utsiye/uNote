import traceback

import customtkinter
import tkinter
from loguru import logger
from PIL import Image
from datetime import datetime
from functions import jsonHandling, get_current_weather, svg_to_ctk_image, do_popup, play_copied_successfully_animation
from svg_images import *
from functools import partial

h_json = jsonHandling()
logger.remove()
logger.add('logs.log', format="[{time:DD.MM.YYYY HH:mm}]   [{level}] - {message}\n\n", backtrace=True, colorize=True)


class App(customtkinter.CTk):

    def __init__(self):
        super().__init__()
        self.weather_label = None
        self.title_frame = None
        self.search_frame = None
        self.items_frame = None
        self.temperature_label = None
        self.time_label = None
        self.menu_frame = None
        self.choosed_category = None

        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("blue")

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        position_right = int(screen_width / 2 - 250)
        position_down = int(screen_height / 2 - 250)

        self.geometry("800x500+{}+{}".format(position_right, position_down))

        self.resizable(False, False)
        self.title('uNote')


    def copy_to_clipboard(self, entry):
        play_copied_successfully_animation(entry)
        self.clipboard_clear()
        self.clipboard_append(entry.get())

    def render_search_menu(self):

        search_input = customtkinter.CTkEntry(self.search_frame, width=150, height=30, placeholder_text='Искать...')
        search_button = customtkinter.CTkButton(self.search_frame, text='', width=35, height=35,
                                                image=svg_to_ctk_image(search_image, 20, 20),
                                                fg_color='#404040', hover_color='#363636',
                                                command=lambda: self.process_search_query(self.choosed_category, search_input.get()))
        add_button = customtkinter.CTkButton(self.search_frame, text='+', width=35, height=35,
                                             font=customtkinter.CTkFont('Arial', 30), fg_color='#404040',
                                             hover_color='#363636', text_color='#cfcfcf')
        right_click_menu = tkinter.Menu(add_button, tearoff=False, background='#424242', fg='#cfcfcf', borderwidth=0,
                                        activebackground='#303030', activeforeground='#cfcfcf', activeborderwidth=0,
                                        font='Arial 15')
        right_click_menu.add_command(label="Запись")
        right_click_menu.add_command(label="Словарь")

        add_button.bind("<Button-1>", lambda event: do_popup(event, frame=right_click_menu))
        right_click_menu.entryconfigure("Запись", command=lambda: self.process_add_note_category_item(self.choosed_category))
        right_click_menu.entryconfigure("Словарь", command=lambda: self.process_add_dict_category_item(self.choosed_category))

        search_input.place(relx=0.25, rely=0.5, anchor=tkinter.CENTER)
        search_button.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
        add_button.place(relx=0.9, rely=0.5, anchor=tkinter.CENTER)

    def render_categories(self):
        data = h_json.get_categories()

        row = 0

        for row, category in enumerate(data.keys()):
            button = customtkinter.CTkButton(self.menu_frame,
                                             text=category if len(category) < 10 else category[:12] + '...',
                                             font=customtkinter.CTkFont('Arial', 20), fg_color='#404040',
                                             hover_color='#363636', width=170, height=35,
                                             command=partial(self.process_choosed_category, category), text_color='#cfcfcf')
            button.bind("<Double-Button-2>", partial(lambda c_name, event: self.process_delete_category(c_name), category))
            button.grid(row=row, column=0, padx=10, pady=5)

        customtkinter.CTkButton(self.menu_frame, text='+',
                                font=customtkinter.CTkFont('Arial', 25), fg_color='#404040', hover_color='#363636',
                                width=50, height=35, command=self.create_new_category_app,
                                text_color='#cfcfcf').grid(row=row + 1, column=0, padx=70, pady=5)

    def render_main_elements(self):
        menu_frame = customtkinter.CTkScrollableFrame(self, width=200, height=350, corner_radius=10)
        title_frame = customtkinter.CTkFrame(self, width=230, height=90, corner_radius=10)
        time_label = customtkinter.CTkLabel(title_frame, text=datetime.now().strftime('%H:%M'),
                                            font=customtkinter.CTkFont('Arial', 25), text_color='#cfcfcf')
        self.after(1000, self.change_title_time)
        temperature, weather_image = get_current_weather()
        # temperature, weather_image = '?°C', None
        temperature_label = customtkinter.CTkLabel(title_frame, text=temperature,
                                                   font=customtkinter.CTkFont('Arial', 25),
                                                   text_color='#cfcfcf')
        slash_label = customtkinter.CTkLabel(title_frame, text='/', font=customtkinter.CTkFont('Arial', 130),
                                             text_color='#242424')
        if weather_image:
            weather_icon_label = customtkinter.CTkLabel(title_frame, text='', image=svg_to_ctk_image(weather_image))
        else:
            weather_icon_label = customtkinter.CTkLabel(title_frame, text='',
                                                        image=svg_to_ctk_image(none_weather_image))

        self.after(600000, lambda: self.change_title_temperature_and_weather())
        search_frame = customtkinter.CTkFrame(self, width=470, height=90, corner_radius=10)
        items_frame = customtkinter.CTkScrollableFrame(self, width=445, height=350, corner_radius=10)

        self.title_frame = title_frame
        self.search_frame = search_frame
        self.items_frame = items_frame
        self.temperature_label = temperature_label
        self.weather_label = weather_icon_label
        self.time_label = time_label
        self.menu_frame = menu_frame

        self.render_search_menu()
        self.render_categories()

        menu_frame.place(relx=0.17, rely=0.6, anchor=tkinter.CENTER)
        title_frame.place(relx=0.17, rely=0.11, anchor=tkinter.CENTER)
        time_label.place(relx=0.22, rely=0.5, anchor=tkinter.CENTER)
        slash_label.place(relx=0.48, rely=0.5, anchor=tkinter.CENTER)
        weather_icon_label.place(relx=0.75, rely=0.3, anchor=tkinter.CENTER)
        temperature_label.place(relx=0.75, rely=0.7, anchor=tkinter.CENTER)
        search_frame.place(relx=0.67, rely=0.11, anchor=tkinter.CENTER)
        items_frame.place(relx=0.67, rely=0.6, anchor=tkinter.CENTER)

    def process_choosed_category(self, c_name: str):
        self.choosed_category = c_name

        category_items = h_json.get_category_items(c_name)

        self.render_category_items(category_items)


    def render_category_items(self, category_items):

        for i in self.items_frame.winfo_children():
            i.destroy()

        for row, item in enumerate(category_items.items()):
            key, value = item
            frame = customtkinter.CTkFrame(self.items_frame, height=30)

            frame.pack(fill='x', pady=7)
            frst_entry = customtkinter.CTkEntry(frame, width=140, height=25, justify='center', text_color='#cfcfcf')
            frst_entry.insert(0, key)
            #frst_entry.configure(state='disabled')
            frst_entry.bind("<Button-3>", partial(lambda entry, event: self.copy_to_clipboard(entry), frst_entry))
            frst_entry.place(relx=0.2, rely=0.5, anchor=tkinter.CENTER)

            scnd_entry = None
            if value:
                scnd_entry = customtkinter.CTkEntry(frame, width=140, height=25, justify='center', text_color='#cfcfcf')
                scnd_entry.insert(0, value)
                scnd_entry.configure(state='disabled')
                scnd_entry.bind("<Button-3>", partial(lambda entry, event: self.copy_to_clipboard(entry), scnd_entry))
                scnd_entry.place(relx=0.55, rely=0.5, anchor=tkinter.CENTER)

            edit_button = customtkinter.CTkButton(frame, width=30, height=30, text='', fg_color='transparent',
                                                  hover_color='#262626', image=svg_to_ctk_image(edit_image, 20, 20))
            edit_button.configure(
                command=partial(self.process_edit_category_item, self.choosed_category, key, edit_button, frst_entry, scnd_entry))
            delete_button = customtkinter.CTkButton(frame, width=30, height=30, text='', fg_color='transparent',
                                                    hover_color='#262626', image=svg_to_ctk_image(delete_image, 20, 20))
            delete_button.configure(command=partial(self.process_destroy_category_item, self.choosed_category, key))

            edit_button.place(relx=0.8, rely=0.5, anchor=tkinter.CENTER)
            delete_button.place(relx=0.9, rely=0.5, anchor=tkinter.CENTER)

    def process_add_note_category_item(self, c_name):
        if not c_name:
            return

        frame = customtkinter.CTkFrame(self.items_frame, height=30)
        entry = customtkinter.CTkEntry(frame, width=140, height=25, justify='center', text_color='#cfcfcf')
        confirm_button = customtkinter.CTkButton(frame, width=30, height=30, text='', fg_color='transparent',
                                                 hover_color='#262626', image=svg_to_ctk_image(confirm_image, 20, 20),
                                                 command=lambda: self.confirm_temp_item(c_name, frame, entry))
        delete_button = customtkinter.CTkButton(frame, width=30, height=30, text='', fg_color='transparent',
                                                hover_color='#262626', image=svg_to_ctk_image(delete_image, 20, 20),
                                                command=lambda: self.delete_temp_item(frame))

        if len(self.items_frame.winfo_children()) > 1:
            frame.pack(side='top', before=self.items_frame.winfo_children()[0], fill='x', pady=7)
        else:
            frame.pack(fill='x', pady=7)
        entry.place(relx=0.2, rely=0.5, anchor=tkinter.CENTER)
        confirm_button.place(relx=0.8, rely=0.5, anchor=tkinter.CENTER)
        delete_button.place(relx=0.9, rely=0.5, anchor=tkinter.CENTER)

    def delete_temp_item(self, frame):
        frame.destroy()

    def confirm_temp_item(self, c_name, frame, frst_entry, scnd_entry=None):
        if frst_entry.get() and (not scnd_entry or (scnd_entry and scnd_entry.get())):
            h_json.add_category_item(c_name, frst_entry.get(), scnd_entry.get() if scnd_entry else '')
            for widget in self.items_frame.winfo_children():
                widget.destroy()
            self.process_choosed_category(c_name)
        else:
            frame.destroy()

    def process_add_dict_category_item(self, c_name):
        if not c_name:
            return

        frame = customtkinter.CTkFrame(self.items_frame, height=30)
        frst_entry = customtkinter.CTkEntry(frame, width=140, height=25, justify='center', text_color='#cfcfcf')
        scnd_entry = customtkinter.CTkEntry(frame, width=140, height=25, justify='center', text_color='#cfcfcf')
        confirm_button = customtkinter.CTkButton(frame, width=30, height=30, text='', fg_color='transparent',
                                                 hover_color='#262626', image=svg_to_ctk_image(confirm_image, 20, 20),
                                                 command=lambda: self.confirm_temp_item(c_name, frame, frst_entry,
                                                                                        scnd_entry))
        delete_button = customtkinter.CTkButton(frame, width=30, height=30, text='', fg_color='transparent',
                                                hover_color='#262626', image=svg_to_ctk_image(delete_image, 20, 20),
                                                command=lambda: self.delete_temp_item(frame))

        if len(self.items_frame.winfo_children()) > 1:
            frame.pack(side='top', before=self.items_frame.winfo_children()[0], fill='x', pady=7)
        else:
            frame.pack(fill='x', pady=7)

        frst_entry.place(relx=0.2, rely=0.5, anchor=tkinter.CENTER)
        scnd_entry.place(relx=0.55, rely=0.5, anchor=tkinter.CENTER)
        confirm_button.place(relx=0.8, rely=0.5, anchor=tkinter.CENTER)
        delete_button.place(relx=0.9, rely=0.5, anchor=tkinter.CENTER)

    def create_new_category_app(self):
        new_c_app = customtkinter.CTkToplevel()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        position_right = int(screen_width / 2 + 50)
        position_down = int(screen_height / 2 - 100)

        new_c_app.geometry("300x150+{}+{}".format(position_right, position_down))

        new_c_app.resizable(False, False)
        new_c_app.title('Новая категория')
        new_c_app.grab_set()

        label = customtkinter.CTkLabel(new_c_app, text='Введите название новой категории:', text_color='#cfcfcf')
        entry = customtkinter.CTkEntry(new_c_app)

        ok_button = customtkinter.CTkButton(new_c_app, text='Ок', fg_color='#404040', hover_color='#363636',
                                            command=lambda: self.process_new_category(new_c_app, entry.get()),
                                            width=110)
        cancel_button = customtkinter.CTkButton(new_c_app, text='Отмена', fg_color='#404040', hover_color='#363636',
                                                command=lambda: new_c_app.destroy(), width=110)

        label.place(relx=0.5, rely=0.2, anchor=tkinter.CENTER)
        entry.place(relx=0.5, rely=0.45, anchor=tkinter.CENTER)
        ok_button.place(relx=0.25, rely=0.8, anchor=tkinter.CENTER)
        cancel_button.place(relx=0.75, rely=0.8, anchor=tkinter.CENTER)

    def process_new_category(self, new_c_app, c_name):
        new_c_app.destroy()
        if c_name:
            is_added = h_json.add_category(c_name)

            if is_added:
                for widget in self.menu_frame.winfo_children():
                    widget.destroy()
                self.render_categories()
            else:
                c_exists_app = customtkinter.CTkToplevel(self)
                c_exists_app.title('Не удалось добавить категорию')
                c_exists_app.geometry("250x150")
                c_exists_app.focus()
                customtkinter.CTkLabel(c_exists_app, text='Категория с таким названием\nуже существует!',
                                       font=customtkinter.CTkFont('Arial', 16), text_color='#cfcfcf').place(relx=0.5,
                                                                                                            rely=0.3,
                                                                                                            anchor=tkinter.CENTER)
                customtkinter.CTkButton(c_exists_app, text='Ок', fg_color='#404040', hover_color='#363636',
                                        command=lambda: c_exists_app.destroy(), text_color='#cfcfcf').place(relx=0.5,
                                                                                                            rely=0.75,
                                                                                                            anchor=tkinter.CENTER)

    def process_delete_category(self, category: str):
        h_json.delete_category(category)
        for widget in self.menu_frame.winfo_children():
            widget.destroy()
        self.render_categories()

    def process_edit_category_item(self, c_name, key, edit_button, frst_entry, scnd_entry=None):
        frst_entry.configure(state='normal')
        if scnd_entry:
            scnd_entry.configure(state='normal')

        edit_button.configure(image=svg_to_ctk_image(confirm_image, 20, 20),
                              command=lambda: self.process_confirm_editing_category_item(c_name, key, edit_button,
                                                                                         frst_entry, scnd_entry))

    def process_confirm_editing_category_item(self, c_name, old_key, edit_button, frst_entry, scnd_entry=None):
        frst_entry.configure(state='disabled')
        if scnd_entry:
            scnd_entry.configure(state='disabled')

        edit_button.configure(image=svg_to_ctk_image(edit_image, 20, 20))
        h_json.edit_category_item(c_name, old_key, frst_entry.get(), scnd_entry.get() if scnd_entry else '')

    def process_destroy_category_item(self, c_name, key):
        h_json.delete_category_item(c_name, key)
        for widget in self.items_frame.winfo_children():
            widget.destroy()
        self.process_choosed_category(c_name)

    def process_search_query(self, c_name, query):
        category_items = h_json.get_category_items(c_name, query)
        if category_items:
            self.render_category_items(category_items)


    def change_title_time(self):
        self.time_label.configure(text=datetime.now().strftime('%H:%M'))
        self.after(1000, self.change_title_time)

    def change_title_temperature_and_weather(self):
        temperature, image = get_current_weather()
        self.temperature_label.configure(text=temperature)
        if image:
            self.weather_label.configure(image=svg_to_ctk_image(image))
        else:
            self.weather_label.configure(image=svg_to_ctk_image(none_weather_image))
        self.after(600000, self.change_title_temperature_and_weather)


def main():
    try:
        app = App()
        app.render_main_elements()
        app.mainloop()
    except:
        logger.error(traceback.format_exc())


if __name__ == '__main__':
    main()
