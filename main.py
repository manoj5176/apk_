from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.metrics import dp
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.uix.modalview import ModalView
from functools import partial
import requests
import json
from datetime import datetime
import os
from kivy.logger import Logger
from kivy.core.window import Window
import threading

class AutoSizeLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, None)
        self.bind(
            width=lambda *x: self.setter('text_size')(self, (self.width, None)),
            texture_size=self._adjust_height
        )
        self.padding = (dp(5), dp(5))
        self.halign = 'center'
        self.valign = 'middle'
        self.font_size = dp(12)
    
    def _adjust_height(self, instance, texture_size):
        self.height = texture_size[1] + dp(10)

class MainApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nav_history = []
        self.first_run = True

    def build(self):
        self.sm = ScreenManager()
        self.sm.bind(current=self.on_screen_change)
        
        launcher_screen = LauncherScreen(name='launcher')
        self.sm.add_widget(launcher_screen)
        
        return self.sm

    def on_start(self):
        if self.first_run:
            self.first_run = False
            current_screen = self.sm.current_screen
            if hasattr(current_screen, 'check_and_load_data'):
                current_screen.check_and_load_data()

    def on_screen_change(self, instance, screen_name):
        if screen_name not in self.nav_history and screen_name != 'launcher':
            self.nav_history.append(screen_name)
        
        if len(self.nav_history) > 10:
            self.nav_history = self.nav_history[-10:]

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

        unit5_btn = Button(
            text="Unit 5 Data",
            size_hint_y=None,
            height=dp(60),
            background_normal='',
            background_color=(0.4, 0.2, 0.6, 1),
            color=(1, 1, 1, 1),
            font_size=dp(20))
        unit5_btn.bind(on_press=self.launch_unit5)
        layout.add_widget(unit5_btn)
        unit6_btn = Button(
            text="Unit 6 Data",
            size_hint_y=None,
            height=dp(60),
            background_normal='',
            background_color=(0.4, 0.2, 0.6, 1),
            color=(1, 1, 1, 1),
            font_size=dp(20))
        unit6_btn.bind(on_press=self.launch_unit6)
        layout.add_widget(unit6_btn)
       
        unit7_btn = Button(
            text="offsite-data",
            size_hint_y=None,
            height=dp(60),
            background_normal='',
            background_color=(0.4, 0.2, 0.6, 1),
            color=(1, 1, 1, 1),
            font_size=dp(20))
        unit7_btn.bind(on_press=self.launch_unit7)
        layout.add_widget(unit7_btn)
        
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
    def launch_unit5(self, instance):
        app = App.get_running_app()
        if not app.sm.has_screen('unit5'):
            unit5_screen = Unit5Screen(name='unit5')
            app.sm.add_widget(unit5_screen)
        app.sm.current = 'unit5'
    def launch_unit6(self, instance):
        app = App.get_running_app()
        if not app.sm.has_screen('unit6'):
            unit6_screen = Unit6Screen(name='unit6')
            app.sm.add_widget(unit6_screen)
        app.sm.current = 'unit6'
    def launch_unit7(self, instance):
        app = App.get_running_app()
        if not app.sm.has_screen('unit7'):
            unit7_screen = Unit7Screen(name='unit7')
            app.sm.add_widget(unit7_screen)
        app.sm.current = 'unit7'

