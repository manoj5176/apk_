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
# GitHub API details


GITHUB_TOKEN1 = "Z2l0aHViX3BhdF8xMUJBUFY1RkEwaWJFa0NnTFIwQkEyX1BaVUZzeXhiNTFFTWxLYjAzYnA4bDJLSnlQQXZmVVk2cnVDeGYwVHNDRHlLWVJHUjRTVlg4cUxmUDBX"
CREDENTIALS_REPO = "manoj5176/app_credentials"  # Private repository
CREDENTIALS_FILE = "admin.json"
CREDENTIALS_FILE1 = "admin_credentials.json"
BRANCH = "main"

# GitHub API to fetch credentials
def fetch_admin_credentials():
    GITHUB_TOKEN= base64.b64decode(GITHUB_TOKEN1.encode("utf-8")).decode("utf-8")

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
    ADMIN_CREDENTIALS = fetch_admin_credentials()
except Exception as e:
    print(f"Error fetching admin credentials: {e}")
    ADMIN_CREDENTIALS = {"username": "admin", "password": "admin123"}  # Fallback credentials

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.create_ui()
        self.add_widget(self.layout)
    def create_ui(self):
        self.layout.clear_widgets()

        # Add a logo at the top
        with self.layout.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # Light gray background
            self.rect = Rectangle(size=self.layout.size, pos=self.layout.pos)
        self.layout.bind(size=self._update_rect, pos=self._update_rect)

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
        self.password_input = TextInput(
            hint_text="Employee Id",
            multiline=False,
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

        # Footer
        footer = Label(
            text="© APP Version 1.0.1",
            size_hint_y=None,
            height=dp(30),
            font_size='12sp',
            color=(0.4, 0.4, 0.4, 1)  # Gray color
        )
        self.layout.add_widget(footer)

    def _update_rect(self, instance, value):
        """Update the size and position of the background rectangle."""
        self.rect.size = instance.size
        self.rect.pos = instance.pos

    def backtomain(self,instance):
        self.manager.current='main'
    

    




    def authenticate(self, instance):
        username = self.username_input.text
        password = self.password_input.text

        if username == ADMIN_CREDENTIALS["username"] and password == ADMIN_CREDENTIALS["password"]:
            self.show_popup("Success", "Login successful!")
            self.manager.current = "admin"
            
        else:
            self.show_popup("Error", "Invalid username or password")
            self.manager.current='main'

    def show_popup(self, title, message):
        popup = Popup(title=title, size_hint=(0.8, 0.4))
        popup.content = Label(text=message)
        self.refresh_data(None)
        popup.open()

    def switch_to_login(self, instance):
        self.manager.current = "login"

    def refresh_data(self, instance):
        # Schedule the UI update using Clock
        Clock.schedule_once(self._refresh_ui, 0.1)  # Schedule after 0.1 seconds

    def _refresh_ui(self, dt):
        """Internal method to refresh the UI."""
       
        self.create_ui()





# GitHub API to fetch questions
def fetch_questions():
    GITHUB_TOKEN= base64.b64decode(GITHUB_TOKEN1.encode("utf-8")).decode("utf-8")
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
def update_github_file(questions):
    GITHUB_TOKEN= base64.b64decode(GITHUB_TOKEN1.encode("utf-8")).decode("utf-8")
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

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_answers = {} 
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.fetch_questions()
        self.create_ui()
        self.add_widget(self.layout)

    def fetch_questions(self):
        try:
            self.questions = fetch_questions()
        except Exception as e:
            print(f"Error fetching questions: {e}")
            self.questions = []



    def create_ui(self):
        self.layout.clear_widgets()

        # Set background color for the entire screen
        with self.layout.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # Light gray background
            self.rect = Rectangle(size=self.layout.size, pos=self.layout.pos)
        self.layout.bind(size=self._update_rect, pos=self._update_rect)

        # Create a ScrollView for questions
        scroll_view = ScrollView(
            size_hint=(1, 0.8),  # Take up remaining space
            do_scroll_x=False,  # Disable horizontal scrolling
            do_scroll_y=True    # Enable vertical scrolling
        )
        scroll_content = BoxLayout(
            orientation='vertical',
            spacing=10,
            padding=10,
            size_hint_y=None
        )
        scroll_content.bind(minimum_height=scroll_content.setter('height'))

        for question in self.questions:
            # Create a card for each question
            question_card = BoxLayout(
                orientation='vertical',
                spacing=10,
                padding=10,
                size_hint_y=None,
                #height=dp(300)  # Increased height to accommodate content
            )
            with question_card.canvas.before:
                Color(1, 1, 1, 1)  # White background for the card
                self.card_rect = RoundedRectangle(size=question_card.size, pos=question_card.pos, radius=[dp(10)])
            question_card.bind(size=self._update_card_rect, pos=self._update_card_rect)

            # Question text
            question_label = Label(
                text=question['question'],
                size_hint_y=None,
                #height=dp(50),  # Increased height for question text
                font_size='18sp',
                bold=True,
                color=(0, 0, 0, 1),  # Black color
                halign='center',
                valign='middle'
            )
            question_label.bind(
                width=lambda *x: question_label.setter('text_size')(question_label, (question_label.width, None))
            )
            question_card.add_widget(question_label)

            # Add options with checkboxes
            for option in question['options']:
                option_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=dp(40))
                checkbox = CheckBox(size_hint_x=None, width=dp(30), color=[0, 0, 1])
                checkbox.bind(active=lambda instance, value, qid=question['id'], opt=option: self.on_checkbox_active(qid, opt, value))
                option_label = Label(
                    text=option,
                    size_hint_x=None,
                    width=dp(200),
                    halign='left',
                    valign='middle',
                    padding=[dp(10), 0],
                    font_size='16sp',
                    color=(0, 0, 0, 1)  # Black text
                )
                option_label.bind(
                    width=lambda *x: option_label.setter('text_size')(option_label, (option_label.width, None)))
                option_layout.add_widget(checkbox)
                option_layout.add_widget(option_label)
                question_card.add_widget(option_layout)
                            # Calculate total height of the card
            total_height = question_label.height + len(question['options']) * dp(40) + dp(20)  # Add padding
            question_card.height = total_height

            scroll_content.add_widget(question_card)

        scroll_view.add_widget(scroll_content)
        self.layout.add_widget(scroll_view)

        # Add Submit and Admin Login buttons
        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=10,
            padding=10
        )
        submit_button = Button(
            text="Submit",
            background_color=(0.2, 0.6, 1, 1),  # Blue color
            color=(1, 1, 1, 1),  # White text
            size_hint_y=None,
            height=dp(50)
        )
        submit_button.bind(on_press=self.show_results)
        admin_button = Button(
            text="Admin Login",
            background_color=(0.8, 0.2, 0.2, 1),  # Red color
            color=(1, 1, 1, 1),  # White text
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
            height=dp(50),
            font_size='24sp',
            bold=True,
            color=(0.2, 0.6, 1, 1)  # Blue color
        )
        self.layout.add_widget(title_label)

    def _update_rect(self, instance, value):
        """Update the size and position of the background rectangle."""
        self.rect.size = instance.size
        self.rect.pos = instance.pos

    def _update_card_rect(self, instance, value):
        """Update the size and position of the card's rounded rectangle."""
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(1, 1, 1, 1)  # White background for the card
            RoundedRectangle(size=instance.size, pos=instance.pos, radius=[dp(10)])

    def update_card_height(self, card, label):
        """Update the height of the card based on the label's texture size."""
        if label.texture_size[1] > dp(100):  # If text wraps and requires more height
            card.height += label.texture_size[1] - dp(100)  # Adjust card height
    def on_checkbox_active(self, question_id, option, value):
        if question_id not in self.user_answers:
            self.user_answers[question_id] = []
        if value:  # Checkbox is checked
            self.user_answers[question_id].append(option)
        else:  # Checkbox is unchecked
            self.user_answers[question_id].remove(option)

    def show_results(self, instance):
        correct_count = 0
        results = []

        for question in self.questions:
            question_id = question['id']
            user_answers = self.user_answers.get(question_id, [])
            correct_answers = question['answers']
            is_correct = set(user_answers) == set(correct_answers)  # Compare sets for multiple answers

            if is_correct:
                correct_count += 1

            results.append({
                "question": question['question'],
                "user_answers": user_answers,
                "correct_answers": correct_answers,
                "is_correct": is_correct,
                "reference": question['reference']
            })

        result_text = f"Correct Answers: {correct_count}/{len(self.questions)}\n\n"
        for result in results:
            result_text += (
                f"Question: {result['question']}\n"
                f"Your Answers: {', '.join(result['user_answers'])}\n"
                f"Correct Answers: {', '.join(result['correct_answers'])}\n"
                f"Reference: {result['reference']}\n\n"
            )
        
        popup = Popup(title='Results', size_hint=(0.8, 0.8))
        popup.content = Label(text=result_text, size_hint=(1, 1))
        popup.open()
        self.refresh_data(None)
        self.user_answers.clear()
        #self.manager.current = "main"

    def refresh_data(self, instance):
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


class AdminScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.fetch_questions()
        self.create_ui()
        self.add_widget(self.layout)

        

    def fetch_questions(self):
        try:
            self.questions = fetch_questions()
        except Exception as e:
            print(f"Error fetching questions: {e}")
            self.questions = []

    def create_ui(self):
        self.layout.clear_widgets()

        # Set background color for the entire screen
        with self.layout.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # Light gray background
            self.rect = Rectangle(size=self.layout.size, pos=self.layout.pos)
        self.layout.bind(size=self._update_rect, pos=self._update_rect)

        # Add a heading
        heading = Label(
            text="Admin Panel",
            size_hint_y=None,
            height=50,
            font_size='24sp',
            bold=True,
            color=(0.2, 0.6, 1, 1)  # Blue color
        )
        self.layout.add_widget(heading)

        # Create a ScrollView
        scroll_view = ScrollView(size_hint=(1, 0.8))
        scroll_content = BoxLayout(orientation='vertical', spacing=10, padding=10, size_hint_y=None)
        scroll_content.bind(minimum_height=scroll_content.setter('height'))

        for question in self.questions:
            # Create a card for each question
            question_card = BoxLayout(orientation='vertical', spacing=10, padding=10, size_hint_y=None, height=150)
            with question_card.canvas.before:
                Color(1, 1, 1, 1)  # White background for the card
                RoundedRectangle(size=question_card.size, pos=question_card.pos, radius=[dp(10)])
            question_card.bind(size=self._update_card_rect, pos=self._update_card_rect)

            question_label = Label(
                text=question['question'],
                size_hint_y=None,
                height=40,
                font_size='18sp',
                bold=True,
                color=(0, 0, 0, 1)  # Black color
            )
            question_card.add_widget(question_label)

            # Display options
            options_label = Label(
                text="Options: " + ", ".join(question['options']),
                size_hint_y=None,
                height=30,
                font_size='14sp',
                color=(0.4, 0.4, 0.4, 1)  # Gray color
            )
            question_card.add_widget(options_label)

            # Add Edit and Delete buttons
            button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10, padding=10)
            edit_button = Button(
                text="Edit",
                size_hint_x=None,
                width=100,
                background_color=(0.2, 0.8, 0.2, 1),  # Green color
                color=(1, 1, 1, 1)  # White text
            )
            edit_button.bind(on_press=lambda instance, q=question: self.edit_question(q))
            delete_button = Button(
                text="Delete",
                size_hint_x=None,
                width=100,
                background_color=(0.8, 0.2, 0.2, 1),  # Red color
                color=(1, 1, 1, 1)  # White text
            )
            delete_button.bind(on_press=lambda instance, q=question: self.delete_question(q))
            button_layout.add_widget(edit_button)
            button_layout.add_widget(delete_button)
            question_card.add_widget(button_layout)

            scroll_content.add_widget(question_card)

        scroll_view.add_widget(scroll_content)
        self.layout.add_widget(scroll_view)

        # Add Add New Question and Back to Main buttons
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10, padding=10)
        add_button = Button(
            text="Add New Question",
            background_color=(0.2, 0.6, 1, 1),  # Blue color
            color=(1, 1, 1, 1),  # White text
            size_hint_y=None,
            height=50
        )
        add_button.bind(on_press=self.add_question)
        back_button = Button(
            text="Back to Main",
            background_color=(0.8, 0.2, 0.2, 1),  # Red color
            color=(1, 1, 1, 1),  # White text
            size_hint_y=None,
            height=50
        )
        back_button.bind(on_press=self.switch_to_main)
        button_layout.add_widget(add_button)
        button_layout.add_widget(back_button)
        self.layout.add_widget(button_layout)

    def _update_rect(self, instance, value):
        """Update the size and position of the background rectangle."""
        self.rect.size = instance.size
        self.rect.pos = instance.pos

    def _update_card_rect(self, instance, value):
        """Update the size and position of the card's rounded rectangle."""
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(1, 1, 1, 1)  # White background for the card
            RoundedRectangle(size=instance.size, pos=instance.pos, radius=[dp(10)])
    def edit_question(self, question):
        self.manager.current = "edit_question"
        self.manager.get_screen("edit_question").load_question(question)
        self.refresh_data(None)

    def delete_question(self, question):
        self.questions.remove(question)
        if update_github_file(self.questions):
            self.show_popup("Success", "Question deleted and file updated on GitHub.")
            #self.create_ui()  # Refresh the UI
            self.refresh_data(None)
            
        else:
            self.show_popup("Error", "Failed to update file on GitHub.")

    

    def add_question(self, instance):
        self.manager.current = "add_question"
        

    def switch_to_main(self, instance):
        if self.manager is None:
            print("Error: self.manager is None")
            return
        main_screen = self.manager.get_screen("main")
        if main_screen is None:
            print("Error: 'main' screen not found")
            return
        main_screen.refresh_data(None)
        self.manager.current = "main"

    def show_popup(self, title, message):
        popup = Popup(title=title, size_hint=(0.8, 0.4))
        popup.content = Label(text=message, size_hint=(1, 1))
        popup.open()

    def refresh_data(self, instance):
        """Refresh the UI by fetching the latest questions and rebuilding the UI."""
        # Schedule the UI update using Clock
        Clock.schedule_once(self._refresh_ui, 0.1)  # Schedule after 0.1 seconds

    def _refresh_ui(self, dt):
        """Internal method to refresh the UI."""
        self.fetch_questions()
        self.create_ui()

class AddQuestionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        self.question_input = TextInput(hint_text="Enter question", multiline=False)
        self.options_input = TextInput(hint_text="Enter options (comma-separated)", multiline=False)
        self.answer_input = TextInput(hint_text="Enter correct answers (comma-separated)", multiline=False)
        self.reference_input = TextInput(hint_text="Enter reference URL", multiline=False)

        self.add_button = Button(text="Add Question", size_hint_y=None, height=50)
        self.add_button.bind(on_press=self.add_question)

        self.back_button = Button(text="Back to Admin", size_hint_y=None, height=50)
        self.back_button.bind(on_press=self.switch_to_admin)

        self.layout.add_widget(self.question_input)
        self.layout.add_widget(self.options_input)
        self.layout.add_widget(self.answer_input)
        self.layout.add_widget(self.reference_input)
        self.layout.add_widget(self.add_button)
        self.layout.add_widget(self.back_button)

        self.add_widget(self.layout)

    def add_question(self, instance):
        question = self.question_input.text
        options = self.options_input.text.split(",")
        answers = self.answer_input.text.split(",")
        reference = self.reference_input.text

        new_question = {
            #"id": len(self.manager.get_screen("admin").questions) + 1,
            "id": str(uuid.uuid4()),
            "question": question,
            "options": options,
            "answers": answers,  # Multiple correct answers
            "reference": reference
        }

        self.manager.get_screen("admin").questions.append(new_question)
        if update_github_file(self.manager.get_screen("admin").questions):
            self.show_popup("Success", "Question added and file updated on GitHub.")
            main_screen = self.manager.get_screen("admin")
            main_screen.refresh_data(None)
            self.manager.current = "admin"
            
        else:
            self.show_popup("Error", "Failed to update file on GitHub.")

    def switch_to_admin(self, instance):
        if self.manager is None:
            print("Error: self.manager is None")
            return
        main_screen = self.manager.get_screen("admin")
        if main_screen is None:
            print("Error: 'main' screen not found")
            return
        main_screen.refresh_data(None)
        self.manager.current = "admin"


    def show_popup(self, title, message):
        popup = Popup(title=title, size_hint=(0.8, 0.4))
        popup.content = Label(text=message)
        popup.open()



class EditQuestionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        self.question_input = TextInput(hint_text="Enter question", multiline=False)
        self.options_input = TextInput(hint_text="Enter options (comma-separated)", multiline=False)
        self.answer_input = TextInput(hint_text="Enter correct answers (comma-separated)", multiline=False)
        self.reference_input = TextInput(hint_text="Enter reference URL", multiline=False)

        self.save_button = Button(text="Save Changes", size_hint_y=None, height=50)
        self.save_button.bind(on_press=self.save_question)

        self.back_button = Button(text="Back to Admin", size_hint_y=None, height=50)
        self.back_button.bind(on_press=self.switch_to_admin)

        self.layout.add_widget(self.question_input)
        self.layout.add_widget(self.options_input)
        self.layout.add_widget(self.answer_input)
        self.layout.add_widget(self.reference_input)
        self.layout.add_widget(self.save_button)
        self.layout.add_widget(self.back_button)

        self.add_widget(self.layout)

    def load_question(self, question):
        self.question = question
        self.question_input.text = question['question']
        self.options_input.text = ",".join(question['options'])
        self.answer_input.text = ",".join(question['answers'])
        self.reference_input.text = question['reference']

    def save_question(self, instance):
        self.question['question'] = self.question_input.text
        self.question['options'] = self.options_input.text.split(",")
        self.question['answers'] = self.answer_input.text.split(",")
        self.question['reference'] = self.reference_input.text

        if update_github_file(self.manager.get_screen("admin").questions):
            self.show_popup("Success", "Question updated and file updated on GitHub.")
        else:
            self.show_popup("Error", "Failed to update file on GitHub.")

    def switch_to_admin(self, instance):
        if self.manager is None:
            print("Error: self.manager is None")
            return
        main_screen = self.manager.get_screen("admin")
        if main_screen is None:
            print("Error: 'main' screen not found")
            return
        main_screen.refresh_data(None)
        self.manager.current = "admin"


    def show_popup(self, title, message):
        popup = Popup(title=title, size_hint=(0.8, 0.4))
        popup.content = Label(text=message)
        popup.open()

class QuestionnaireApp(App):
    def build(self):
        self.screen_manager = ScreenManager()
        self.questions = []
        self.selected_answers = {}

        self.main_screen = MainScreen(name="main")
        self.admin_screen = AdminScreen(name="admin")
        self.login_screen = LoginScreen(name="login")
        self.add_question_screen = AddQuestionScreen(name="add_question")
        self.edit_question_screen = EditQuestionScreen(name="edit_question")

        self.screen_manager.add_widget(self.main_screen)
        self.screen_manager.add_widget(self.admin_screen)
        self.screen_manager.add_widget(self.login_screen)
        self.screen_manager.add_widget(self.add_question_screen)
        self.screen_manager.add_widget(self.edit_question_screen)

      

        return self.screen_manager

if __name__ == '__main__':
    main_app = QuestionnaireApp()
    main_app.run()
