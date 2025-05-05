from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.metrics import dp
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ObjectProperty
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
import sqlite3
from datetime import datetime
import pandas as pd

class TableViewScreen(Screen):
    def __init__(self, table_key, header, table_data, **kwargs):
        super().__init__(**kwargs)
        self.name = table_key
        self.table_key = table_key
        self.header = header
        self.table_data = table_data
        self.build_ui()
    
    def build_ui(self):
        # Main layout
        main_layout = BoxLayout(orientation='vertical')
        
        # Fixed header with back button
        header_box = BoxLayout(
            size_hint_y=None, 
            height=dp(60),
            padding=dp(10),
            spacing=dp(10)
        )
        with header_box.canvas.before:
            Color(0.2, 0.4, 0.6, 1)
            self.header_bg = Rectangle(pos=header_box.pos, size=header_box.size)
        
        def update_header_bg(instance, value):
            self.header_bg.pos = instance.pos
            self.header_bg.size = instance.size
        
        header_box.bind(pos=update_header_bg, size=update_header_bg)
        
        back_btn = Button(
            text="← Back",
            size_hint_x=0.2,
            background_color=(0.3, 0.5, 0.7, 1),
            color=(1, 1, 1, 1),
            font_size=dp(16)
        )
        back_btn.bind(on_press=self.go_back)
        header_box.add_widget(back_btn)
        
        title = Label(
            text=f"[b]{self.table_key}:[/b] {self.header[:100]}{'...' if len(self.header) > 100 else ''}",
            markup=True,
            halign='left',
            valign='middle',
            color=(1, 1, 1, 1),
            font_size=dp(16)
        )
        header_box.add_widget(title)
        main_layout.add_widget(header_box)
        
        # Container for table with fixed column headers
        table_container = BoxLayout(orientation='vertical')
        
        # Create column headers (fixed)
        self.column_headers = self._create_column_headers(self.table_data)
        table_container.add_widget(self.column_headers)
        
        # Scrollable data area
        self.data_scroll = ScrollView(
            size_hint=(1, 1),
            bar_width=dp(10),
            scroll_type=['bars', 'content']
        )
        
        # Data grid
        self.data_grid = self._create_data_grid(self.table_data)
        self.data_scroll.add_widget(self.data_grid)
        table_container.add_widget(self.data_scroll)
        
        main_layout.add_widget(table_container)
        self.add_widget(main_layout)
    
    def _create_column_headers(self, table_data):
        try:
            df = pd.DataFrame(table_data)
            col_header = GridLayout(
                cols=len(df.columns),
                size_hint_y=None,
                height=dp(40),
                spacing=dp(2)
            )
            
            with col_header.canvas.before:
                Color(0.3, 0.5, 0.7, 1)
                col_header.bg = Rectangle(pos=col_header.pos, size=col_header.size)

            def update_col_header_bg(instance, value):
                col_header.bg.pos = instance.pos
                col_header.bg.size = instance.size

            col_header.bind(pos=update_col_header_bg, size=update_col_header_bg)

            for col in df.columns:
                header_label = Label(
                    text=str(col),
                    color=(1, 1, 1, 1),
                    bold=True,
                    size_hint=(1, None),
                    height=dp(40),
                    halign='center',
                    valign='middle',
                    font_size=dp(14)
                )
                header_label.bind(size=header_label.setter('text_size'))
                col_header.add_widget(header_label)
            
            return col_header
            
        except Exception as e:
            error_label = Label(
                text=f"Error creating headers: {str(e)}",
                size_hint_y=None,
                height=dp(40),
                color=(0.8, 0.2, 0.2, 1)
            )
            return error_label
    
    def _create_data_grid(self, table_data):
        try:
            df = pd.DataFrame(table_data)
            data_grid = GridLayout(
                cols=len(df.columns),
                size_hint_y=None,
                spacing=dp(2),
                padding=[dp(0)]
            )
            data_grid.bind(minimum_height=data_grid.setter('height'))

            for i, (_, row) in enumerate(df.iterrows()):
                row_color = (0.95, 0.95, 0.95, 1) if i % 2 == 0 else (0.85, 0.85, 0.85, 1)

                for value in row:
                    cell = BoxLayout(
                        size_hint_y=None,
                        height=dp(40),
                        padding=dp(5)
                    )

                    with cell.canvas.before:
                        Color(*row_color)
                        cell.bg = Rectangle(pos=cell.pos, size=cell.size)

                    def update_cell_bg(instance, value):
                        instance.bg.pos = instance.pos
                        instance.bg.size = instance.size

                    cell.bind(pos=update_cell_bg, size=update_cell_bg)

                    value_label = Label(
                        text=str(value),
                        color=(0, 0, 0, 1),
                        halign='center',
                        valign='middle',
                        size_hint=(1, 1),
                        font_size=dp(13)
                    )
                    value_label.bind(size=value_label.setter('text_size'))
                    cell.add_widget(value_label)
                    data_grid.add_widget(cell)

            # Calculate total height
            data_grid.height = len(df) * dp(40)
            return data_grid
            
        except Exception as e:
            error_label = Label(
                text=f"Error creating data grid: {str(e)}",
                size_hint_y=None,
                height=dp(40),
                color=(0.8, 0.2, 0.2, 1)
            )
            return error_label
    
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
        # Main layout with proper spacing
        layout = BoxLayout(orientation="vertical", spacing=dp(10))
        
        # Header with fixed height and proper padding
        header = BoxLayout(
            size_hint_y=None,
            height=dp(60),
            padding=[dp(10), dp(5)],
            spacing=dp(10)
        )
        
        # Background for header
        with header.canvas.before:
            Color(0.2, 0.4, 0.6, 1)
            self.header_bg = Rectangle(pos=header.pos, size=header.size)
        
        def update_header_bg(instance, value):
            self.header_bg.pos = instance.pos
            self.header_bg.size = instance.size
        
        header.bind(pos=update_header_bg, size=update_header_bg)
        
        # Title label with proper text sizing
        self.title_label = Label(
            text="PDF Data Search",
            font_size=dp(24),
            color=(1, 1, 1, 1),
            size_hint_x=0.8,
            halign='left',
            valign='middle'
        )
        self.title_label.bind(
            width=lambda *x: setattr(self.title_label, 'text_size', (self.title_label.width, None))
        )
        
        # Status label with proper sizing
        self.status_label = Label(
            text=f"Last updated: {self.app.last_updated}",
            color=(1, 1, 1, 1),
            size_hint_x=0.2,
            halign='right',
            valign='middle',
            font_size=dp(14)
        )
        self.status_label.bind(
            width=lambda *x: setattr(self.status_label, 'text_size', (self.status_label.width, None)))
        
        header.add_widget(self.title_label)
        header.add_widget(self.status_label)
        layout.add_widget(header)

        # Search Area
        search_box = BoxLayout(size_hint_y=0.15, spacing=dp(10))
        self.search_input = TextInput(
            hint_text="Type to search...",
            multiline=False,
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            padding=dp(10),
            font_size=dp(16)
        )
        self.search_input.bind(on_text_validate=partial(self.app.do_search, None))
        search_box.add_widget(self.search_input)

        search_btn = Button(
            text="Search",
            size_hint_x=0.2,
            background_color=(0.3, 0.5, 0.7, 1),
            color=(1, 1, 1, 1),
            font_size=dp(16)
        )
        search_btn.bind(on_press=self.app.do_search)
        search_box.add_widget(search_btn)

        clear_btn = Button(
            text="Clear",
            size_hint_x=0.2,
            background_color=(0.7, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
            font_size=dp(16)
        )
        clear_btn.bind(on_press=self.app.clear_search)
        search_box.add_widget(clear_btn)

        update_btn = Button(
            text="Update",
            size_hint_x=0.2,
            background_color=(0.3, 0.5, 0.7, 1),
            color=(1, 1, 1, 1),
            font_size=dp(16)
        )
        update_btn.bind(on_press=self.app.update_data)
        search_box.add_widget(update_btn)

        headers_btn = Button(
            text="Headers",
            size_hint_x=0.2,
            background_color=(0.3, 0.5, 0.7, 1),
            color=(1, 1, 1, 1),
            font_size=dp(16)
        )
        headers_btn.bind(on_press=self.app.show_headers_list)
        search_box.add_widget(headers_btn)
        
        back_btn = Button(
            text="Back",
            size_hint_x=0.2,
            background_color=(0.3, 0.5, 0.7, 1),
            color=(1, 1, 1, 1),
            font_size=dp(16)
        )
        back_btn.bind(on_press=self.back_to_launcher)
        search_box.add_widget(back_btn)

        layout.add_widget(search_box)

        # Results count label
        self.results_count_label = Label(
            text="",
            size_hint_y=None,
            height=dp(30),
            color=(0.3, 0.5, 0.7, 1),
            bold=True,
            font_size=dp(14)
        )
        layout.add_widget(self.results_count_label)

        # Headers List Area - Initially fill available space
        self.headers_scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            do_scroll_y=True
        )
        self.headers_layout = GridLayout(
            cols=1,
            spacing=dp(5),
            size_hint_y=None,
            padding=dp(10)
        )
        self.headers_layout.bind(minimum_height=self.headers_layout.setter('height'))
        self.headers_scroll.add_widget(self.headers_layout)
        layout.add_widget(self.headers_scroll)

        # Main Results Area - Initially hidden
        self.main_scroll = ScrollView(
            size_hint=(1, 0),
            opacity=0
        )
        self.results_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(15),
            padding=[dp(10), dp(10), dp(10), dp(10)]
        )
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
    
    def __init__(self, db_name="unit3.db", **kwargs):
        super().__init__(**kwargs)
        self.db_name = db_name
        self.proxies = {"https": "http://10.0.9.40:8080"}
        self.headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json',
            'Cache-Control': 'no-cache'
        }
        self.conn = None
        self.cursor = None

    def build(self):
        self.setup_database()
        self.sm = ScreenManager()
        
        # Create main screen
        main_screen = MainScreen(self)
        self.sm.add_widget(main_screen)
        
        # Setup auto-update
        Clock.schedule_interval(self.check_for_updates, 3600)
        Clock.schedule_once(lambda dt: self.load_headers_list(), 0.5)

        return self.sm

    @property
    def main_screen(self):
        if self.sm and 'main' in self.sm.screen_names:
            return self.sm.get_screen('main')
        return None

    def setup_database(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS pdf_data (
                id INTEGER PRIMARY KEY,
                table_key TEXT,
                header TEXT,
                table_data TEXT,
                last_updated TEXT
            )
            '''
        )
        self.conn.commit()
        self.load_data_from_db()

    def load_data_from_db(self):
        if not self.cursor:
            return
            
        self.cursor.execute("SELECT * FROM pdf_data")
        rows = self.cursor.fetchall()
        if rows:
            self.last_updated = rows[0][4] if len(rows[0]) > 4 else "Never"
            main_screen = self.main_screen
            if main_screen and main_screen.status_label:
                main_screen.status_label.text = f"Last updated: {self.last_updated}"

    def load_headers_list(self):
        main_screen = self.main_screen
        if not main_screen or not main_screen.headers_layout or not self.cursor:
            return
            
        main_screen.headers_layout.clear_widgets()
        
        self.cursor.execute("SELECT DISTINCT table_key, header FROM pdf_data")
        headers = self.cursor.fetchall()

        for table_key, header in headers:
            btn = Button(
                text=f"{table_key}: {header[:50]}{'...' if len(header) > 50 else ''}",
                size_hint_y=None,
                height=dp(40),
                background_color=(0.8, 0.8, 0.9, 1),
                background_normal='',
                color=(0, 0, 0, 1),
                font_size=dp(14)
            )
            btn.table_key = table_key
            btn.header_text = header
            btn.bind(on_press=self.on_header_click)
            main_screen.headers_layout.add_widget(btn)

    def on_header_click(self, instance):
        if not self.cursor or not self.sm:
            return
            
        self.cursor.execute(
            "SELECT table_data FROM pdf_data WHERE table_key = ? LIMIT 1",
            (instance.table_key,))
        result = self.cursor.fetchone()
        if result:
            try:
                table_data = json.loads(result[0])
                # Check if screen already exists
                if instance.table_key in self.sm.screen_names:
                    self.sm.current = instance.table_key
                else:
                    table_screen = TableViewScreen(
                        instance.table_key,
                        instance.header_text,
                        table_data
                    )
                    self.sm.add_widget(table_screen)
                    self.sm.current = instance.table_key
            except json.JSONDecodeError:
                main_screen = self.main_screen
                if main_screen and main_screen.results_container:
                    error_label = Label(
                        text="Error: Could not load table data",
                        size_hint_y=None,
                        height=dp(40),
                        color=(0.8, 0.2, 0.2, 1)
                    )
                    main_screen.results_container.add_widget(error_label)

    def show_headers_list(self, instance):
        self.clear_search(instance)
        self.toggle_headers_list(instance)

    def toggle_headers_list(self, instance):
        main_screen = self.main_screen
        if not main_screen:
            return
            
        self.show_headers = not self.show_headers
        
        if self.show_headers:
            # Show headers, hide results
            anim = Animation(size_hint_y=1, duration=0.2)
            anim &= Animation(opacity=1, duration=0.2)
            anim.start(main_screen.headers_scroll)
            
            anim2 = Animation(size_hint_y=0, duration=0.2)
            anim2 &= Animation(opacity=0, duration=0.2)
            anim2.start(main_screen.main_scroll)
        else:
            # Show results, hide headers
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
        
        # Show headers full screen again
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
                main_screen.status_label.text = "Updating data..."
            
            # Show loading modal
            self.loading_modal = ModalView(size_hint=(0.5, 0.2))
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
            if not self.conn or not self.cursor:
                raise Exception("Database not initialized")
                
            response = requests.get(
                self.github_data_url,
               # proxies=self.proxies,
                headers=self.headers,
                timeout=10,
                verify=False
            )
            response.raise_for_status()
            data = response.json()

            with self.conn:
                self.cursor.execute("DELETE FROM pdf_data")
                for key, value in data.items():
                    self.cursor.execute(
                        '''
                        INSERT INTO pdf_data (table_key, header, table_data, last_updated)
                        VALUES (?, ?, ?, ?)
                        ''',
                        (
                            key,
                            value.get("header", ""),
                            json.dumps(value.get("table", [])),
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        ),
                    )

            self.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            main_screen = self.main_screen
            if main_screen and main_screen.status_label:
                main_screen.status_label.text = f"Last updated: {self.last_updated}"
            
            self.load_headers_list()
            
            # Close loading modal
            if hasattr(self, 'loading_modal'):
                self.loading_modal.dismiss()

        except Exception as e:
            main_screen = self.main_screen
            if main_screen and main_screen.status_label:
                self.main_screen.status_label.text = f"Update failed: {str(e)}"
            if hasattr(self, 'loading_modal'):
                self.loading_modal.dismiss()

    def do_search(self, instance):
        main_screen = self.main_screen
        if not main_screen or not main_screen.search_input or not main_screen.results_container:
            return
            
        search_term = main_screen.search_input.text.strip().lower()
        if not search_term:
            return

        # Hide headers and show results
        self.show_headers = False
        anim = Animation(size_hint_y=0, duration=0.2)
        anim &= Animation(opacity=0, duration=0.2)
        anim.start(main_screen.headers_scroll)
        
        anim2 = Animation(size_hint_y=1, duration=0.2)
        anim2 &= Animation(opacity=1, duration=0.2)
        anim2.start(main_screen.main_scroll)
        
        main_screen.results_container.clear_widgets()

        # Show loading indicator
        loading = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(40))
        loading.add_widget(Label(text="Searching...", color=(0.3, 0.5, 0.7, 1)))
        main_screen.results_container.add_widget(loading)

        self.search_term = search_term
        self.current_search_index = 0
        self.search_results_count = 0
        if self.cursor:
            self.cursor.execute("SELECT table_key, header, table_data FROM pdf_data")
            self.all_data = self.cursor.fetchall()

        Clock.schedule_once(partial(self._process_next_table), 0.1)

    def _process_next_table(self, *args):
        if not hasattr(self, 'all_data') or self.current_search_index >= len(self.all_data):
            if self.search_results_count == 0:
                main_screen = self.main_screen
                if main_screen and main_screen.results_count_label:
                    main_screen.results_count_label.text = "No results found"
                if main_screen and main_screen.results_container:
                    no_results = Label(
                        text="No results found",
                        size_hint_y=None,
                        height=dp(40),
                        color=(0.8, 0.2, 0.2, 1)
                    )
                    main_screen.results_container.add_widget(no_results)
            return

        table_key, header, table_data = self.all_data[self.current_search_index]
        self.current_search_index += 1

        header_matches = self.search_term in header.lower()
        table_matches = []

        try:
            data = json.loads(table_data)
            if isinstance(data, list):
                table_matches = [
                    row for row in data
                    if any(self.search_term in str(value).lower() for value in row.values())
                ]
        except json.JSONDecodeError:
            Clock.schedule_once(partial(self._process_next_table), 0)
            return

        if header_matches or table_matches:
            self.search_results_count += len(table_matches) if table_matches else 1
            self._add_table_result(table_key, header, table_matches if table_matches else data, header_matches)

        Clock.schedule_once(partial(self._process_next_table), 0.01)

    def _add_table_result(self, table_key, header, table_data, is_header_match):
        main_screen = self.main_screen
        if not main_screen or not main_screen.results_container or not main_screen.results_count_label:
            return

        section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(10),
            padding=[dp(10), dp(10), dp(10), dp(10)]
        )

        # Header with click to open in new screen
        header_btn = Button(
            text=f"[b]{table_key}:[/b] {header[:100]}{'...' if len(header) > 100 else ''}",
            size_hint_y=None,
            height=dp(45),
            markup=True,
            halign='left',
            valign='middle',
            background_color=(0.2, 0.6, 0.4, 1) if is_header_match else (0.3, 0.5, 0.7, 1),
            background_normal='',
            color=(1, 1, 1, 1),
            font_size=dp(16)
        )
        header_btn.table_key = table_key
        header_btn.header_text = header
        header_btn.table_data = table_data
        header_btn.bind(on_press=self.on_search_result_click)
        section.add_widget(header_btn)

        # Table content
        if isinstance(table_data, list) and table_data:
            try:
                df = pd.DataFrame(table_data)
                table_widget = self._create_table_widget(df)
                section.add_widget(table_widget)
                
                # Calculate heights
                header_height = header_btn.height
                table_height = table_widget.height
                spacing = section.spacing
                padding = sum(section.padding[1::2])
                
                section.height = header_height + table_height + spacing + padding
                
            except Exception as e:
                error_label = Label(
                    text=f"Error displaying table: {str(e)}",
                    size_hint_y=None,
                    height=dp(40),
                    color=(0.8, 0.2, 0.2, 1)
                )
                section.add_widget(error_label)
                section.height = header_btn.height + dp(50)
        else:
            section.height = header_btn.height + dp(10)

        main_screen.results_container.add_widget(section)
        main_screen.results_count_label.text = f"Results: {self.search_results_count}"

    def _create_table_widget(self, df):
        table_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(2),
            padding=[dp(5), dp(5)]
        )
        
        # Column headers
        col_header = GridLayout(
            cols=len(df.columns),
            size_hint_y=None,
            height=dp(40),
            spacing=dp(5)
        )
        
        with col_header.canvas.before:
            Color(0.3, 0.5, 0.7, 1)
            col_header.bg = Rectangle(pos=col_header.pos, size=col_header.size)

        def update_col_header_bg(instance, value):
            col_header.bg.pos = instance.pos
            col_header.bg.size = instance.size

        col_header.bind(pos=update_col_header_bg, size=update_col_header_bg)

        for col in df.columns:
            col_label = Label(
                text=str(col),
                color=(1, 1, 1, 1),
                bold=True,
                size_hint=(1, None),
                height=dp(40),
                halign='center',
                valign='middle',
                font_size=dp(14)
            )
            col_label.bind(size=col_label.setter('text_size'))
            col_header.add_widget(col_label)

        table_container.add_widget(col_header)

        # Data rows
        data_grid = GridLayout(
            cols=len(df.columns),
            size_hint_y=None,
            spacing=dp(2),
            padding=[dp(0)]
        )
        data_grid.bind(minimum_height=data_grid.setter('height'))

        for i, (_, row) in enumerate(df.iterrows()):
            row_color = (0.95, 0.95, 0.95, 1) if i % 2 == 0 else (0.85, 0.85, 0.85, 1)

            for value in row:
                cell = BoxLayout(
                    size_hint_y=None,
                    height=dp(40),
                    padding=dp(5)
                )

                with cell.canvas.before:
                    Color(*row_color)
                    cell.bg = Rectangle(pos=cell.pos, size=cell.size)

                def update_cell_bg(instance, value):
                    instance.bg.pos = instance.pos
                    instance.bg.size = instance.size

                cell.bind(pos=update_cell_bg, size=update_cell_bg)

                value_label = Label(
                    text=str(value),
                    color=(0, 0, 0, 1),
                    halign='center',
                    valign='middle',
                    size_hint=(1, 1),
                    font_size=dp(13)
                )
                value_label.bind(size=value_label.setter('text_size'))
                cell.add_widget(value_label)
                data_grid.add_widget(cell)

        table_container.add_widget(data_grid)
        
        # Calculate total table height
        table_container.height = dp(40) + (len(df) * dp(40)) + dp(10)
        
        return table_container

    def on_search_result_click(self, instance):
        if not self.sm:
            return
            
        # Check if screen already exists
        if instance.table_key in self.sm.screen_names:
            self.sm.current = instance.table_key
        else:
            table_screen = TableViewScreen(
                instance.table_key,
                instance.header_text,
                instance.table_data
            )
            self.sm.add_widget(table_screen)
            self.sm.current = instance.table_key

    def check_for_updates(self, dt):
        try:
            if not self.github_data_url:
                return
                
            response = requests.head(
                self.github_data_url,
               # proxies=self.proxies,
                headers=self.headers,
                timeout=5,
                verify=False
            )
            response.raise_for_status()
            github_last_modified = response.headers.get("Last-Modified", "")
            if github_last_modified and self.cursor:
                self.cursor.execute("SELECT last_updated FROM pdf_data LIMIT 1")
                local_last_updated = self.cursor.fetchone()
                if local_last_updated and github_last_modified > local_last_updated[0]:
                    self.update_data()
        except requests.RequestException:
            pass

    def on_stop(self):
        if self.conn:
            self.conn.close()

class Unit3App(SearchApp):
    def __init__(self, **kwargs):
        super().__init__(db_name="unit3.db", **kwargs)
        self.github_data_url = "https://raw.githubusercontent.com/manoj5176/swgrdetails/main/data/processed_pdf_data.json"

class Unit4App(SearchApp):
    def __init__(self, **kwargs):
        super().__init__(db_name="unit4.db", **kwargs)
        self.github_data_url = "https://raw.githubusercontent.com/manoj5176/swgrdetails/main/data/processed_pdf_data1.json"

class LauncherScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'launcher'
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(40))
        
        # Title
        title = Label(
            text="[b]SWGR Data Applications[/b]",
            markup=True,
            font_size=dp(28),
            size_hint_y=None,
            height=dp(80),
            color=(0.2, 0.2, 0.6, 1))
        layout.add_widget(title)
        
        # Unit 3 Button (PDF Data Search)
        unit3_btn = Button(
            text="Unit 3 - Data Search",
            size_hint_y=None,
            height=dp(80),
            background_normal='',
            background_color=(0.2, 0.4, 0.6, 1),
            color=(1, 1, 1, 1),
            font_size=dp(22),
            bold=True)
        unit3_btn.bind(on_press=self.launch_pdf_search)
        layout.add_widget(unit3_btn)
        
        # Unit 4 Button
        unit4_btn = Button(
            text="Unit 4 - Data Search",
            size_hint_y=None,
            height=dp(80),
            background_normal='',
            background_color=(0.4, 0.2, 0.6, 1),
            color=(1, 1, 1, 1),
            font_size=dp(22))
        unit4_btn.bind(on_press=self.launch_pdf_search1)
        layout.add_widget(unit4_btn)
        
        # Placeholder for Unit 5
        unit2_btn = Button(
            text="Unit 5 - Coming Soon",
            size_hint_y=None,
            height=dp(80),
            background_normal='',
            background_color=(0.6, 0.2, 0.4, 1),
            color=(1, 1, 1, 1),
            font_size=dp(22))
        layout.add_widget(unit2_btn)
        
        # Exit Button
        exit_btn = Button(
            text="Exit",
            size_hint_y=None,
            height=dp(60),
            background_normal='',
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            font_size=dp(18))
        exit_btn.bind(on_press=self.exit_app)
        layout.add_widget(exit_btn)
        
        self.add_widget(layout)
    
    def launch_pdf_search(self, instance):
        # Stop the launcher and start Unit 3 app
        App.get_running_app().stop()
        Unit3App().run()
    
    def launch_pdf_search1(self, instance):
        # Stop the launcher and start Unit 4 app
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
