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
from functools import partial
import requests
import json
from datetime import datetime
import os
from kivy.logger import Logger
from kivy.core.window import Window
from kivy.utils import platform
class MainScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.name = 'main'
        self.app = app
        self.build_ui()

    def build_ui(self):
        main_layout = BoxLayout(
            orientation="vertical",
            spacing=dp(5),
            padding=[dp(10), dp(5), dp(10), dp(5)])

        # Header
        header = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            padding=dp(5),
            spacing=dp(5))

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
            shorten=True,
            shorten_from='right')

        self.status_label = Label(
            text=f"Last updated: {self.app.last_updated}",
            color=(1, 1, 1, 1),
            size_hint_x=0.4,
            halign='right',
            valign='middle',
            font_size=dp(10),
            text_size=(Window.width * 0.35, None),
            shorten=True)

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

        buttons = [
            ("Update", self.app.update_data),
            ("Headers", self.app.show_headers_list),
            ("Back", self.back_to_launcher)
        ]

        for text, callback in buttons:
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

        # Content Area with proper Screen management
        content_area = BoxLayout(orientation='vertical', size_hint=(1, 1))

        # Create headers screen
        self.headers_screen = Screen(name='headers')
        self.headers_scroll = ScrollView()
        self.headers_layout = GridLayout(
            cols=1,
            spacing=dp(5),
            size_hint_y=None,
            padding=dp(5))
        self.headers_layout.bind(minimum_height=self.headers_layout.setter('height'))
        self.headers_scroll.add_widget(self.headers_layout)
        self.headers_screen.add_widget(self.headers_scroll)

        # Create main results screen
        self.results_screen = Screen(name='results')
        self.results_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(5),
            padding=dp(5))
        self.results_container.bind(minimum_height=self.results_container.setter('height'))

        # Create a single ScrollView that wraps everything
        self.main_scroll = ScrollView(size_hint=(1, 1))
        self.main_scroll.add_widget(self.results_container)
        self.results_screen.add_widget(self.main_scroll)

        # Create screen manager
        self.content_switcher = ScreenManager()
        self.content_switcher.add_widget(self.headers_screen)
        self.content_switcher.add_widget(self.results_screen)
        content_area.add_widget(self.content_switcher)

        # Start with headers view visible
        self.content_switcher.current = 'headers'

        main_layout.add_widget(content_area)
        self.add_widget(main_layout)

        Window.bind(on_resize=self._update_layout)
        self._update_layout()

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

    def __init__(self, json_file="unit3.json", **kwargs):
        super().__init__(**kwargs)
        self.json_file = json_file
        self.data = {"tables": {}, "last_updated": "Never"}
        self.headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json',
            'Cache-Control': 'no-cache'}

    def get_data_path(self, filename):
        """Get appropriate storage path for the current platform"""
        if platform == 'android':
            from android.storage import app_storage_path
            storage_path = app_storage_path()
            os.makedirs(storage_path, exist_ok=True)
            return os.path.join(storage_path, filename)
        return filename

    def ensure_data_file(self):
        """Ensure data file exists, download if needed"""
        json_path = self.get_data_path(self.json_file)
        
        # If file doesn't exist or is empty, try to download
        if not os.path.exists(json_path) or os.path.getsize(json_path) == 0:
            return self.download_data_file()
        return json_path

    def download_data_file(self):
        """Download data file from GitHub"""
        try:
            if not self.github_data_url:
                Logger.error("No GitHub URL configured")
                return None

            response = requests.get(self.github_data_url, headers=self.headers)
            response.raise_for_status()
            
            json_path = self.get_data_path(self.json_file)
            data = response.json()
            data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(json_path, 'w') as f:
                json.dump(data, f)
                
            return json_path
        except Exception as e:
            Logger.error(f"Data download failed: {str(e)}")
            return None

    def load_data(self):
        """Load data with fallback to packaged version"""
        # First try downloaded version
        json_path = self.get_data_path(self.json_file)
        
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r') as f:
                    self.data = json.load(f)
                    self.last_updated = self.data.get("last_updated", "Never")
                return
            except Exception as e:
                Logger.error(f"Error loading downloaded JSON: {str(e)}")

        # Fallback to packaged version
        try:
            from kivy.resources import resource_find
            packaged_file = resource_find(self.json_file)
            if packaged_file:
                with open(packaged_file, 'r') as f:
                    self.data = json.load(f)
                    self.last_updated = "Packaged version"
        except Exception as e:
            Logger.error(f"Error loading packaged JSON: {str(e)}")
            self.data = {"tables": {}, "last_updated": "Never"}

    def save_data(self):
        """Save data to writable location"""
        try:
            json_path = self.get_data_path(self.json_file)
            with open(json_path, 'w') as f:
                json.dump(self.data, f)
        except Exception as e:
            Logger.error(f"Error saving JSON: {str(e)}")

    def build(self):
        self.ensure_data_file()
        self.load_data()
        self.sm = ScreenManager()
        main_screen = MainScreen(self)
        self.sm.add_widget(main_screen)
        Clock.schedule_interval(self.check_for_updates, 3600)
        Clock.schedule_once(lambda dt: self.load_headers_list(), 0.5)
        return self.sm

    @property
    def main_screen(self):
        if self.sm and 'main' in self.sm.screen_names:
            return self.sm.get_screen('main')
        return None

    def load_headers_list(self):
        main_screen = self.main_screen
        if not main_screen or not main_screen.headers_layout:
            return

        main_screen.headers_layout.clear_widgets()

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
            main_screen.headers_layout.add_widget(btn)

    def on_header_click(self, instance):
        if not self.sm:
            return

        table_data = self.data.get("tables", {}).get(instance.table_key, {}).get("table", [])

        if instance.table_key in self.sm.screen_names:
            self.sm.current = instance.table_key
        else:
            table_screen = TableViewScreen(
                instance.table_key,
                instance.header_text,
                table_data)
            self.sm.add_widget(table_screen)
            self.sm.current = instance.table_key

    def show_headers_list(self, instance):
        self.clear_search(instance)
        main_screen = self.main_screen
        if main_screen:
            main_screen.content_switcher.current = 'headers'

    def clear_search(self, instance):
        main_screen = self.main_screen
        if not main_screen:
            return

        if main_screen.search_input:
            main_screen.search_input.text = ""

        main_screen.content_switcher.current = 'headers'

        if main_screen.results_container:
            main_screen.results_container.clear_widgets()
        if main_screen.results_count_label:
            main_screen.results_count_label.text = ""

    def update_data(self, instance=None):
        try:
            main_screen = self.main_screen
            if main_screen and main_screen.status_label:
                main_screen.status_label.text = "Updating..."

            self.loading_modal = ModalView(size_hint=(0.8, 0.3))
            loading_box = BoxLayout(orientation='vertical', padding=dp(20))
            loading_box.add_widget(Label(text="Updating data...", font_size=dp(18)))
            self.loading_modal.add_widget(loading_box)
            self.loading_modal.open()

            Clock.schedule_once(self._perform_update, 0.1)
        except Exception as e:
            main_screen = self.main_screen
            if main_screen and main_screen.status_label:
                main_screen.status_label.text = f"Update failed: {str(e)}"

    def _perform_update(self, *args):
        try:
            response = requests.get(
                self.github_data_url,
                headers=self.headers,
                timeout=10,
                verify=False)
            response.raise_for_status()
            new_data = response.json()

            self.data["tables"] = new_data
            self.data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.last_updated = self.data["last_updated"]

            self.save_data()
            self.load_headers_list()

            if hasattr(self, 'loading_modal'):
                self.loading_modal.dismiss()

        except Exception as e:
            Logger.error(f"Update failed: {str(e)}")
            if hasattr(self, 'loading_modal'):
                self.loading_modal.dismiss()
                self.loading_modal = ModalView(size_hint=(0.8, 0.3))
                error_box = BoxLayout(orientation='vertical', padding=dp(20))
                error_box.add_widget(Label(text=f"Update failed:\n{str(e)}", color=(0.8, 0.2, 0.2, 1)))
                self.loading_modal.add_widget(error_box)
                self.loading_modal.open()
                Clock.schedule_once(lambda dt: self.loading_modal.dismiss(), 2)

    def do_search(self, instance):
        main_screen = self.main_screen
        if not main_screen or not main_screen.search_input or not main_screen.results_container:
            return

        search_term = main_screen.search_input.text.strip().lower()
        if not search_term:
            return

        # Clear previous results
        main_screen.results_container.clear_widgets()

        # Show loading indicator
        loading = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(40))
        loading.add_widget(Label(text="Searching...", color=(0.3, 0.5, 0.7, 1)))
        main_screen.results_container.add_widget(loading)

        # Switch to results view
        main_screen.content_switcher.current = 'results'

        # Perform search
        self.search_term = search_term
        self.search_results_count = 0
        self.all_data = self.data.get("tables", {})
        self.current_search_index = 0

        Clock.schedule_once(partial(self.process_next_table), 0.1)

    def process_next_table(self, *args):
        if not hasattr(self, 'all_data'):
            if self.search_results_count == 0:
                main_screen = self.main_screen
                if main_screen and main_screen.results_count_label:
                    main_screen.results_count_label.text = "No results found"
                if main_screen and main_screen.results_container:
                    no_results = Label(
                        text="No results found",
                        size_hint_y=None,
                        height=dp(40),
                        color=(0.8, 0.2, 0.2, 1))
                    main_screen.results_container.add_widget(no_results)
            return

        tables = list(self.all_data.items())
        if self.current_search_index >= len(tables):
            if self.search_results_count == 0:
                main_screen = self.main_screen
                if main_screen and main_screen.results_count_label:
                    main_screen.results_count_label.text = "No results found"
                if main_screen and main_screen.results_container:
                    no_results = Label(
                        text="No results found",
                        size_hint_y=None,
                        height=dp(40),
                        color=(0.8, 0.2, 0.2, 1))
                    main_screen.results_container.add_widget(no_results)
            return

        table_key, table_data = tables[self.current_search_index]
        self.current_search_index += 1

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
            self.add_table_result(table_key, header, table_matches if table_matches else table_content, header_matches)

        Clock.schedule_once(partial(self.process_next_table), 0.01)

    def add_table_result(self, table_key, header, table_data, is_header_match):
        main_screen = self.main_screen
        if not main_screen or not main_screen.results_container or not main_screen.results_count_label:
            return

        # Create result item (without its own ScrollView)
        result_item = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(5),
            padding=dp(5))

        # Add header button with attributes
        header_btn = Button(
            text=f"[b]{table_key}:[/b] {header[:50]}{'...' if len(header) > 50 else ''}",
            size_hint_y=None,
            height=dp(45),
            markup=True,
            halign='left',
            background_normal='',
            background_color=(0.2, 0.6, 0.4, 1) if is_header_match else (0.3, 0.5, 0.7, 1),
            color=(1, 1, 1, 1))
        header_btn.table_key = table_key
        header_btn.header_text = header
        header_btn.table_data = table_data
        header_btn.bind(on_press=self.on_search_result_click)

        result_item.add_widget(header_btn)

        if isinstance(table_data, list) and table_data:
            try:
                # Create the data table container (no ScrollView here)
                data_table = GridLayout(
                    cols=1,
                    size_hint_y=None,
                    spacing=dp(1),
                    padding=dp(1))
                data_table.bind(minimum_height=data_table.setter('height'))

                # Determine columns and rows (your existing code)
                if isinstance(table_data[0], dict):
                    columns = list(table_data[0].keys())
                    rows = table_data
                else:
                    columns = table_data[0] if len(table_data) > 1 else [f"Col {i+1}" for i in range(len(table_data[0]))]
                    rows = table_data[1:] if len(table_data) > 1 else table_data

                # Add header row (your existing code)
                header_row = GridLayout(
                    cols=len(columns),
                    size_hint_y=None,
                    height=dp(40),
                    spacing=dp(1))

                with header_row.canvas.before:
                    Color(0.3, 0.5, 0.7, 1)
                    header_row.bg = Rectangle(pos=header_row.pos, size=header_row.size)

                header_row.bind(
                    pos=self.update_header_bg,
                    size=self.update_header_bg)

                for col in columns:
                    header_cell = Label(
                        text=str(col),
                        color=(1, 1, 1, 1),
                        bold=True,
                        halign='center',
                        valign='middle',
                        font_size=dp(14))
                    header_cell.bind(size=header_cell.setter('text_size'))
                    header_row.add_widget(header_cell)

                data_table.add_widget(header_row)

                # Add data rows (your existing code)
                for i, row in enumerate(rows):
                    row_layout = GridLayout(
                        cols=len(columns),
                        size_hint_y=None,
                        height=dp(40),
                        spacing=dp(1))

                    row_layout.row_color = (0.95, 0.95, 0.95, 1) if i % 2 == 0 else (0.85, 0.85, 0.85, 1)

                    with row_layout.canvas.before:
                        Color(*row_layout.row_color)
                        row_layout.bg = Rectangle(pos=row_layout.pos, size=row_layout.size)

                    row_layout.bind(
                        pos=self.update_row_bg,
                        size=self.update_row_bg)

                    if isinstance(row, dict):
                        for col in columns:
                            value = row.get(col, "")
                            cell = Label(
                                text=str(value) if value is not None else "",
                                color=(0, 0, 0, 1),
                                halign='center',
                                valign='middle',
                                font_size=dp(14))
                            cell.bind(size=cell.setter('text_size'))
                            row_layout.add_widget(cell)
                    else:
                        for value in row:
                            cell = Label(
                                text=str(value) if value is not None else "",
                                color=(0, 0, 0, 1),
                                halign='center',
                                valign='middle',
                                font_size=dp(14))
                            cell.bind(size=cell.setter('text_size'))
                            row_layout.add_widget(cell)

                    data_table.add_widget(row_layout)

                # Calculate height for this table only
                row_count = len(rows)
                table_height = dp(40) + (row_count * dp(40))
                data_table.height = table_height

                # Add table directly to result item (no ScrollView)
                result_item.add_widget(data_table)
                result_item.height = header_btn.height + data_table.height + dp(10)

            except Exception as e:
                Logger.error(f"Error displaying table: {str(e)}")
                error_label = Label(
                    text=f"Error displaying table data",
                    size_hint_y=None,
                    height=dp(40),
                    color=(0.8, 0.2, 0.2, 1))
                result_item.add_widget(error_label)
                result_item.height = header_btn.height + dp(50)
        else:
            result_item.height = header_btn.height + dp(10)

        # Add result to container
        main_screen.results_container.add_widget(result_item)
        main_screen.results_count_label.text = f"Results: {self.search_results_count}"

    def update_header_bg(self, instance, value):
        instance.bg.pos = instance.pos
        instance.bg.size = instance.size

    def update_row_bg(self, instance, value):
        with instance.canvas.before:
            Color(*instance.row_color)
            instance.bg.pos = instance.pos
            instance.bg.size = instance.size

    def on_search_result_click(self, instance):
        if not self.sm:
            return

        # Safely get the attributes with defaults
        table_key = getattr(instance, 'table_key', None)
        header_text = getattr(instance, 'header_text', "")
        table_data = getattr(instance, 'table_data', [])

        if not table_key:
            Logger.error("Clicked button has no table_key")
            return

        if table_key in self.sm.screen_names:
            self.sm.current = table_key
        else:
            table_screen = TableViewScreen(
                table_key,
                header_text,
                table_data)
            self.sm.add_widget(table_screen)
            self.sm.current = table_key

    def check_for_updates(self, dt):
        try:
            if not self.github_data_url:
                return

            response = requests.head(
                self.github_data_url,
                headers=self.headers,
                timeout=5,
                verify=False)
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
        screen_header = BoxLayout(
            size_hint_y=None, 
            height=dp(50),
            padding=[10, 5],
            spacing=10)

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
        content_layout = GridLayout(
            cols=1,
            size_hint_y=None,
            spacing=5,
            padding=[0, 5, 0, 5])
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
        header_row = GridLayout(
            cols=len(columns),
            size_hint_y=None,
            height=dp(40),
            spacing=2)

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
            row_layout = GridLayout(
                cols=len(columns),
                size_hint_y=None,
                height=dp(40),
                spacing=2)

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