class BaseAppScreen(Screen):
    github_data_url = StringProperty("")
    last_updated = StringProperty("Never")
    search_results_count = NumericProperty(0)
    
    def __init__(self, json_file, **kwargs):
        super().__init__(**kwargs)
        self.json_file = json_file
        self.data = {"tables": {}, "last_updated": "Never"}
        self.build_ui()
        self._search_trigger = Clock.create_trigger(self._perform_search, 0.5)
        self._first_update_done = False
        self.loading_modal = None
    
    def check_and_load_data(self):
        """Check if JSON exists, download if not, load if exists"""
        if not os.path.exists(self.json_file):
            Logger.info(f"JSON file not found at {self.json_file}, downloading...")
            self.update_data()  # This will trigger the download
        else:
            Logger.info(f"Loading existing JSON file from {self.json_file}")
            try:
                self.load_data()
                self.load_headers_list()
            except Exception as e:
                Logger.error(f"Error loading local data: {str(e)}")
                # If loading fails, try to download fresh data
                self.update_data()

    def update_data(self, instance=None):
        """Manual update triggered by button or automatic first download"""
        try:
            if not self.github_data_url:
                raise ValueError("No data URL configured")
            
            self.status_label.text = "Updating..."
            self.show_loading("Downloading data..." if not os.path.exists(self.json_file) 
                            else "Updating data...")
            
            threading.Thread(target=self._download_and_update, daemon=True).start()
        except Exception as e:
            self.status_label.text = f"Update failed: {str(e)}"
            self.show_error(f"Update failed: {str(e)}")

    def _download_and_update(self):
        """Download data from GitHub and update local file"""
        try:
            Logger.info(f"Downloading data from {self.github_data_url}")
            response = requests.get(self.github_data_url, timeout=10)
            response.raise_for_status()
            new_data = response.json()

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.json_file), exist_ok=True)
            
            with open(self.json_file, 'w') as f:
                json.dump(new_data, f)
            
            Clock.schedule_once(lambda dt: self._update_complete())
        except Exception as e:
            Logger.error(f"Download failed: {str(e)}")
            Clock.schedule_once(lambda dt: self._update_failed(str(e)))

    def _update_complete(self):
        """Called when download and save completes successfully"""
        try:
            self.load_data()
            self.load_headers_list()
            self.status_label.text = f"Last updated: {self.last_updated}"
            Logger.info("Data update completed successfully")
        except Exception as e:
            Logger.error(f"Error completing update: {str(e)}")
            self.status_label.text = "Update completed with errors"
        finally:
            self.dismiss_loading()

    def on_enter(self):
        """Called when screen becomes visible"""
        if not hasattr(self, '_initial_load_done'):
            self._initial_load_done = True
            Clock.schedule_once(lambda dt: self.check_and_load_data(), 0.5)
    
    def load_data(self):
        try:
            if os.path.exists(self.json_file):
                with open(self.json_file, 'r') as f:
                    self.data = json.load(f)
                    self.last_updated = self.data.get("last_updated", "Never")
                    self.status_label.text = f"Last updated: {self.last_updated}"
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
        self.results_scroll = ScrollView(bar_width=dp(8))
        self.results_list = GridLayout(
            cols=1,
            size_hint_y=None,
            spacing=dp(5),
            padding=dp(5))
        self.results_list.bind(minimum_height=self.results_list.setter('height'))
        self.results_scroll.add_widget(self.results_list)
        self.results_screen.add_widget(self.results_scroll)
        self.content_manager.add_widget(self.results_screen)
        
        self.content_manager.current = 'headers'
        self.main_layout.add_widget(self.content_manager)
        
        self.add_widget(self.main_layout)
        Window.bind(on_resize=self._update_layout)
    
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
                text=f" {header}",
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
        self.results_list.clear_widgets()
        self.results_count_label.text = ""
        self.search_results_count = 0
    
    def do_search(self, instance):
        search_term = self.search_input.text.strip().lower()
        if not search_term:
            self.clear_search(instance)
            return
        
        self._search_trigger()
    
    def _perform_search(self, *args):
        search_term = self.search_input.text.strip().lower()
        
        self.results_list.clear_widgets()
        loading = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(40))
        loading.add_widget(Label(text="Searching...", color=(0.3, 0.5, 0.7, 1)))
        self.results_list.add_widget(loading)
        self.content_manager.current = 'results'
        
        try:
            self.search_term = search_term
            self.search_results_count = 0
            self.all_data = self.data.get("tables", {})
            self.current_search_index = 0

            threading.Thread(target=self._threaded_search, daemon=True).start()
        except Exception as e:
            Logger.error(f"Search error: {str(e)}")
            self.results_list.clear_widgets()
            error = Label(text=f"Search error: {str(e)}", color=(0.8, 0.2, 0.2, 1))
            self.results_list.add_widget(error)
    
    def _threaded_search(self):
        results = []
        
        for table_key, table_data in self.all_data.items():
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
                results.append((table_key, header, table_matches if table_matches else table_content, header_matches))
        
        Clock.schedule_once(lambda dt: self._display_search_results(results))
    
    def _display_search_results(self, results):
        self.results_list.clear_widgets()
        self.search_results_count = len(results)
        
        if not results:
            no_results = Label(
                text="No results found",
                size_hint_y=None,
                height=dp(40),
                color=(0.8, 0.2, 0.2, 1))
            self.results_list.add_widget(no_results)
            self.results_count_label.text = "No results found"
            return
        
        for table_key, header, table_data, is_header_match in results:
            header_label = Label(
                text=f"[b]{table_key}: {header}[/b]",
                markup=True,
                size_hint_y=None,
                height=dp(40),
                color=(0.2, 0.4, 0.6, 1),
                bold=True,
                halign='left',
                valign='middle')
            self.results_list.add_widget(header_label)
            
            if isinstance(table_data, list) and table_data:
                try:
                    if isinstance(table_data[0], dict):
                        columns = list(table_data[0].keys())
                        rows = table_data
                    else:
                        columns = table_data[0] if len(table_data) > 1 else [f"Col {i+1}" for i in range(len(table_data[0]))]
                        rows = table_data[1:] if len(table_data) > 1 else table_data
                    
                    header_row = GridLayout(
                        cols=len(columns),
                        size_hint_y=None,
                        spacing=dp(1),
                        padding=(0, dp(1)))
                    
                    with header_row.canvas.before:
                        Color(0.3, 0.5, 0.7, 1)
                        header_row.bg = Rectangle(pos=header_row.pos, size=header_row.size)
                    
                    header_row.bind(
                        pos=lambda i, v: setattr(header_row.bg, 'pos', i.pos),
                        size=lambda i, v: setattr(header_row.bg, 'size', i.size))
                    
                    max_header_height = dp(40)
                    for col in columns:
                        header_cell = AutoSizeLabel(
                            text=str(col),
                            color=(1, 1, 1, 1),
                            bold=True,
                            font_size=dp(14))
                        header_row.add_widget(header_cell)
                        max_header_height = max(max_header_height, header_cell.height)
                    
                    header_row.height = max_header_height
                    self.results_list.add_widget(header_row)
                    
                    for i, row in enumerate(rows):
                        row_layout = GridLayout(
                            cols=len(columns),
                            size_hint_y=None,
                            spacing=dp(1),
                            padding=(0, dp(1)))
                        
                        row_color = (0.95, 0.95, 0.95, 1) if i % 2 == 0 else (0.85, 0.85, 0.85, 1)
                        
                        with row_layout.canvas.before:
                            Color(*row_color)
                            row_layout.bg = Rectangle(pos=row_layout.pos, size=row_layout.size)
                        
                        row_layout.bind(
                            pos=lambda i, v: setattr(i.bg, 'pos', i.pos),
                            size=lambda i, v: setattr(i.bg, 'size', i.size))
                        
                        max_cell_height = dp(40)
                        if isinstance(row, dict):
                            for col in columns:
                                value = row.get(col, "")
                                cell = AutoSizeLabel(
                                    text=str(value) if value is not None else "",
                                    color=(0, 0, 0, 1),
                                    font_size=dp(12))
                                row_layout.add_widget(cell)
                                max_cell_height = max(max_cell_height, cell.height)
                        else:
                            for value in row:
                                cell = AutoSizeLabel(
                                    text=str(value) if value is not None else "",
                                    color=(0, 0, 0, 1),
                                    font_size=dp(12))
                                row_layout.add_widget(cell)
                                max_cell_height = max(max_cell_height, cell.height)
                        
                        row_layout.height = max_cell_height
                        self.results_list.add_widget(row_layout)
                
                except Exception as e:
                    error_label = Label(
                        text=f"Error displaying table data: {str(e)}",
                        size_hint_y=None,
                        height=dp(40),
                        color=(0.8, 0.2, 0.2, 1))
                    self.results_list.add_widget(error_label)
        
        self.results_count_label.text = f"Results: {self.search_results_count}"
    
    def update_data(self, instance=None):
        try:
            if not self.github_data_url:
                raise ValueError("No data URL configured")
                
            self.status_label.text = "Updating..."
            self.show_loading("Updating data...")
            
            threading.Thread(target=self._download_and_update, daemon=True).start()
        except Exception as e:
            self.status_label.text = f"Update failed: {str(e)}"
            self.show_error(f"Update failed: {str(e)}")
    
    def _download_and_update(self):
        try:
            response = requests.get(self.github_data_url, timeout=10)
            response.raise_for_status()
            new_data = response.json()

            self.data["tables"] = new_data
            self.data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(self.json_file, 'w') as f:
                json.dump(self.data, f)
            
            Clock.schedule_once(lambda dt: self._update_complete())
        except Exception as e:
            Clock.schedule_once(lambda dt: self._update_failed(str(e)))
    
    def _update_complete(self):
        self.load_data()
        self.load_headers_list()
        self.status_label.text = f"Last updated: {self.last_updated}"
        self.dismiss_loading()
    
    def _update_failed(self, error):
        Logger.error(f"Update failed: {error}")
        self.status_label.text = f"Update failed: {error}"
        self.dismiss_loading()
        self.show_error(f"Update failed:\n{error}")
    
    def show_loading(self, message):
        if self.loading_modal:
            self.loading_modal.dismiss()
        
        self.loading_modal = ModalView(size_hint=(0.8, 0.3))
        loading_box = BoxLayout(orientation='vertical', padding=dp(20))
        loading_box.add_widget(Label(text=message, font_size=dp(18)))
        self.loading_modal.add_widget(loading_box)
        self.loading_modal.open()
    
    def show_error(self, message):
        error_modal = ModalView(size_hint=(0.8, 0.3))
        error_box = BoxLayout(orientation='vertical', padding=dp(20))
        error_box.add_widget(Label(text=message, color=(0.8, 0.2, 0.2, 1)))
        error_modal.add_widget(error_box)
        error_modal.open()
        Clock.schedule_once(lambda dt: error_modal.dismiss(), 2)
    
    def dismiss_loading(self):
        if self.loading_modal:
            self.loading_modal.dismiss()
            self.loading_modal = None
    
    def go_back(self, instance):
        try:
            if not hasattr(self, 'manager') or not self.manager:
                Logger.warning("No screen manager available")
                return
                
            if 'headers' in self.manager.screen_names:
                self.manager.current = 'headers'
            elif 'launcher' in self.manager.screen_names:
                self.manager.current = 'launcher'
            elif self.manager.screens:
                self.manager.current = self.manager.screens[0].name
        except Exception as e:
            Logger.error(f"Navigation error: {str(e)}")
            if 'launcher' in self.manager.screen_names:
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

        # Screen header
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
            size_hint_x=1,
            text_size=(Window.width - dp(100), None),
            padding=(5, 5))
        screen_header.add_widget(title)
        main_layout.add_widget(screen_header)

        # Scrollable content
        scroll_view = ScrollView(bar_width=dp(8))
        self.content_layout = GridLayout(
            cols=1,
            size_hint_y=None,
            spacing=dp(5),
            padding=[0, dp(5), 0, dp(5)])
        self.content_layout.bind(minimum_height=self.content_layout.setter('height'))

        # Add table name label
        table_name_label = Label(
            text=f"[b]{self.table_key}[/b]",
            markup=True,
            size_hint_y=None,
            height=dp(40),
            color=(0.2, 0.4, 0.6, 1),
            bold=True,
            halign='left',
            valign='middle',
            font_size=dp(16))
        self.content_layout.add_widget(table_name_label)

        # Add headers and rows
        self.add_headers()
        self.add_rows()

        scroll_view.add_widget(self.content_layout)
        main_layout.add_widget(scroll_view)
        self.add_widget(main_layout)

    def add_headers(self):
        if not self.table_data:
            return

        if isinstance(self.table_data[0], dict):
            columns = list(self.table_data[0].keys())
        else:
            columns = self.table_data[0] if len(self.table_data) > 1 else [f"Col {i+1}" for i in range(len(self.table_data[0]))]

        header_row = GridLayout(
            cols=len(columns),
            size_hint_y=None,
            spacing=dp(2),
            padding=(0, dp(1)))
        
        with header_row.canvas.before:
            Color(0.3, 0.5, 0.7, 1)
            header_row.bg = Rectangle(pos=header_row.pos, size=header_row.size)

        header_row.bind(
            pos=lambda i, v: setattr(header_row.bg, 'pos', i.pos),
            size=lambda i, v: setattr(header_row.bg, 'size', i.size))

        max_header_height = dp(40)
        for col in columns:
            header_cell = AutoSizeLabel(
                text=str(col),
                color=(1, 1, 1, 1),
                bold=True,
                font_size=dp(14))
            header_row.add_widget(header_cell)
            max_header_height = max(max_header_height, header_cell.height)

        header_row.height = max_header_height
        self.content_layout.add_widget(header_row)

    def add_rows(self):
        if not self.table_data:
            return

        if isinstance(self.table_data[0], dict):
            columns = list(self.table_data[0].keys())
            rows = self.table_data
        else:
            columns = self.table_data[0] if len(self.table_data) > 1 else [f"Col {i+1}" for i in range(len(self.table_data[0]))]
            rows = self.table_data[1:] if len(self.table_data) > 1 else self.table_data

        for i, row in enumerate(rows):
            row_layout = GridLayout(
                cols=len(columns),
                size_hint_y=None,
                spacing=dp(2),
                padding=(0, dp(1)))

            row_color = (0.95, 0.95, 0.95, 1) if i % 2 == 0 else (0.85, 0.85, 0.85, 1)

            with row_layout.canvas.before:
                Color(*row_color)
                row_layout.bg = Rectangle(pos=row_layout.pos, size=row_layout.size)

            row_layout.bind(
                pos=lambda i, v: setattr(i.bg, 'pos', i.pos),
                size=lambda i, v: setattr(i.bg, 'size', i.size))

            max_cell_height = dp(40)
            if isinstance(row, dict):
                for col in columns:
                    value = row.get(col, "")
                    cell = AutoSizeLabel(
                        text=str(value) if value is not None else "",
                        color=(0, 0, 0, 1),
                        font_size=dp(12))
                    row_layout.add_widget(cell)
                    max_cell_height = max(max_cell_height, cell.height)
            else:
                for value in row:
                    cell = AutoSizeLabel(
                        text=str(value) if value is not None else "",
                        color=(0, 0, 0, 1),
                        font_size=dp(12))
                    row_layout.add_widget(cell)
                    max_cell_height = max(max_cell_height, cell.height)

            row_layout.height = max_cell_height
            self.content_layout.add_widget(row_layout)

    def go_back(self, instance):
        app = App.get_running_app()
        if hasattr(self, 'manager') and self.manager and hasattr(app, 'nav_history'):
            if self.name in app.nav_history:
                app.nav_history.remove(self.name)
            
            for screen_name in reversed(app.nav_history):
                if screen_name in self.manager.screen_names:
                    self.manager.current = screen_name
                    return
            
            if 'headers' in self.manager.screen_names:
                self.manager.current = 'headers'
            elif 'launcher' in self.manager.screen_names:
                self.manager.current = 'launcher'

