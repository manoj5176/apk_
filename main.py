import os
import json
import requests
from datetime import datetime
from functools import partial
from threading import Thread
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.metrics import dp
from kivy.properties import (StringProperty, BooleanProperty, 
                          NumericProperty, ObjectProperty)
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.uix.modalview import ModalView
from kivy.logger import Logger
from kivy.core.window import Window
from kivy.utils import platform

if platform == 'android':
    from android.permissions import request_permissions, Permission
    from android.storage import app_storage_path

class LoadingModal(ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.6, 0.2)
        box = BoxLayout(orientation='vertical', padding=dp(10))
        box.add_widget(Label(text="Loading data..."))
        self.add_widget(box)

class ErrorModal(ModalView):
    def __init__(self, message, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.8, 0.4)
        box = BoxLayout(orientation='vertical', padding=dp(10))
        box.add_widget(Label(text=message))
        btn = Button(text="OK", size_hint_y=None, height=dp(50))
        btn.bind(on_press=lambda x: self.dismiss())
        box.add_widget(btn)
        self.add_widget(box)

class MainScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.name = 'main'
        self.app = app
        self.build_ui()

    def build_ui(self):
        main_layout = BoxLayout(orientation="vertical", spacing=dp(5), padding=[dp(10), dp(5), dp(10), dp(5)])

        # Header
        header = BoxLayout(size_hint_y=None, height=dp(50), padding=dp(5), spacing=dp(5))
        with header.canvas.before:
            Color(0.2, 0.4, 0.6, 1)
            self.header_bg = Rectangle(pos=header.pos, size=header.size)
        header.bind(
            pos=lambda i, v: setattr(self.header_bg, 'pos', i.pos),
            size=lambda i, v: setattr(self.header_bg, 'size', i.size))

        self.title_label = Label(
            text="PDF Data Search",
            font_size=dp(18),
            color=(1, 1, 1, 1),
            size_hint_x=0.6,
            halign='left',
            valign='middle',
            text_size=(Window.width * 0.55, None),
            shorten=True)
        self.status_label = Label(
            text=f"Last updated: {self.app.last_updated}",
            color=(1, 1, 1, 1),
            size_hint_x=0.4,
            halign='right',
            valign='middle',
            font_size=dp(10),
            text_size=(Window.width * 0.35, None))
        header.add_widget(self.title_label)
        header.add_widget(self.status_label)
        main_layout.add_widget(header)

        # Search Area
        search_box = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(5))
        self.search_input = TextInput(
            hint_text="Search...",
            multiline=False,
            padding=[dp(15), dp(10)],
            font_size=dp(14),
            size_hint_x=0.7)
        self.search_input.bind(on_text_validate=partial(self.app.do_search, None))

        search_btn = Button(
            text="search",
            size_hint_x=0.15,
            font_size=dp(14),
            background_normal='',
            background_color=(0.3, 0.5, 0.7, 1))
        search_btn.bind(on_press=self.app.do_search)

        clear_btn = Button(
            text="clear",
            size_hint_x=0.15,
            font_size=dp(14),
            background_normal='',
            background_color=(0.7, 0.3, 0.3, 1))
        clear_btn.bind(on_press=self.app.clear_search)

        search_box.add_widget(self.search_input)
        search_box.add_widget(search_btn)
        search_box.add_widget(clear_btn)
        main_layout.add_widget(search_box)

        # Action buttons
        action_box = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(5))
        for text, callback in [
            ("Update", self.app.update_data),
            ("Headers", self.app.show_headers_list),
            ("Back", self.back_to_launcher)
        ]:
            btn = Button(
                text=text,
                font_size=dp(12),
                background_normal='',
                background_color=(0.3, 0.5, 0.7, 1))
            btn.bind(on_press=callback)
            action_box.add_widget(btn)
        main_layout.add_widget(action_box)

        self.results_count_label = Label(
            text="",
            size_hint_y=None,
            height=dp(25),
            color=(0.3, 0.5, 0.7, 1),
            bold=True,
            font_size=dp(12))
        main_layout.add_widget(self.results_count_label)

        # Content Area
        content_area = BoxLayout(orientation='vertical', size_hint=(1, 1))
        
        # Headers screen
        self.headers_screen = Screen(name='headers')
        self.headers_scroll = ScrollView()
        self.headers_layout = GridLayout(cols=1, spacing=dp(5), size_hint_y=None, padding=dp(5))
        self.headers_layout.bind(minimum_height=self.headers_layout.setter('height'))
        self.headers_scroll.add_widget(self.headers_layout)
        self.headers_screen.add_widget(self.headers_scroll)

        # Results screen
        self.results_screen = Screen(name='results')
        self.results_scroll = ScrollView()
        self.results_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(5),
            padding=dp(5))
        self.results_container.bind(minimum_height=self.results_container.setter('height'))
        self.results_scroll.add_widget(self.results_container)
        self.results_screen.add_widget(self.results_scroll)

        # Screen manager
        self.content_switcher = ScreenManager()
        self.content_switcher.add_widget(self.headers_screen)
        self.content_switcher.add_widget(self.results_screen)
        content_area.add_widget(self.content_switcher)
        self.content_switcher.current = 'headers'

        main_layout.add_widget(content_area)
        self.add_widget(main_layout)
        Window.bind(on_resize=self._update_layout)

    def _update_layout(self, *args):
        self.title_label.text_size = (Window.width * 0.55, None)
        self.status_label.text_size = (Window.width * 0.35, None)
        self.title_label.texture_update()
        self.status_label.texture_update()

    def back_to_launcher(self, instance):
        App.get_running_app().stop()
        LauncherApp().run()

