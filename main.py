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

# Custom Widgets
class PerfectFitLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_size = dp(14)
        self.size_hint = (1, None)
        self.valign = 'middle'
        self.halign = 'center'
        self.color = (0, 0, 0, 1)  # Black text
        self.padding = (dp(5), dp(5))
        self.bind(
            width=self.update_text_size,
            texture_size=self.update_height)
    
    def update_text_size(self, instance, width):
        text_length = len(self.text)
        if width < dp(100) and text_length > 20:
            self.font_size = dp(10)
        elif width < dp(150) and text_length > 30:
            self.font_size = dp(12)
        else:
            self.font_size = dp(14)
        self.text_size = (width - self.padding[0]*2, None)
    
    def update_height(self, instance, size):
        self.height = max(dp(40), size[1] + self.padding[1]*2)

class TableCell(BoxLayout):
    def __init__(self, text='', **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, None)
        self.height = dp(40)
        self.padding = (dp(2), dp(2))
        self.orientation = 'vertical'
        
        with self.canvas.before:
            self.bg_color = Color(0.95, 0.95, 0.95, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        
        self.bind(pos=self.update_bg, size=self.update_bg)
        
        self.label = PerfectFitLabel(text=text)
        self.add_widget(self.label)
    
    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def set_text(self, text):
        self.label.text = text
    
    def set_color(self, r, g, b, a):
        self.bg_color.rgba = (r, g, b, a)

class FixedHeaderScrollView(ScrollView):
    def __init__(self, header=None, table_name=None, **kwargs):
        super().__init__(**kwargs)
        self.header = header
        self.table_name = table_name
        self.bind(scroll_y=self._update_header_position)
    
    def _update_header_position(self, instance, value):
        if self.header:
            self.header.y = self.top + (self.scroll_y * (self.height - self.header.height))
        if self.table_name:
            self.table_name.y = self.top + (self.scroll_y * (self.height - self.table_name.height)) + self.header.height

class DataTable(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 1
        self.size_hint = (1, None)
        self.bind(minimum_height=self.setter('height'))
        self.spacing = dp(1)
        self.padding = dp(1)
    
    def build_table(self, columns, data_rows, table_key=None):
        self.clear_widgets()
        
        # Create table name label (fixed while scrolling)
        if table_key:
            self.table_name = Label(
                text=f"[b]{table_key}[/b]",
                markup=True,
                size_hint=(1, None),
                height=dp(40),
                color=(0.2, 0.4, 0.6, 1),
                bold=True)
            self.add_widget(self.table_name)
        
        # Create header row (fixed while scrolling)
        self.header = GridLayout(cols=len(columns), size_hint=(1, None), height=dp(40))
        with self.header.canvas.before:
            Color(0.3, 0.5, 0.7, 1)
            self.header.bg = Rectangle(pos=self.header.pos, size=self.header.size)
        self.header.bind(
            pos=lambda i, v: setattr(self.header.bg, 'pos', i.pos),
            size=lambda i, v: setattr(self.header.bg, 'size', i.size))
        
        for col in columns:
            header_cell = PerfectFitLabel(text=str(col), bold=True, color=(1, 1, 1, 1))
            self.header.add_widget(header_cell)
        
        self.add_widget(self.header)
        
        # Create data rows
        for i, row in enumerate(data_rows):
            row_layout = GridLayout(cols=len(columns), size_hint=(1, None))
            row_layout.bind(minimum_height=row_layout.setter('height'))
            
            for j, value in enumerate(row):
                cell = TableCell(text=str(value))
                cell.set_color(0.95, 0.95, 0.95, 1) if i % 2 == 0 else cell.set_color(0.85, 0.85, 0.85, 1)
                row_layout.add_widget(cell)
            
            self.add_widget(row_layout)

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
        
        # Main screen header with back button
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
        
        # Scrollable content area (now includes table name)
        scroll_view = ScrollView(bar_width=dp(8))
        content_layout = GridLayout(
            cols=1,
            size_hint_y=None,
            spacing=5,
            padding=[0, 5, 0, 5])
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        # Add table name label (now scrolls with content)
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


class MainScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.name = 'main'
        self.app = app
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation="vertical", spacing=dp(5), padding=dp(5))
        
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
            font_size=dp(20),
            color=(1, 1, 1, 1),
            size_hint_x=0.6)
        self.title_label.bind(width=lambda *x: setattr(self.title_label, 'text_size', (self.title_label.width, None)))
        
        self.status_label = Label(
            text=f"Last updated: {self.app.last_updated}",
            color=(1, 1, 1, 1),
            size_hint_x=0.4,
            halign='right',
            font_size=dp(12))
        self.status_label.bind(width=lambda *x: setattr(self.status_label, 'text_size', (self.status_label.width, None)))
        
        header.add_widget(self.title_label)
        header.add_widget(self.status_label)
        layout.add_widget(header)

        # Search Area
        search_box = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(5))
        self.search_input = TextInput(
            hint_text="Search...",
            multiline=False,
            padding=dp(15),
            font_size=dp(16))
        self.search_input.bind(on_text_validate=partial(self.app.do_search, None))
        search_box.add_widget(self.search_input)

        search_btn = Button(
            text="🔍",
            size_hint_x=0.15,
            background_normal='',
            background_color=(0.3, 0.5, 0.7, 1))
        search_btn.bind(on_press=self.app.do_search)
        search_box.add_widget(search_btn)

        clear_btn = Button(
            text="✕",
            size_hint_x=0.15,
            background_normal='',
            background_color=(0.7, 0.3, 0.3, 1))
        clear_btn.bind(on_press=self.app.clear_search)
        search_box.add_widget(clear_btn)

        layout.add_widget(search_box)

        # Action buttons
        action_box = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(5))
        
        update_btn = Button(
            text="Update",
            size_hint_x=0.33,
            background_normal='',
            background_color=(0.3, 0.5, 0.7, 1))
        update_btn.bind(on_press=self.app.update_data)
        action_box.add_widget(update_btn)

        headers_btn = Button(
            text="Headers",
            size_hint_x=0.33,
            background_normal='',
            background_color=(0.3, 0.5, 0.7, 1))
        headers_btn.bind(on_press=self.app.show_headers_list)
        action_box.add_widget(headers_btn)

        back_btn = Button(
            text="Back",
            size_hint_x=0.33,
            background_normal='',
            background_color=(0.3, 0.5, 0.7, 1))
        back_btn.bind(on_press=self.back_to_launcher)
        action_box.add_widget(back_btn)

        layout.add_widget(action_box)

        # Results count label
        self.results_count_label = Label(
            text="",
            size_hint_y=None,
            height=dp(30),
            color=(0.3, 0.5, 0.7, 1),
            bold=True)
        layout.add_widget(self.results_count_label)

        # Headers List Area
        self.headers_scroll = ScrollView(size_hint=(1, 1))
        self.headers_layout = GridLayout(
            cols=1,
            spacing=dp(5),
            size_hint_y=None,
            padding=dp(5))
        self.headers_layout.bind(minimum_height=self.headers_layout.setter('height'))
        self.headers_scroll.add_widget(self.headers_layout)
        layout.add_widget(self.headers_scroll)

        # Main Results Area
        self.main_scroll = ScrollView(size_hint=(1, 0), opacity=0)
        self.results_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(10),
            padding=dp(5))
        self.results_container.bind(minimum_height=self.results_container.setter('height'))
        self.main_scroll.add_widget(self.results_container)
        layout.add_widget(self.main_scroll)

        self.add_widget(layout)
    
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

    def load_data(self):
        try:
            if os.path.exists(self.json_file):
                with open(self.json_file, 'r') as f:
                    self.data = json.load(f)
                    self.last_updated = self.data.get("last_updated", "Never")
            else:
                self.data = {"tables": {}, "last_updated": "Never"}
        except Exception as e:
            Logger.error(f"Error loading JSON: {str(e)}")
            self.data = {"tables": {}, "last_updated": "Never"}

    def save_data(self):
        try:
            with open(self.json_file, 'w') as f:
                json.dump(self.data, f)
        except Exception as e:
            Logger.error(f"Error saving JSON: {str(e)}")

    def build(self):
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
        self.toggle_headers_list(instance)

    def toggle_headers_list(self, instance):
        main_screen = self.main_screen
        if not main_screen:
            return
            
        self.show_headers = not self.show_headers
        
        if self.show_headers:
            anim = Animation(size_hint_y=1, duration=0.2)
            anim &= Animation(opacity=1, duration=0.2)
            anim.start(main_screen.headers_scroll)
            
            anim2 = Animation(size_hint_y=0, duration=0.2)
            anim2 &= Animation(opacity=0, duration=0.2)
            anim2.start(main_screen.main_scroll)
        else:
            anim = Animation(size_hint_y=0, duration=0.2)
            anim &= Animation(opacity=0, duration=0.2)
            anim.start(main_screen.headers_scroll)
            
            anim2 = Animation(size_hint_y=1, duration=0.2)
            anim2 &= Animation(opacity=1, duration=0.2)
            anim2.start(main_screen.main_scroll)

    def clear_search(self, instance):
        main_screen = self.main_screen
        if not main_screen:
            return
            
        if main_screen.search_input:
            main_screen.search_input.text = ""
        
        self.show_headers = True
        anim = Animation(size_hint_y=1, duration=0.2)
        anim &= Animation(opacity=1, duration=0.2)
        anim.start(main_screen.headers_scroll)
        
        anim2 = Animation(size_hint_y=0, duration=0.2)
        anim2 &= Animation(opacity=0, duration=0.2)
        anim2.start(main_screen.main_scroll)
        
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

        self.show_headers = False
        anim = Animation(size_hint_y=0, duration=0.2)
        anim &= Animation(opacity=0, duration=0.2)
        anim.start(main_screen.headers_scroll)
        
        anim2 = Animation(size_hint_y=1, duration=0.2)
        anim2 &= Animation(opacity=1, duration=0.2)
        anim2.start(main_screen.main_scroll)
        
        main_screen.results_container.clear_widgets()

        loading = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(40))
        loading.add_widget(Label(text="Searching...", color=(0.3, 0.5, 0.7, 1)))
        main_screen.results_container.add_widget(loading)

        self.search_term = search_term
        self.search_results_count = 0
        self.all_data = self.data.get("tables", {})
        self.current_search_index = 0

        Clock.schedule_once(partial(self._process_next_table), 0.1)

    def _process_next_table(self, *args):
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
            self._add_table_result(table_key, header, table_matches if table_matches else table_content, header_matches)

        Clock.schedule_once(partial(self._process_next_table), 0.01)

    def _add_table_result(self, table_key, header, table_data, is_header_match):
            main_screen = self.main_screen
            if not main_screen or not main_screen.results_container or not main_screen.results_count_label:
                return

            section = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                spacing=dp(5),
                padding=dp(5))

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
            section.add_widget(header_btn)

            if isinstance(table_data, list) and table_data:
                try:
                    scroll_view = FixedHeaderScrollView(bar_width=dp(8))
                    data_table = DataTable()
                    
                    if isinstance(table_data[0], dict):
                        columns = list(table_data[0].keys())
                        rows = [list(row.values()) for row in table_data]
                    else:
                        columns = table_data[0] if len(table_data) > 1 else [f"Col {i+1}" for i in range(len(table_data[0]))]
                        rows = table_data[1:] if len(table_data) > 1 else table_data
                    
                    data_table.build_table(columns, rows)
                    scroll_view.header = data_table.header
                    
                    # Add scroll view with data
                    scroll_view.add_widget(data_table)
                    section.add_widget(scroll_view)
                    
                    # Calculate height (limit to 300dp max)
                    row_count = len(rows)
                    table_height = min(300, dp(40) + (row_count * dp(40)))
                    scroll_view.height = table_height
                    
                    section.height = header_btn.height + table_height + dp(10)
                except Exception as e:
                    error_label = Label(
                        text=f"Error displaying table: {str(e)}",
                        size_hint_y=None,
                        height=dp(40),
                        color=(0.8, 0.2, 0.2, 1))
                    section.add_widget(error_label)
                    section.height = header_btn.height + dp(50)
            else:
                section.height = header_btn.height + dp(10)

            main_screen.results_container.add_widget(section)
            main_screen.results_count_label.text = f"Results: {self.search_results_count}"


    def on_search_result_click(self, instance):
        if not self.sm:
            return
            
        if instance.table_key in self.sm.screen_names:
            self.sm.current = instance.table_key
        else:
            table_screen = TableViewScreen(
                instance.table_key,
                instance.header_text,
                instance.table_data)
            self.sm.add_widget(table_screen)
            self.sm.current = instance.table_key

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
