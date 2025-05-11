from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
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

class MainApp(App):
    def build(self):
        self.sm = ScreenManager()
        
        # Create and add launcher screen
        launcher_screen = LauncherScreen(name='launcher')
        self.sm.add_widget(launcher_screen)
        
        return self.sm

class LauncherScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
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
        
        # Unit 3 Button
        unit3_btn = Button(
            text="Unit 3 Data",
            size_hint_y=None,
            height=dp(60),
            background_normal='',
            background_color=(0.2, 0.4, 0.6, 1),
            color=(1, 1, 1, 1),
            font_size=dp(20))
        unit3_btn.bind(on_press=self.launch_unit3)
        layout.add_widget(unit3_btn)
        
        # Unit 4 Button
        unit4_btn = Button(
            text="Unit 4 Data",
            size_hint_y=None,
            height=dp(60),
            background_normal='',
            background_color=(0.4, 0.2, 0.6, 1),
            color=(1, 1, 1, 1),
            font_size=dp(20))
        unit4_btn.bind(on_press=self.launch_unit4)
        layout.add_widget(unit4_btn)
        
        # Exit Button
        exit_btn = Button(
            text="Exit",
            size_hint_y=None,
            height=dp(50),
            background_normal='',
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            font_size=dp(18))
        exit_btn.bind(on_press=lambda x: App.get_running_app().stop())
        layout.add_widget(exit_btn)
        
        self.add_widget(layout)
    
    def launch_unit3(self, instance):
        app = App.get_running_app()
        if not app.sm.has_screen('unit3'):
            unit3_screen = Unit3Screen(name='unit3')
            app.sm.add_widget(unit3_screen)
        app.sm.current = 'unit3'
    
    def launch_unit4(self, instance):
        app = App.get_running_app()
        if not app.sm.has_screen('unit4'):
            unit4_screen = Unit4Screen(name='unit4')
            app.sm.add_widget(unit4_screen)
        app.sm.current = 'unit4'