class SearchApp(App):
    github_data_url = StringProperty("")
    last_updated = StringProperty("Never")
    show_headers = BooleanProperty(True)
    search_results_count = NumericProperty(0)
    current_open_header = StringProperty("")
    sm = ObjectProperty(None, allownone=True)
    loading_modal = None

    def __init__(self, json_file="unit3.json", **kwargs):
        super().__init__(**kwargs)
        self.json_file = json_file
        self.data = {"tables": {}, "last_updated": "Never"}
        self.headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json',
            'Cache-Control': 'no-cache'}

    def on_start(self):
        if platform == 'android':
            request_permissions([
                Permission.INTERNET,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ])

    def get_data_path(self, filename):
        if platform == 'android':
            storage_path = app_storage_path()
            os.makedirs(storage_path, exist_ok=True)
            return os.path.join(storage_path, filename)
        return filename

    def show_loading(self):
        self.loading_modal = LoadingModal()
        self.loading_modal.open()

    def hide_loading(self):
        if self.loading_modal:
            self.loading_modal.dismiss()
            self.loading_modal = None

    def load_data(self):
        def _load_in_thread():
            try:
                Clock.schedule_once(lambda dt: self.show_loading())
                
                json_path = self.get_data_path(self.json_file)
                
                # Try downloaded version first
                if os.path.exists(json_path):
                    with open(json_path, 'r') as f:
                        data = json.load(f)
                        Clock.schedule_once(lambda dt: self._finish_loading(data))
                        return
                
                # Fallback to packaged version
                from kivy.resources import resource_find
                packaged_file = resource_find(self.json_file)
                if packaged_file:
                    with open(packaged_file, 'r') as f:
                        data = json.load(f)
                        Clock.schedule_once(lambda dt: self._finish_loading(data))
                        return
                
                # No data found, try to download
                self.download_data()
                
            except Exception as e:
                Logger.error(f"Load error: {str(e)}")
                Clock.schedule_once(lambda dt: ErrorModal(f"Load failed: {str(e)}").open())
            finally:
                Clock.schedule_once(lambda dt: self.hide_loading())

        Thread(target=_load_in_thread, daemon=True).start()

    def _finish_loading(self, data):
        self.data = data
        self.last_updated = data.get("last_updated", "Never")
        if self.main_screen:
            self.main_screen.status_label.text = f"Last updated: {self.last_updated}"
        self.load_headers_list()

    def download_data(self):
        def _download_in_thread():
            try:
                if not self.github_data_url:
                    Clock.schedule_once(lambda dt: ErrorModal("No data source configured").open())
                    return

                Clock.schedule_once(lambda dt: self.show_loading())
                
                response = requests.get(self.github_data_url, headers=self.headers, timeout=10)
                response.raise_for_status()
                
                json_path = self.get_data_path(self.json_file)
                data = response.json()
                data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                with open(json_path, 'w') as f:
                    json.dump(data, f)
                
                Clock.schedule_once(lambda dt: self._finish_loading(data))
            except Exception as e:
                Logger.error(f"Download error: {str(e)}")
                Clock.schedule_once(lambda dt: ErrorModal(f"Download failed: {str(e)}").open())
            finally:
                Clock.schedule_once(lambda dt: self.hide_loading())

        Thread(target=_download_in_thread, daemon=True).start()

    def save_data(self):
        try:
            json_path = self.get_data_path(self.json_file)
            with open(json_path, 'w') as f:
                json.dump(self.data, f)
            Logger.info("Data saved successfully")
        except Exception as e:
            Logger.error(f"Error saving JSON: {str(e)}")

    def build(self):
        self.sm = ScreenManager()
        main_screen = MainScreen(self)
        self.sm.add_widget(main_screen)
        Clock.schedule_once(lambda dt: self.load_data(), 0.1)
        return self.sm

    @property
    def main_screen(self):
        if self.sm and 'main' in self.sm.screen_names:
            return self.sm.get_screen('main')
        return None

    def load_headers_list(self):
        if not self.main_screen:
            return

        self.main_screen.headers_layout.clear_widgets()

        for table_key, table_data in self.data.get("tables", {}).items():
            header = table_data.get("header", "")
            btn = Button(
                text=f"{table_key}: {header[:30]}{'...' if len(header) > 30 else ''}",
                size_hint_y=None,
                height=dp(40),
                background_normal='',
                background_color=(0.8, 0.8, 0.9, 1),
                color=(0, 0, 0, 1))
            btn.table_key = table_key
            btn.header_text = header
            btn.bind(on_press=self.on_header_click)
            self.main_screen.headers_layout.add_widget(btn)

    def on_header_click(self, instance):
        table_data = self.data.get("tables", {}).get(instance.table_key, {}).get("table", [])
        
        if instance.table_key in self.sm.screen_names:
            self.sm.current = instance.table_key
        else:
            table_screen = TableViewScreen(instance.table_key, instance.header_text, table_data)
            self.sm.add_widget(table_screen)
            self.sm.current = instance.table_key

    def show_headers_list(self, instance):
        self.clear_search(instance)
        if self.main_screen:
            self.main_screen.content_switcher.current = 'headers'

    def clear_search(self, instance):
        if self.main_screen:
            if self.main_screen.search_input:
                self.main_screen.search_input.text = ""
            self.main_screen.content_switcher.current = 'headers'
            self.main_screen.results_container.clear_widgets()
            if self.main_screen.results_count_label:
                self.main_screen.results_count_label.text = ""

    def update_data(self, instance=None):
        self.download_data()

    def do_search(self, instance):
        if not self.main_screen or not self.main_screen.search_input:
            return

        search_term = self.main_screen.search_input.text.strip().lower()
        if not search_term:
            return

        self.main_screen.results_container.clear_widgets()
        self.main_screen.content_switcher.current = 'results'

        loading = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(40))
        loading.add_widget(Label(text="Searching...", color=(0.3, 0.5, 0.7, 1)))
        self.main_screen.results_container.add_widget(loading)

        self.search_term = search_term
        self.search_results_count = 0
        self.all_data = self.data.get("tables", {})
        self.current_search_index = 0

        def _search_in_thread():
            try:
                tables = list(self.all_data.items())
                for table_key, table_data in tables:
                    header = table_data.get("header", "")
                    table_content = table_data.get("table", [])

                    header_matches = self.search_term in header.lower()
                    table_matches = []

                    try:
                        if isinstance(table_content, list):
                            if table_content and isinstance(table_content[0], dict):
                                table_matches = [
                                    row for row in table_content
                                    if any(self.search_term in str(value).lower() for value in row.values())
                                ]
                            elif table_content and isinstance(table_content[0], list):
                                table_matches = [
                                    row for row in table_content
                                    if any(self.search_term in str(value).lower() for value in row)
                                ]
                    except Exception as e:
                        Logger.error(f"Error processing table: {str(e)}")

                    if header_matches or table_matches:
                        self.search_results_count += len(table_matches) if table_matches else 1
                        Clock.schedule_once(lambda dt, k=table_key, h=header, d=table_matches if table_matches else table_content, hm=header_matches: 
                                         self.main_screen.add_table_result(k, h, d, hm))

                Clock.schedule_once(lambda dt: self.main_screen.results_container.remove_widget(loading))
                if self.search_results_count == 0:
                    Clock.schedule_once(lambda dt: ErrorModal("No results found").open())
            except Exception as e:
                Logger.error(f"Search error: {str(e)}")
                Clock.schedule_once(lambda dt: ErrorModal(f"Search failed: {str(e)}").open())

        Thread(target=_search_in_thread, daemon=True).start()

    def on_search_result_click(self, instance):
        table_key = getattr(instance, 'table_key', None)
        header_text = getattr(instance, 'header_text', "")
        table_data = getattr(instance, 'table_data', [])

        if not table_key:
            Logger.error("Clicked button has no table_key")
            return

        if table_key in self.sm.screen_names:
            self.sm.current = table_key
        else:
            table_screen = TableViewScreen(table_key, header_text, table_data)
            self.sm.add_widget(table_screen)
            self.sm.current = table_key

    def check_for_updates(self, dt):
        try:
            if not self.github_data_url:
                return

            response = requests.head(self.github_data_url, headers=self.headers, timeout=5)
            response.raise_for_status()
            github_last_modified = response.headers.get("Last-Modified", "")
            if github_last_modified and github_last_modified > self.data.get("last_updated", ""):
                self.update_data()
        except requests.RequestException:
            pass

    def on_stop(self):
        self.save_data()