class Unit3Screen(BaseAppScreen):
    def __init__(self, **kwargs):
        super().__init__(json_file="unit3.json", **kwargs)
        self.github_data_url = "https://raw.githubusercontent.com/manoj5176/swgrdetails/main/data/processed_pdf_data.json"

class Unit4Screen(BaseAppScreen):
    def __init__(self, **kwargs):
        super().__init__(json_file="unit4.json", **kwargs)
        self.github_data_url = "https://raw.githubusercontent.com/manoj5176/swgrdetails/main/data/processed_pdf_data1.json"
class Unit5Screen(BaseAppScreen):
    def __init__(self, **kwargs):
        super().__init__(json_file="unit5.json", **kwargs)
        self.github_data_url = "https://raw.githubusercontent.com/manoj5176/swgrdetails/main/data/processed_pdf_data2.json"
class Unit6Screen(BaseAppScreen):
    def __init__(self, **kwargs):
        super().__init__(json_file="unit6.json", **kwargs)
        self.github_data_url = "https://raw.githubusercontent.com/manoj5176/swgrdetails/main/data/processed_pdf_data3.json"
class Unit7Screen(BaseAppScreen):
    def __init__(self, **kwargs):
        super().__init__(json_file="unit7.json", **kwargs)
        self.github_data_url = "https://raw.githubusercontent.com/manoj5176/swgrdetails/main/data/processed_pdf_data4.json"
if __name__ == "__main__":
    MainApp().run()
