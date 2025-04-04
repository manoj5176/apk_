import os
import json
import requests
import base64
import uuid
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle,RoundedRectangle
from kivy.metrics import dp
from kivy.uix.progressbar import ProgressBar
from kivy.uix.anchorlayout import AnchorLayout
from kivy.core.window import Window
import sys

# GitHub API details
# File to store the access token
CONFIG_FILE = "config5.json"
def load_access_token():
    """Load the access token from the config file."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                return config.get("access_token")
        except Exception as e:
            print(f"Error loading access token: {e}")
    return None

# Save access token to config file
def save_access_token(token):
    """Save the access token to the config file."""
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump({"access_token": token}, f)
        return True
    except Exception as e:
        print(f"Error saving access token: {e}")
        return False


CREDENTIALS_REPO = "manoj5176/app_credentials"  # Private repository
CREDENTIALS_FILE = "admin.json"
CREDENTIALS_FILE1 = "admin_credentials.json"
BRANCH = "main"
def check_internet():
    """Check internet connection with timeout"""
    try:
        response = requests.get("https://www.google.com", timeout=5)
        return True
    except (requests.ConnectionError, requests.Timeout):
        return False

def show_no_internet_popup():
    """Show popup that closes the app when no internet"""
    def close_app(_):
        App.get_running_app().stop()
        sys.exit(0)

    content = BoxLayout(orientation='vertical', padding=10)
    content.add_widget(Label(
        text="No Internet Connection\nApp will close",
        halign='center'
    ))
    close_btn = Button(text="OK", size_hint=(1, 0.4))
    close_btn.bind(on_press=close_app)
    content.add_widget(close_btn)

    popup = Popup(
        title="Connection Error",
        content=content,
        size_hint=(0.7, 0.4),
        auto_dismiss=False
    )
    popup.open()

# Registration Screen
class RegistrationScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.create_ui()
        Window.bind(on_keyboard=self.on_keyboard)
        Window.bind(on_keyboard_height=self.on_keyboard_height)
        Window.keyboard_anim_args={'d':.2,'t':'in_out_expo'}
        Window.softinput_mode="below_target"
        self.add_widget(self.layout)

    def create_ui(self):
        self.layout.clear_widgets()
        self.scroll_view = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        self.content_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.content_layout.bind(minimum_height=self.content_layout.setter('height'))
        self.scroll_view.add_widget(self.content_layout)

        for i in range(5):
            self.content_layout.add_widget(Label(
                text=f"Sample Content {i}",
                size_hint_y=None,
                height=dp(50),
                font_size='18sp',
                color=(0, 0, 0, 1)
            ))

        self.layout.add_widget(self.scroll_view)
        self.anchor_layout = AnchorLayout(anchor_y='bottom', size_hint_y=None, height=dp(150))
        self.form_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(150), spacing=10)
        self.token_input = TextInput(
            hint_text="Enter Access Token",
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            padding=[10, 0],
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1)
        )
        self.form_layout.add_widget(self.token_input)
        register_button = Button(
            text="Register",
            size_hint_y=None,
            height=dp(50),
            background_color=(0.2, 0.6, 1, 1),
            color=(1, 1, 1, 1)
        )
        register_button.bind(on_press=self.register_device)
        self.form_layout.add_widget(register_button)
        self.anchor_layout.add_widget(self.form_layout)
        self.layout.add_widget(self.anchor_layout)

    def on_keyboard(self, window, key, *args):
        if key == 27:  # Escape key
            return True
        return False

    def on_keyboard_height(self, window, height):
        if height > 0:
            self.scroll_view.height = Window.height - height - dp(150)
            self.anchor_layout.y = height
        else:
            self.scroll_view.height = Window.height
            self.anchor_layout.y = 0

    def register_device(self, instance):
        token = self.token_input.text.strip()
        if not token:
            self.show_popup("Error", "Access token cannot be empty.")
            return
        if save_access_token(token):
            self.show_popup("Success", "Device registered successfully!")
            app = App.get_running_app()
            app.access_token = token
            app.refresh_all_screens()
            Clock.schedule_once(lambda dt: restart_app(), 1)
        else:
            self.show_popup("Error", "Failed to save access token.")

    def show_popup(self, title, message):
        popup = Popup(title=title, size_hint=(0.8, 0.4))
        popup.content = Label(text=message)
        popup.open()

def restart_app():
    python = sys.executable
    os.execl(python, python, *sys.argv)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.create_ui()

        # Bind keyboard events
        Window.bind(on_keyboard=self.on_keyboard)
        Window.bind(on_keyboard_height=self.on_keyboard_height)
        Window.keyboard_anim_args={'d':.2,'t':'in_out_expo'}
        Window.softinput_mode="below_target"

        # Add the layout to the screen
        self.add_widget(self.layout)

    def create_ui(self):
        self.layout.clear_widgets()

        # Add a ScrollView for the main content
        self.scroll_view = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        self.content_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.content_layout.bind(minimum_height=self.content_layout.setter('height'))
        self.scroll_view.add_widget(self.content_layout)

        # Add some example content (optional)
        for i in range(5):
            self.content_layout.add_widget(Label(
                text=f"Sample Content {i}",
                size_hint_y=None,
                height=dp(50),
                font_size='18sp',
                color=(0, 0, 0, 1)
            ))

        self.layout.add_widget(self.scroll_view)

        # Add an AnchorLayout to keep the registration form at the bottom
        self.anchor_layout = AnchorLayout(anchor_y='bottom', size_hint_y=None, height=dp(150))
        self.form_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(150), spacing=10)

        # Token Input
        self.token_input = TextInput(
            hint_text="Enter Access Token",
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            padding=[10, 0],
            background_color=(1, 1, 1, 1),  # White background
            foreground_color=(0, 0, 0, 1)  # Black text
        )
        self.form_layout.add_widget(self.token_input)

        # Register Button
        register_button = Button(
            text="Register",
            size_hint_y=None,
            height=dp(50),
            background_color=(0.2, 0.6, 1, 1),  # Blue color
            color=(1, 1, 1, 1)  # White text
        )
        register_button.bind(on_press=self.register_device)
        self.form_layout.add_widget(register_button)

        self.anchor_layout.add_widget(self.form_layout)
        self.layout.add_widget(self.anchor_layout)

    def on_keyboard(self, window, key, *args):
        # Handle keyboard events (optional)
        pass

    def on_keyboard_height(self, window, height):
        # Adjust the layout when the keyboard opens/closes
        if height > 0:
            # Keyboard is open
            self.scroll_view.height = Window.height - height - dp(150)  # Subtract the form height
            self.anchor_layout.y = height  # Move the form above the keyboard
        else:
            # Keyboard is closed
            self.scroll_view.height = Window.height  # Reset to full height
            self.anchor_layout.y = 0  # Reset the form position

    def register_device(self, instance):
        token = self.token_input.text.strip()
        if not token:
            self.show_popup("Error", "Access token cannot be empty.")
            return

        # Save the token to the config file
        if save_access_token(token):
            self.show_popup("Success", "Device registered successfully!")
            app = App.get_running_app()
            app.access_token = token  # Store the token in the App instance
            app.refresh_all_screens()  # Refresh all screens

            # Restart the app after successful registration
            Clock.schedule_once(lambda dt: restart_app(), 1)  # Restart after 1 second
        else:
            self.show_popup("Error", "Failed to save access token.")

    def show_popup(self, title, message):
        popup = Popup(title=title, size_hint=(0.8, 0.4))
        popup.content = Label(text=message)
        popup.open()
def restart_app():
    """Restart the application."""
    python = sys.executable  # Get the current Python interpreter
    os.execl(python, python, *sys.argv)  # Restart the script

# GitHub API to fetch credentials
def fetch_admin_credentials(token):
    #GITHUB_TOKEN= base64.b64decode(GITHUB_TOKEN1.encode("utf-8")).decode("utf-8")
    GITHUB_TOKEN = token
    if not GITHUB_TOKEN:
        raise Exception("Access token not found. Please register the device first.")
    #GITHUB_TOKEN = load_access_token(CONFIG_FILE.access_token)

    url = f"https://api.github.com/repos/{CREDENTIALS_REPO}/contents/{CREDENTIALS_FILE}"
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    proxies = {
    "https": "http://10.0.9.40:8080"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        file_data = response.json()

        # Debugging: Print the GitHub API response
        print("GitHub API Response:", file_data)

        if "content" in file_data:
            # Decode the Base64-encoded content
            encoded_content = file_data["content"]
            decoded_content = base64.b64decode(encoded_content).decode('utf-8')

            # Debugging: Print the decoded content
            print("Decoded Content:", decoded_content)

            if decoded_content.strip():  # Check if content is not empty
                return json.loads(decoded_content)
            else:
                raise Exception("The decoded content is empty.")
        else:
            raise Exception("The 'content' key is missing in the API response.")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch admin credentials: {e}")
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to decode JSON content: {e}")
        

# Fetch admin credentials
try:
    access_token = load_access_token()
    if access_token:
        ADMIN_CREDENTIALS = fetch_admin_credentials(access_token)
    else:
        ADMIN_CREDENTIALS = {"username": "admin", "password": "admin123"}  # Fallback credentials
except Exception as e:
    print(f"Error fetching admin credentials: {e}")
    ADMIN_CREDENTIALS = {"username": "admin", "password": "admin123"}  # Fallback credentials
# Base Screen Class
class BaseScreen(Screen):
    def on_pre_enter(self, *args):
        #"""Check internet before screen appears"""
        if not check_internet():
            show_no_internet_popup()
            return False
        return True
    def show_loading(self, message="Loading..."):
        self.loading_popup = Popup(title=message, size_hint=(0.6, 0.2))
        self.loading_popup.content = ProgressBar()
        self.loading_popup.open()

    def hide_loading(self):
        if self.loading_popup:
            self.loading_popup.dismiss()

    def show_popup(self, title, message):
        popup = Popup(title=title, size_hint=(0.8, 0.4))
        popup.content = Label(text=message)
        popup.open()

    def refresh_data(self, instance):
        Clock.schedule_once(self._refresh_ui, 0.1)

    def _refresh_ui(self, dt):
        """Subclasses must implement this method to refresh their UI."""
        raise NotImplementedError("Subclasses must implement this method")


class LoginScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.create_ui()
        self.add_widget(self.layout)
        try:
            ADMIN_CREDENTIALS = fetch_admin_credentials(App.get_running_app().access_token)
        except Exception as e:
            print(f"Error fetching admin credentials: {e}")
        ADMIN_CREDENTIALS = {"username": "admin", "password": "admin123"}  # Fallback credentials

        Window.bind(on_keyboard=self.on_keyboard)
        Window.bind(on_keyboard_height=self.on_keyboard_height)
        Window.keyboard_anim_args={'d':.2,'t':'in_out_expo'}
        Window.softinput_mode="below_target"

    def _refresh_ui(self, dt):
        """Clear input fields when the screen is opened."""
        self.username_input.text = ""
        self.password_input.text = ""

    def create_ui(self):
        self.layout.clear_widgets()

        # Heading
        heading = Label(
            text="Sign In to start your session...",
            size_hint_y=None,
            height=dp(50),
            font_size='24sp',
            bold=True,
            color=(0.2, 0.6, 1, 1)  # Blue color
        )
        self.layout.add_widget(heading)

        # Employee ID Input
        self.username_input = TextInput(
            hint_text="Employee Id",
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            padding=[10, 0],
            background_color=(1, 1, 1, 1),  # White background
            foreground_color=(0, 0, 0, 1)  # Black text
        )
        self.layout.add_widget(self.username_input)

        # Password Input
        self.password_input = TextInput(
            hint_text="Password",
            multiline=False,
            password=True,  # Hide password input
            size_hint_y=None,
            height=dp(40),
            padding=[10, 0],
            background_color=(1, 1, 1, 1),  # White background
            foreground_color=(0, 0, 0, 1)  # Black text
        )
        self.layout.add_widget(self.password_input)

        # Sign In Button
        sign_in_button = Button(
            text="Sign In",
            size_hint_y=None,
            height=dp(50),
            background_color=(0.2, 0.6, 1, 1),  # Blue color
            color=(1, 1, 1, 1)  # White text
        )
        sign_in_button.bind(on_press=self.authenticate)
        self.layout.add_widget(sign_in_button)

        # Skip Sign In Button
        skip_button = Button(
            text="Skip Sign In",
            size_hint_y=None,
            height=dp(50),
            background_color=(0.8, 0.2, 0.2, 1),  # Red color
            color=(1, 1, 1, 1)  # White text
        )
        skip_button.bind(on_press=self.backtomain)
        self.layout.add_widget(skip_button)

    def on_keyboard(self, window, key, *args):
        if key == 27:  # Escape key
            return True
        return False

    def on_keyboard_height(self, window, height):
        if height > 0:
            self.layout.height = Window.height - height
        else:
            self.layout.height = Window.height

    def authenticate(self, instance):
        username = self.username_input.text
        password = self.password_input.text

        if username == ADMIN_CREDENTIALS["username"] and password == ADMIN_CREDENTIALS["password"]:
            self.show_popup("Success", "Login successful!")
            self.manager.current = "admin"
        else:
            self.show_popup("Error", "Invalid username or password")

    def backtomain(self, instance):
        self.manager.current = 'main'

    def show_popup(self, title, message):
        popup = Popup(title=title, size_hint=(0.8, 0.4))
        popup.content = Label(text=message)
        self.refresh_data(None)
        popup.open()

    def refresh_data(self, instance):
        """Refresh the UI by fetching the latest questions and rebuilding the UI."""
        # Schedule the UI update using Clock
        Clock.schedule_once(self._refresh_ui, 0.1)  # Schedule after 0.1 seconds

    def _refresh_ui(self, dt):
        """Internal method to refresh the UI."""
        self.create_ui()





# GitHub API to fetch questions
def fetch_questions(token):
    GITHUB_TOKEN = token
    if not GITHUB_TOKEN:
        raise Exception("Access token not found. Please register the device first.")
    #GITHUB_TOKEN = load_access_token(CONFIG_FILE.access_token)
    url = f"https://api.github.com/repos/{CREDENTIALS_REPO}/contents/{CREDENTIALS_FILE1}"
    headers = {'Authorization': 'token ' + GITHUB_TOKEN }
    proxies = {
    "https": "http://10.0.9.40:8080"}

    response = requests.get(url, headers=headers)
    print(f"API Response: {response.status_code} - {response.text}")  # Debugging
    if response.status_code == 200:
        file_data = response.json()
        if "content" in file_data:
            # Decode the content from base64
            content = base64.b64decode(file_data['content']).decode("utf-8")
            return json.loads(content)
        else:
            raise Exception("The 'content' key is missing in the API response.")
    else:
        raise Exception(f"Failed to fetch questions: {response.status_code} - {response.text}")

# Update questions on GitHub
def update_github_file(token,questions):
    GITHUB_TOKEN = token
    if not GITHUB_TOKEN:
        raise Exception("Access token not found. Please register the device first.")
    #GITHUB_TOKEN = load_access_token(CONFIG_FILE.access_token)
    url = f"https://api.github.com/repos/{CREDENTIALS_REPO}/contents/{CREDENTIALS_FILE1}"
    headers = {'Authorization': 'token ' + GITHUB_TOKEN }
    proxies = {
    "https": "http://10.0.9.40:8080"}

    # Fetch existing file details
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        file_data = response.json()
        if "sha" in file_data:
            sha = file_data['sha']

            # Update the file
            updated_content = json.dumps(questions, indent=2)
            update_data = {
                "message": "Update questions from app",
                "content": base64.b64encode(updated_content.encode("utf-8")).decode("utf-8"),
                "sha": sha,
                "branch": BRANCH
            }

            update_response = requests.put(url, headers=headers, json=update_data)
            if update_response.status_code == 200:
                return True
            else:
                raise Exception(f"Failed to update file on GitHub: {update_response.status_code} - {update_response.text}")
        else:
            raise Exception("The 'sha' key is missing in the API response.")
    else:
        raise Exception(f"Failed to fetch file details from GitHub: {response.status_code} - {response.text}")
    

from kivy.uix.widget import Widget

class QuestionCard(BoxLayout):
    def __init__(self, question, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(10)
        self.padding = dp(15)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))
        self.question_id = question['id']
        
        # Card background
        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # Light gray background
            self.rect = RoundedRectangle(
                size=self.size,
                pos=self.pos,
                radius=[dp(15)])
        self.bind(size=self._update_rect, pos=self._update_rect)

        # Question Label (with proper text wrapping)
        self.question_label = Label(
            text=f"[b]Q:[/b] {question['question']}",
            size_hint=(1, None),
            height=dp(50),  # Initial height
            markup=True,
            font_size='18sp',
            color=(0, 0, 0, 1),
            text_size=(Window.width - dp(50), None),  # Constrain width
            halign='left',
            valign='top',
            padding=(dp(5), dp(5)))
        self.question_label.bind(
            texture_size=lambda lbl, val: setattr(lbl, 'height', val[1] + dp(10)))
        self.add_widget(self.question_label)

        # Options container
        self.options_container = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            spacing=dp(5))
        self.options_container.bind(minimum_height=self.options_container.setter('height'))

        # Add each option with checkbox
        self.option_widgets = []
        for option in question['options']:
            option_row = BoxLayout(
                orientation='horizontal',
                size_hint=(1, None),
                height=dp(40),
                spacing=dp(10))
            
            # Left padding
            option_row.add_widget(Widget(size_hint_x=None, width=dp(10)))
            
            # Checkbox
            checkbox = CheckBox(
                size_hint=(None, None),
                size=(dp(30), dp(30)),
                group=str(question['id']) if len(question['answers']) == 1 else None,
                color=(0.2, 0.6, 1, 1))  # Blue color
            
            # Bind checkbox
            checkbox.bind(active=lambda instance, value, opt=option: 
                self.on_checkbox_active(instance, value, opt))
            
            # Option label
            option_label = Label(
                text=option.capitalize(),
                size_hint=(1, 1),
                font_size='16sp',
                color=(0.3, 0.3, 0.3, 1),
                text_size=(Window.width - dp(100), None),  # Constrain width
                halign='left',
                valign='middle',
                padding=(dp(5), 0))
            option_label.bind(texture_size=option_label.setter('size'))
            
            option_row.add_widget(checkbox)
            option_row.add_widget(option_label)
            self.options_container.add_widget(option_row)
            self.option_widgets.append((option, checkbox))

        # Set options container height
        self.options_container.height = len(question['options']) * dp(40)
        self.add_widget(self.options_container)

        # Reference link if available
        if question.get('reference'):
            self.ref_label = Label(
                text=f"[ref={question['reference']}]View Reference[/ref]",
                size_hint=(1, None),
                height=dp(30),
                markup=True,
                font_size='14sp',
                color=(0.2, 0.4, 0.8, 1),
                halign='left',
                padding=(dp(15), 0))
            #self.ref_label.bind(on_ref_press=lambda instance, value: webbrowser.open(value))
            self.add_widget(self.ref_label)

        # Calculate final card height
        self.height = (self.question_label.height + 
                      self.options_container.height + 
                      (dp(30) if question.get('reference') else 0) + 
                      dp(20))  # Extra padding

    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos

    def on_checkbox_active(self, checkbox, value, option):
        # Get the parent screen (MainScreen)
        parent_screen = None
        parent = self.parent
        while parent:
            if hasattr(parent, 'user_answers'):  # This identifies MainScreen
                parent_screen = parent
                break
            parent = parent.parent
        
        if parent_screen:
            if value:
                if self.question_id not in parent_screen.user_answers:
                    parent_screen.user_answers[self.question_id] = []
                parent_screen.user_answers[self.question_id].append(option)
            else:
                if (self.question_id in parent_screen.user_answers and 
                    option in parent_screen.user_answers[self.question_id]):
                    parent_screen.user_answers[self.question_id].remove(option)
            
            # Update visual state of all checkboxes for this question
            self.update_checkbox_states()

    def update_checkbox_states(self):
        # Get the parent screen (MainScreen)
        parent_screen = None
        parent = self.parent
        while parent:
            if hasattr(parent, 'user_answers'):
                parent_screen = parent
                break
            parent = parent.parent
        
        if parent_screen and self.question_id in parent_screen.user_answers:
            selected_options = parent_screen.user_answers[self.question_id]
            for option, checkbox in self.option_widgets:
                checkbox.active = option in selected_options
class MainScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_answers = {}
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.progress_bar = ProgressBar(max=100, value=0)  # Add ProgressBar
        self.layout.add_widget(self.progress_bar)
        self.fetch_questions()
        self.create_ui()
        self.add_widget(self.layout)

    def fetch_questions(self):
        try:
            self.questions = fetch_questions(App.get_running_app().access_token)
        except Exception as e:
            print(f"Error fetching questions: {e}")
            self.questions = []

    def _refresh_ui(self, dt):
        """Refresh the UI by fetching the latest questions and rebuilding the UI."""
        self.fetch_questions()
        self.create_ui()

    def create_ui(self):
        self.layout.clear_widgets()

        if not self.questions:  # Handle empty list
            no_questions_label = Label(
                text="No questions found.",
                size_hint_y=None,
                height=dp(50),
                font_size='22sp',
                bold=True,
                color=(0.8, 0.2, 0.2, 1)  # Red color
            )
            self.layout.add_widget(no_questions_label)
            return

        # Add questions to the UI
        self.scroll_view = ScrollView(size_hint=(1, 0.8), size=(Window.width, Window.height))
        self.scroll_content = BoxLayout(orientation='vertical', spacing=10, padding=10, size_hint_y=None)
        self.scroll_content.bind(minimum_height=self.scroll_content.setter('height'))

        self.question_cards = []
        for question in self.questions:
            question_card = QuestionCard(question)
            self.scroll_content.add_widget(question_card)
            self.question_cards.append(question_card)

        self.scroll_view.add_widget(self.scroll_content)
        self.layout.add_widget(self.scroll_view)

        # Add Submit and Admin Login buttons
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10, padding=10)
        submit_button = Button(
            text="Submit",
            background_color=(0.2, 0.6, 1, 1),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(50)
        )
        submit_button.bind(on_press=self.show_results)
        admin_button = Button(
            text="Admin Login",
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(50)
        )
        admin_button.bind(on_press=self.switch_to_login)
        button_layout.add_widget(submit_button)
        button_layout.add_widget(admin_button)
        self.layout.add_widget(button_layout)

        # Add the title at the bottom
        title_label = Label(
            text="Questionnaire",
            size_hint_y=None,
            height=50,
            font_size='24sp',
            bold=True,
            color=(0.2, 0.6, 1, 1)
        )
        self.layout.add_widget(title_label)

    def start_progress_animation(self):
        """Start the progress bar animation."""
        self.progress_bar.value = 0
        self.animation_event = Clock.schedule_interval(self.update_progress, 0.1)  # Update every 0.1 seconds

    def stop_progress_animation(self):
        """Stop the progress bar animation."""
        if self.animation_event:
            self.animation_event.cancel()
            self.animation_event = None

    def update_progress(self, dt):
        """Update the progress bar value."""
        if self.progress_bar.value < self.progress_bar.max:
            self.progress_bar.value += 1  # Increment progress
        else:
            self.stop_progress_animation()  # Stop when progress reaches 100%

    def _update_rect(self, instance, value):
        """Update the size and position of the background rectangle."""
        self.rect.size = instance.size
        self.rect.pos = instance.pos

    def update_selected_options(self, question_id):
        selected_options = self.user_answers.get(question_id, [])
        for question_card in self.question_cards:
            if question_card.question_id == question_id:
                for option, checkbox in question_card.option_layouts:
                    checkbox.active = (option, checkbox) in selected_options

    def show_results(self, instance):
        correct_count = 0
        results = []

        for question in self.questions:
            question_id = question['id']
            user_answers = [
                option for option in self.user_answers.get(question_id, [])
                if isinstance(option, str)
            ]
            correct_answers = question['answers']
            is_correct = set(user_answers) == set(correct_answers)  # Compare sets for multiple answers

            if is_correct:
                correct_count += 1

            results.append({
                "question": question['question'],
                "user_answers": user_answers,
                "correct_answers": correct_answers,
                "is_correct": is_correct,
                "reference": question.get('reference')
            })

        result_text = f"Correct Answers: {correct_count}/{len(self.questions)}\n\n"
        for result in results:
            result_text += (
                f"Question: {result['question']}\n"
                f"Your Answers: {', '.join(result['user_answers'])}\n"
                f"Correct Answers: {', '.join(result['correct_answers'])}\n"
                f"Reference: {result.get('reference', 'N/A')}\n\n"
            )
        
        self.show_fitting_popup(
            title='Results',
            message=result_text
        )
        self.refresh_data(None)
        self.user_answers.clear()

    def show_fitting_popup(self, title, message):
        # Improved popup that auto-adjusts to message length.
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Label with dynamic text wrapping
        label = Label(
            text=message,
            text_size=(Window.width * 0.7, None),  # Constrain width to 70% of window
            halign="center",
            valign="middle",
            size_hint_y=None,
            padding=(10, 10))
        label.bind(texture_size=lambda lbl, val: setattr(lbl, 'height', val[1]))
        
        # ScrollView for long messages
        scroll = ScrollView(size_hint=(1, 0.8))
        scroll.add_widget(label)
        content.add_widget(scroll)
        
        # OK button
        ok_button = Button(
            text="OK", 
            size_hint=(1, 0.2),
            background_color=(0.2, 0.6, 1, 1))
        ok_button.bind(on_press=lambda x: popup.dismiss())
        content.add_widget(ok_button)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.6),
            auto_dismiss=False
        )
        popup.open()

    def refresh_data(self, instance=None):
        """Refresh the UI by fetching the latest questions and rebuilding the UI."""
        # Schedule the UI update using Clock
        Clock.schedule_once(self._refresh_ui, 0.1)  # Schedule after 0.1 seconds

    def _refresh_ui(self, dt):
        """Internal method to refresh the UI."""
        self.fetch_questions()
        self.create_ui()

    def switch_to_admin(self, instance):
        self.manager.current = "admin"

    def switch_to_login(self, instance):
        self.manager.current = "login"
class AdminScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_answers = {}
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.progress_bar = ProgressBar(max=100, value=0)
        self.layout.add_widget(self.progress_bar)
        self.fetch_questions()
        self.create_ui()
        self.add_widget(self.layout)

    def fetch_questions(self):
        try:
            self.questions = fetch_questions(App.get_running_app().access_token)
        except Exception as e:
            print(f"Error fetching questions: {e}")
            self.questions = []

    def create_ui(self):
        self.layout.clear_widgets()

        # Add a heading with improved styling
        heading = Label(
            text="Admin Panel",
            size_hint=(1, None),
            height=dp(60),
            font_size='24sp',
            bold=True,
            color=(0.2, 0.6, 1, 1),
            padding=(10, 10)
        )
        self.layout.add_widget(heading)

        if not self.questions:
            no_questions_label = Label(
                text="No questions found.",
                size_hint=(1, None),
                height=dp(50),
                font_size='18sp',
                color=(0.8, 0.2, 0.2, 1)
            )
            self.layout.add_widget(no_questions_label)
            return

        # Main scrollable area
        self.scroll_view = ScrollView(
            size_hint=(1, 1),
            bar_width=dp(10),
            bar_color=(0.2, 0.6, 1, 1)
        )
        self.scroll_content = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(15),
            padding=dp(10)
        )
        self.scroll_content.bind(minimum_height=self.scroll_content.setter('height'))
        self.scroll_view.add_widget(self.scroll_content)
        self.layout.add_widget(self.scroll_view)

        # Add question cards
        self.question_cards = []
        for question in self.questions:
            card = self.create_question_card(question)
            self.scroll_content.add_widget(card)
            self.question_cards.append(card)

        # Bottom buttons
        self.add_bottom_buttons()

    def create_question_card(self, question):
        """Create a properly sized card for each question"""
        card = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            spacing=dp(10),
            padding=dp(15)
        )
        
        # Calculate minimum height based on content
        min_height = dp(150)  # Base height for buttons and padding
        
        # Question text
        question_label = Label(
            text=question['question'],
            size_hint=(1, None),
            font_size='18sp',
            bold=True,
            color=(0, 0, 0, 1),
            text_size=(Window.width - dp(40), None),
            halign='left',
            valign='top'
        )
        question_label.bind(
            texture_size=lambda lbl, val: setattr(lbl, 'height', val[1] + dp(10)))
        card.add_widget(question_label)
        min_height += question_label.height
        
        # Options text
        options_text = "Options: " + ", ".join(question['options'])
        options_label = Label(
            text=options_text,
            size_hint=(1, None),
            font_size='16sp',
            color=(0.4, 0.4, 0.4, 1),
            text_size=(Window.width - dp(40), None),
            halign='left'
        )
        options_label.bind(
            texture_size=lambda lbl, val: setattr(lbl, 'height', val[1] + dp(10)))
        card.add_widget(options_label)
        min_height += options_label.height
        
        # Buttons
        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(50),
            spacing=dp(10))
        
        edit_button = Button(
            text="EDIT",
            size_hint=(0.5, None),
            height=dp(45),
            background_color=(0.2, 0.8, 0.2, 1),
            color=(1, 1, 1, 1),
            font_size='16sp'
        )
        edit_button.bind(on_press=lambda instance, q=question: self.edit_question(q))
        
        delete_button = Button(
            text="DELETE",
            size_hint=(0.5, None),
            height=dp(45),
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            font_size='16sp'
        )
        delete_button.bind(on_press=lambda instance, q=question: self.delete_question(q))
        
        button_layout.add_widget(edit_button)
        button_layout.add_widget(delete_button)
        card.add_widget(button_layout)
        
        # Set minimum height
        card.height = min_height
        
        # Card styling
        with card.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # Light gray background
            self.rect = RoundedRectangle(
                size=card.size,
                pos=card.pos,
                radius=[dp(15)]
            )
        card.bind(
            size=self._update_card_rect,
            pos=self._update_card_rect
        )
        
        return card

    def add_bottom_buttons(self):
        """Add the bottom action buttons"""
        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(60),
            spacing=dp(10),
            padding=dp(10)
        )
        
        add_button = Button(
            text="ADD NEW QUESTION",
            background_color=(0.2, 0.6, 1, 1),
            color=(1, 1, 1, 1),
            font_size='16sp'
        )
        add_button.bind(on_press=self.add_question)
        
        back_button = Button(
            text="BACK TO MAIN",
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            font_size='16sp'
        )
        back_button.bind(on_press=self.switch_to_main)
        
        button_layout.add_widget(add_button)
        button_layout.add_widget(back_button)
        self.layout.add_widget(button_layout)

    def _update_card_rect(self, instance, value):
        """Update the card's background rectangle"""
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            RoundedRectangle(
                size=instance.size,
                pos=instance.pos,
                radius=[dp(15)]
            )

    def edit_question(self, question):
        self.manager.current = "edit_question"
        self.manager.get_screen("edit_question").load_question(question)
        self.refresh_data(None)

    def delete_question(self, question):
        # Confirmation popup before deletion
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(
            text=f"Delete this question?\n\n{question['question']}",
            halign='center',
            text_size=(Window.width * 0.7, None)))
        
        btn_box = BoxLayout(size_hint=(1, 0.3), spacing=10)
        yes_btn = Button(text="Delete", background_color=(0.8, 0.2, 0.2, 1))
        no_btn = Button(text="Cancel", background_color=(0.4, 0.4, 0.4, 1))
        
        btn_box.add_widget(no_btn)
        btn_box.add_widget(yes_btn)
        content.add_widget(btn_box)
        
        popup = Popup(
            title="Confirm Deletion",
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False)
        
        no_btn.bind(on_press=popup.dismiss)
        yes_btn.bind(on_press=lambda x: self._confirm_delete(question, popup))
        popup.open()

    def _confirm_delete(self, question, popup):
        self.questions.remove(question)
        if update_github_file(App.get_running_app().access_token, self.questions):
            self.show_popup("Success", "Question deleted successfully!")
            self.refresh_data(None)
        else:
            self.show_popup("Error", "Failed to update on GitHub")
        popup.dismiss()

    def add_question(self, instance):
        self.manager.current = "add_question"

    def switch_to_main(self, instance):
        main_screen = self.manager.get_screen("main")
        if (main_screen):
            main_screen.refresh_data(None)
        self.manager.current = "main"

    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text=message))
        ok_btn = Button(text="OK", size_hint=(1, 0.4))
        popup = Popup(title=title, content=content, size_hint=(0.7, 0.4))
        ok_btn.bind(on_press=popup.dismiss)
        content.add_widget(ok_btn)
        popup.open()

    def refresh_data(self, instance=None):
        """Refresh the UI by fetching the latest questions and rebuilding the UI."""
        Clock.schedule_once(self._refresh_ui, 0.1)  # Schedule after 0.1 seconds

    def _refresh_ui(self, dt):
        """Internal method to refresh the UI."""
        self.fetch_questions()
        self.create_ui()

    def start_progress_animation(self):
        """Start the progress bar animation."""
        self.progress_bar.value = 0
        self.animation_event = Clock.schedule_interval(self.update_progress, 0.1)  # Update every 0.1 seconds

    def stop_progress_animation(self):
        """Stop the progress bar animation."""
        if self.animation_event:
            self.animation_event.cancel()
            self.animation_event = None

    def update_progress(self, dt):
        """Update the progress bar value."""
        if self.progress_bar.value < self.progress_bar.max:
            self.progress_bar.value += 1  # Increment progress
        else:
            self.stop_progress_animation()  # Stop when progress reaches 100%
class AddQuestionScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.create_ui()
        self.add_widget(self.layout)

        Window.bind(on_keyboard=self.on_keyboard)
        Window.bind(on_keyboard_height=self.on_keyboard_height)
        Window.keyboard_anim_args={'d':.2,'t':'in_out_expo'}


    def create_ui(self):
        self.layout.clear_widgets()

        # Heading
        heading = Label(
            text="Add New Question",
            size_hint_y=None,
            height=dp(50),
            font_size='24sp',
            bold=True,
            color=(0.2, 0.6, 1, 1)  # Blue color
        )
        self.layout.add_widget(heading)

        # Question Input
        self.question_input = TextInput(
            hint_text="Enter question",
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            padding=[10, 0],
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1)
        )
        self.layout.add_widget(self.question_input)

        # Options Input
        self.options_input = TextInput(
            hint_text="Enter options (comma-separated)",
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            padding=[10, 0],
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1)
        )
        self.layout.add_widget(self.options_input)

        # Answer Input
        self.answer_input = TextInput(
            hint_text="Enter correct answers (comma-separated)",
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            padding=[10, 0],
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1)
        )
        self.layout.add_widget(self.answer_input)

        # Reference Input
        self.reference_input = TextInput(
            hint_text="Enter reference URL",
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            padding=[10, 0],
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1)
        )
        self.layout.add_widget(self.reference_input)

        # Add Question Button
        add_button = Button(
            text="Add Question",
            size_hint_y=None,
            height=dp(50),
            background_color=(0.2, 0.6, 1, 1),
            color=(1, 1, 1, 1)
        )
        add_button.bind(on_press=self.add_question)
        self.layout.add_widget(add_button)

        # Back to Admin Button
        back_button = Button(
            text="Back to Admin",
            size_hint_y=None,
            height=dp(50),
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        back_button.bind(on_press=self.switch_to_admin)
        self.layout.add_widget(back_button)

    def on_keyboard(self, window, key, *args):
        if key == 27:  # Escape key
            return True
        return False

    def on_keyboard_height(self, window, height):
        if height > 0:
            self.layout.height = Window.height - height
        else:
            self.layout.height = Window.height

    def add_question(self, instance):
        question = self.question_input.text.strip()
        options = [opt.strip() for opt in self.options_input.text.split(",")]
        answers = [ans.strip() for ans in self.answer_input.text.split(",")]
        reference = self.reference_input.text.strip()

        if not question or not options or not answers:
            self.show_popup("Error", "Please fill in all fields.")
            return

        new_question = {
            "id": str(uuid.uuid4()),
            "question": question,
            "options": options,
            "answers": answers,
            "reference": reference
        }

        admin_screen = self.manager.get_screen("admin")
        admin_screen.questions.append(new_question)

        if update_github_file(App.get_running_app().access_token, admin_screen.questions):
            self.show_popup("Success", "Question added and file updated on GitHub.")
            admin_screen.refresh_data(None)
            self.manager.current = "admin"
        else:
            self.show_popup("Error", "Failed to update file on GitHub.")

    def switch_to_admin(self, instance):
        self.manager.current = "admin"

    def show_popup(self, title, message):
        popup = Popup(title=title, size_hint=(0.8, 0.4))
        popup.content = Label(text=message)
        popup.open()
class EditQuestionScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.create_ui()
        self.add_widget(self.layout)

        Window.bind(on_keyboard=self.on_keyboard)
        Window.bind(on_keyboard_height=self.on_keyboard_height)
        Window.keyboard_anim_args={'d':.2,'t':'in_out_expo'}


    def create_ui(self):
        self.layout.clear_widgets()

        # Heading
        heading = Label(
            text="Edit Question",
            size_hint_y=None,
            height=dp(50),
            font_size='24sp',
            bold=True,
            color=(0.2, 0.6, 1, 1)  # Blue color
        )
        self.layout.add_widget(heading)

        # Question Input
        self.question_input = TextInput(
            hint_text="Enter question",
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            padding=[10, 0],
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1)
        )
        self.layout.add_widget(self.question_input)

        # Options Input
        self.options_input = TextInput(
            hint_text="Enter options (comma-separated)",
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            padding=[10, 0],
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1)
        )
        self.layout.add_widget(self.options_input)

        # Answer Input
        self.answer_input = TextInput(
            hint_text="Enter correct answers (comma-separated)",
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            padding=[10, 0],
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1)
        )
        self.layout.add_widget(self.answer_input)

        # Reference Input
        self.reference_input = TextInput(
            hint_text="Enter reference URL",
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            padding=[10, 0],
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1)
        )
        self.layout.add_widget(self.reference_input)

        # Save Changes Button
        save_button = Button(
            text="Save Changes",
            size_hint_y=None,
            height=dp(50),
            background_color=(0.2, 0.6, 1, 1),
            color=(1, 1, 1, 1)
        )
        save_button.bind(on_press=self.save_question)
        self.layout.add_widget(save_button)

        # Back to Admin Button
        back_button = Button(
            text="Back to Admin",
            size_hint_y=None,
            height=dp(50),
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        back_button.bind(on_press=self.switch_to_admin)
        self.layout.add_widget(back_button)

    def on_keyboard(self, window, key, *args):
        if key == 27:  # Escape key
            return True
        return False

    def on_keyboard_height(self, window, height):
        if height > 0:
            self.layout.height = Window.height - height
        else:
            self.layout.height = Window.height

    def load_question(self, question):
        self.question = question
        self.question_input.text = question['question']
        self.options_input.text = ", ".join(question['options'])
        self.answer_input.text = ", ".join(question['answers'])
        self.reference_input.text = question['reference']

    def save_question(self, instance):
        # Update the question data
        self.question['question'] = self.question_input.text.strip()
        self.question['options'] = [opt.strip() for opt in self.options_input.text.split(",")]
        self.question['answers'] = [ans.strip() for ans in self.answer_input.text.split(",")]
        self.question['reference'] = self.reference_input.text.strip()

        # Get the AdminScreen instance
        admin_screen = self.manager.get_screen("admin")

        # Update the questions list in AdminScreen
        for i, q in enumerate(admin_screen.questions):
            if q['id'] == self.question['id']:
                admin_screen.questions[i] = self.question
                break

        # Update the file on GitHub
        if update_github_file(App.get_running_app().access_token, admin_screen.questions):
            self.show_popup("Success", "Question updated and file updated on GitHub.")
            admin_screen.refresh_data(None)  # Refresh the AdminScreen UI
            self.manager.current = "admin"
        else:
            self.show_popup("Error", "Failed to update file on GitHub.")

    def switch_to_admin(self, instance):
        self.manager.current = "admin"

    def show_popup(self, title, message):
        popup = Popup(title=title, size_hint=(0.8, 0.4))
        popup.content = Label(text=message)
        popup.open()
class MainApp(App):
    def build(self):
        self.screen_manager = ScreenManager()
        self.access_token = load_access_token()
        self.questions = []
        self.selected_answers = {}

        if self.access_token:
            self.main_screen = MainScreen(name="main")
            self.screen_manager.add_widget(self.main_screen)

            self.admin_screen = AdminScreen(name="admin")
            self.login_screen = LoginScreen(name="login")
            self.add_question_screen = AddQuestionScreen(name="add_question")
            self.edit_question_screen = EditQuestionScreen(name="edit_question")
            self.screen_manager.add_widget(self.admin_screen)
            self.screen_manager.add_widget(self.login_screen)
            self.screen_manager.add_widget(self.add_question_screen)
            self.screen_manager.add_widget(self.edit_question_screen)
        else:
            self.registration_screen = RegistrationScreen(name="registration")
            self.screen_manager.add_widget(self.registration_screen)

        Window.bind(on_keyboard=self.on_keyboard)
        Window.bind(on_keyboard_height=self.on_keyboard_height)
        Window.keyboard_anim_args={'d':.2,'t':'in_out_expo'}


        return self.screen_manager

    def refresh_all_screens(self):
        for screen_name in self.screen_manager.screen_names:
            screen = self.screen_manager.get_screen(screen_name)
            if hasattr(screen, 'refresh_data'):
                screen.refresh_data(None)

    def on_keyboard(self, window, key, *args):
        pass

    def on_keyboard_height(self, window, height):
        current_screen = self.screen_manager.current_screen
        if height > 0:
            if isinstance(current_screen, MainScreen) or isinstance(current_screen, RegistrationScreen):
                current_screen.scroll_view.height = Window.height - height - dp(150)
                current_screen.anchor_layout.y = height
            else:
                current_screen.scroll_view.height = Window.height - height
                current_screen.anchor_layout.y = height
        else:
            current_screen.scroll_view.height = Window.height
            current_screen.anchor_layout.y = 0

if __name__ == '__main__':
    main_app = MainApp()
    main_app.run()