class TableViewScreen(Screen):
    def __init__(self, table_key, header, table_data, **kwargs):
        super().__init__(**kwargs)
        self.name = table_key
        self.table_key = table_key
        self.header_text = header
        self.table_data = table_data
        self.build_ui()

    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', spacing=0)

        # Screen header with back button
        screen_header = BoxLayout(size_hint_y=None, height=dp(50), padding=[10, 5], spacing=10)
        with screen_header.canvas.before:
            Color(0.2, 0.4, 0.6, 1)
            screen_header.bg = Rectangle(pos=screen_header.pos, size=screen_header.size)
        screen_header.bind(
            pos=lambda i, v: setattr(screen_header.bg, 'pos', i.pos),
            size=lambda i, v: setattr(screen_header.bg, 'size', i.size))

        back_btn = Button(
            text="← Back",
            size_hint_x=None,
            width=dp(80),
            background_normal='',
            background_color=(0.3, 0.5, 0.7, 1),
            color=(1, 1, 1, 1))
        back_btn.bind(on_press=self.go_back)
        screen_header.add_widget(back_btn)

        title = Label(
            text=self.header_text,
            halign='left',
            valign='middle',
            color=(1, 1, 1, 1),
            size_hint_x=1)
        title.bind(width=lambda *x: setattr(title, 'text_size', (title.width, None)))
        screen_header.add_widget(title)
        main_layout.add_widget(screen_header)

        # Scrollable content area
        scroll_view = ScrollView(bar_width=dp(8))
        content_layout = GridLayout(cols=1, size_hint_y=None, spacing=5, padding=[0, 5, 0, 5])
        content_layout.bind(minimum_height=content_layout.setter('height'))

        # Add table name label
        table_name_label = Label(
            text=f"[b]{self.table_key}[/b]",
            markup=True,
            size_hint_y=None,
            height=dp(40),
            color=(0.2, 0.4, 0.6, 1),
            bold=True,
            halign='left')
        content_layout.add_widget(table_name_label)

        # Determine columns
        if isinstance(self.table_data[0], dict):
            columns = list(self.table_data[0].keys())
            rows = [list(row.values()) for row in self.table_data]
        else:
            columns = self.table_data[0] if len(self.table_data) > 1 else [f"Col {i+1}" for i in range(len(self.table_data[0]))]
            rows = self.table_data[1:] if len(self.table_data) > 1 else self.table_data

        # Add column headers
        header_row = GridLayout(cols=len(columns), size_hint_y=None, height=dp(40), spacing=2)
        with header_row.canvas.before:
            Color(0.3, 0.5, 0.7, 1)
            header_row.bg = Rectangle(pos=header_row.pos, size=header_row.size)
        header_row.bind(
            pos=lambda i, v: setattr(header_row.bg, 'pos', i.pos),
            size=lambda i, v: setattr(header_row.bg, 'size', i.size))

        for col in columns:
            header_cell = Label(
                text=str(col),
                color=(1, 1, 1, 1),
                bold=True,
                halign='center',
                valign='middle')
            header_cell.bind(size=header_cell.setter('text_size'))
            header_row.add_widget(header_cell)
        content_layout.add_widget(header_row)

        # Add data rows
        for i, row in enumerate(rows):
            row_layout = GridLayout(cols=len(columns), size_hint_y=None, height=dp(40), spacing=2)
            row_color = (0.95, 0.95, 0.95, 1) if i % 2 == 0 else (0.85, 0.85, 0.85, 1)
            with row_layout.canvas.before:
                Color(*row_color)
                row_layout.bg = Rectangle(pos=row_layout.pos, size=row_layout.size)
            row_layout.bind(
                pos=lambda i, v: setattr(i.bg, 'pos', i.pos),
                size=lambda i, v: setattr(i.bg, 'size', i.size))

            for value in row:
                cell = Label(
                    text=str(value),
                    color=(0, 0, 0, 1),
                    halign='center',
                    valign='middle')
                cell.bind(size=cell.setter('text_size'))
                row_layout.add_widget(cell)
            content_layout.add_widget(row_layout)

        scroll_view.add_widget(content_layout)
        main_layout.add_widget(scroll_view)
        self.add_widget(main_layout)

    def go_back(self, instance):
        if self.manager:
            self.manager.current = 'main'