class BaseAppScreen(Screen):
    github_data_url = StringProperty("")
    last_updated = StringProperty("Never")
    search_results_count = NumericProperty(0)
    
    def __init__(self, json_file, **kwargs):
        super().__init__(**kwargs)
        self.json_file = json_file
        self.data = {"tables": {}, "last_updated": "Never"}
        self.load_data()
        self.build_ui()
        Clock.schedule_interval(self.check_for_updates, 3600)
    
    def load_data(self):
        try:
            if os.path.exists(self.json_file):
                with open(self.json_file, 'r') as f:
                    self.data = json.load(f)
                    self.last_updated = self.data.get("last_updated", "Never")
        except Exception as e:
            Logger.error(f"Error loading JSON: {str(e)}")
    
    def save_data(self):
        try:
            with open(self.json_file, 'w') as f:
                json.dump(self.data, f)
        except Exception as e:
            Logger.error(f"Error saving JSON: {str(e)}")
    
    def build_ui(self):
        self.main_layout = BoxLayout(orientation='vertical')
        
        # Header
        self.header = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            padding=dp(5),
            spacing=dp(5))
        
        with self.header.canvas.before:
            Color(0.2, 0.4, 0.6, 1)
            self.header_bg = Rectangle(pos=self.header.pos, size=self.header.size)
        
        self.header.bind(
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
            text=f"Last updated: {self.last_updated}",
            color=(1, 1, 1, 1),
            size_hint_x=0.4,
            halign='right',
            valign='middle',
            font_size=dp(10),
            text_size=(Window.width * 0.35, None),
            shorten=True)
        
        self.header.add_widget(self.title_label)
        self.header.add_widget(self.status_label)
        self.main_layout.add_widget(self.header)

        # Search Area
        search_box = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(5))
        self.search_input = TextInput(
            hint_text="Search...",
            multiline=False,
            padding=[dp(15), dp(10)],
            font_size=dp(14),
            size_hint_x=0.7)
        self.search_input.bind(on_text_validate=partial(self.do_search, None))
        
        search_btn = Button(
            text="search",
            size_hint_x=0.15,
            font_size=dp(14),
            background_normal='',
            background_color=(0.3, 0.5, 0.7, 1))
        search_btn.bind(on_press=self.do_search)
        
        clear_btn = Button(
            text="clear",
            size_hint_x=0.15,
            font_size=dp(14),
            background_normal='',
            background_color=(0.7, 0.3, 0.3, 1))
        clear_btn.bind(on_press=self.clear_search)
        
        search_box.add_widget(self.search_input)
        search_box.add_widget(search_btn)
        search_box.add_widget(clear_btn)
        self.main_layout.add_widget(search_box)

        # Action buttons
        action_box = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(5))
        
        buttons = [
            ("Update", self.update_data),
            ("Headers", self.show_headers_list),
            ("Back", self.go_back)
        ]
        
        for text, callback in buttons:
            btn = Button(
                text=text,
                font_size=dp(12),
                background_normal='',
                background_color=(0.3, 0.5, 0.7, 1))
            btn.bind(on_press=callback)
            action_box.add_widget(btn)
        
        self.main_layout.add_widget(action_box)

        self.results_count_label = Label(
            text="",
            size_hint_y=None,
            height=dp(25),
            color=(0.3, 0.5, 0.7, 1),
            bold=True,
            font_size=dp(12))
        self.main_layout.add_widget(self.results_count_label)

        # Content Area
        self.content_manager = ScreenManager(transition=NoTransition())
        
        # Headers screen
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
        self.content_manager.add_widget(self.headers_screen)

        # Results screen
        self.results_screen = Screen(name='results')
        self.results_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(5),
            padding=dp(5))
        self.results_container.bind(minimum_height=self.results_container.setter('height'))

        self.main_scroll = ScrollView(size_hint=(1, 1))
        self.main_scroll.add_widget(self.results_container)
        self.results_screen.add_widget(self.main_scroll)
        self.content_manager.add_widget(self.results_screen)
        
        self.content_manager.current = 'headers'
        self.main_layout.add_widget(self.content_manager)
        
        self.add_widget(self.main_layout)
        Window.bind(on_resize=self._update_layout)
        Clock.schedule_once(self.load_headers_list, 0.5)
    
    def _update_layout(self, *args):
        self.title_label.text_size = (Window.width * 0.55, None)
        self.status_label.text_size = (Window.width * 0.35, None)
        self.title_label.texture_update()
        self.status_label.texture_update()
    
    def load_headers_list(self, *args):
        self.headers_layout.clear_widgets()
        
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
            self.headers_layout.add_widget(btn)
    
    def on_header_click(self, instance):
        table_data = self.data.get("tables", {}).get(instance.table_key, {}).get("table", [])
        
        if instance.table_key in self.manager.screen_names:
            self.manager.current = instance.table_key
        else:
            table_screen = TableViewScreen(
                instance.table_key,
                instance.header_text,
                table_data)
            self.manager.add_widget(table_screen)
            self.manager.current = instance.table_key
    
    def show_headers_list(self, instance):
        self.clear_search(instance)
        self.content_manager.current = 'headers'
    
    def clear_search(self, instance):
        self.search_input.text = ""
        self.content_manager.current = 'headers'
        self.results_container.clear_widgets()
        self.results_count_label.text = ""
    
    def update_data(self, instance=None):
        try:
            self.status_label.text = "Updating..."
            
            self.loading_modal = ModalView(size_hint=(0.8, 0.3))
            loading_box = BoxLayout(orientation='vertical', padding=dp(20))
            loading_box.add_widget(Label(text="Updating data...", font_size=dp(18)))
            self.loading_modal.add_widget(loading_box)
            self.loading_modal.open()
            
            Clock.schedule_once(self._perform_update, 0.1)
        except Exception as e:
            self.status_label.text = f"Update failed: {str(e)}"
    
    def _perform_update(self, *args):
        try:
            response = requests.get(
                self.github_data_url,
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
        search_term = self.search_input.text.strip().lower()
        if not search_term:
            return

        self.results_container.clear_widgets()
        
        loading = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(40))
        loading.add_widget(Label(text="Searching...", color=(0.3, 0.5, 0.7, 1)))
        self.results_container.add_widget(loading)
        
        self.content_manager.current = 'results'
        self.search_term = search_term
        self.search_results_count = 0
        self.all_data = self.data.get("tables", {})
        self.current_search_index = 0

        Clock.schedule_once(partial(self.process_next_table), 0.1)
    
    def process_next_table(self, *args):
        if not hasattr(self, 'all_data'):
            if self.search_results_count == 0:
                self.results_count_label.text = "No results found"
                no_results = Label(
                    text="No results found",
                    size_hint_y=None,
                    height=dp(40),
                    color=(0.8, 0.2, 0.2, 1))
                self.results_container.add_widget(no_results)
            return

        tables = list(self.all_data.items())
        if self.current_search_index >= len(tables):
            if self.search_results_count == 0:
                self.results_count_label.text = "No results found"
                no_results = Label(
                    text="No results found",
                    size_hint_y=None,
                    height=dp(40),
                    color=(0.8, 0.2, 0.2, 1))
                self.results_container.add_widget(no_results)
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
        result_item = BoxLayout(
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
        
        result_item.add_widget(header_btn)

        if isinstance(table_data, list) and table_data:
            try:
                data_table = GridLayout(
                    cols=1,
                    size_hint_y=None,
                    spacing=dp(1),
                    padding=dp(1))
                data_table.bind(minimum_height=data_table.setter('height'))
                
                if isinstance(table_data[0], dict):
                    columns = list(table_data[0].keys())
                    rows = table_data
                else:
                    columns = table_data[0] if len(table_data) > 1 else [f"Col {i+1}" for i in range(len(table_data[0]))]
                    rows = table_data[1:] if len(table_data) > 1 else table_data
                
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
                
                row_count = len(rows)
                table_height = dp(40) + (row_count * dp(40))
                data_table.height = table_height
                
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

        self.results_container.add_widget(result_item)
        self.results_count_label.text = f"Results: {self.search_results_count}"
    
    def update_header_bg(self, instance, value):
        instance.bg.pos = instance.pos
        instance.bg.size = instance.size
    
    def update_row_bg(self, instance, value):
        with instance.canvas.before:
            Color(*instance.row_color)
            instance.bg.pos = instance.pos
            instance.bg.size = instance.size
    
    def on_search_result_click(self, instance):
        table_key = getattr(instance, 'table_key', None)
        header_text = getattr(instance, 'header_text', "")
        table_data = getattr(instance, 'table_data', [])
        
        if not table_key:
            Logger.error("Clicked button has no table_key")
            return
            
        if table_key in self.manager.screen_names:
            self.manager.current = table_key
        else:
            table_screen = TableViewScreen(
                table_key,
                header_text,
                table_data)
            self.manager.add_widget(table_screen)
            self.manager.current = table_key
    
    def check_for_updates(self, dt):
        try:
            if not self.github_data_url:
                return
                
            response = requests.head(
                self.github_data_url,
                timeout=5,
                verify=False)
            response.raise_for_status()
            github_last_modified = response.headers.get("Last-Modified", "")
            if github_last_modified and github_last_modified > self.data.get("last_updated", ""):
                self.update_data()
        except requests.RequestException:
            pass
    
    def go_back(self, instance):
        self.manager.current = 'launcher'

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
            self.manager.current = 'launcher'

class Unit3Screen(BaseAppScreen):
    def __init__(self, **kwargs):
        super().__init__(json_file="unit3.json", **kwargs)
        self.github_data_url = "https://raw.githubusercontent.com/manoj5176/swgrdetails/main/data/processed_pdf_data.json"

class Unit4Screen(BaseAppScreen):
    def __init__(self, **kwargs):
        super().__init__(json_file="unit4.json", **kwargs)
        self.github_data_url = "https://raw.githubusercontent.com/manoj5176/swgrdetails/main/data/processed_pdf_data1.json"

if __name__ == "__main__":
    MainApp().run()