class Unit3App(SearchApp):
    def __init__(self, **kwargs):
        super().__init__(json_file="unit3.json", **kwargs)
        self.github_data_url = "https://raw.githubusercontent.com/manoj5176/swgrdetails/main/data/processed_pdf_data.json"

class Unit4App(SearchApp):
    def __init__(self, **kwargs):
        super().__init__(json_file="unit4.json", **kwargs)
        self.github_data_url = "https://raw.githubusercontent.com/manoj5176/swgrdetails/main/data/processed_pdf_data1.json"

class LauncherScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'launcher'
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(20))

        title = Label(
            text="[b]SWGR Data Apps[/b]",
            markup=True,
            font_size=dp(24),
            size_hint_y=None,
            height=dp(60),
            color=(0.2, 0.2, 0.6, 1))
        layout.add_widget(title)

        unit3_btn = Button(
            text="Unit 3 Data",
            size_hint_y=None,
            height=dp(60),
            background_normal='',
            background_color=(0.2, 0.4, 0.6, 1),
            color=(1, 1, 1, 1),
            font_size=dp(20))
        unit3_btn.bind(on_press=self.launch_pdf_search)
        layout.add_widget(unit3_btn)
        
        unit4_btn = Button(
            text="Unit 4 Data",
            size_hint_y=None,
            height=dp(60),
            background_normal='',
            background_color=(0.4, 0.2, 0.6, 1),
            color=(1, 1, 1, 1),
            font_size=dp(20))
        unit4_btn.bind(on_press=self.launch_pdf_search1)
        layout.add_widget(unit4_btn)
        
        unit2_btn = Button(
            text="Coming Soon",
            size_hint_y=None,
            height=dp(60),
            background_normal='',
            background_color=(0.6, 0.2, 0.4, 1),
            color=(1, 1, 1, 1),
            font_size=dp(20))
        layout.add_widget(unit2_btn)

        exit_btn = Button(
            text="Exit",
            size_hint_y=None,
            height=dp(50),
            background_normal='',
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            font_size=dp(18))
        exit_btn.bind(on_press=self.exit_app)
        layout.add_widget(exit_btn)

        self.add_widget(layout)

    def launch_pdf_search(self, instance):
        App.get_running_app().stop()
        Unit3App().run()
    
    def launch_pdf_search1(self, instance):
        App.get_running_app().stop()
        Unit4App().run()

    def exit_app(self, instance):
        App.get_running_app().stop()

class LauncherApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LauncherScreen())
        return sm

if __name__ == "__main__":
    LauncherApp().run()
