import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.spinner import Spinner
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.metrics import dp

kivy.require('2.0.0')

DIGIT_MAP = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+/"

class RoundButton(Button):
    """
    Modern round button with custom styling
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)  # Transparent
        self.bind(pos=self.update_graphics, size=self.update_graphics)
        self.bind(state=self.update_graphics)
        
    def update_graphics(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # Modern button colors
            if self.state == 'down':
                Color(0.2, 0.6, 0.9, 1)  # Blue when pressed
            else:
                Color(0.3, 0.7, 1.0, 1)  # Light blue normal state
            
            # Calculate the size to make it circular
            size = min(self.width, self.height) * 0.8
            pos_x = self.center_x - size / 2
            pos_y = self.center_y - size / 2
            
            # Draw rounded rectangle (circular appearance)
            Ellipse(pos=(pos_x, pos_y), size=(size, size))

class BaseInput(TextInput):
    """
    Accepts only valid characters for any base (2–64),
    and maps input characters to DIGIT_MAP.
    """
    def __init__(self, base=10, **kwargs):
        super().__init__(**kwargs)
        self.base = base

    def insert_text(self, substring, from_undo=False):
        filtered = []
        for c in substring:
            if '0' <= c <= '9':
                idx = ord(c) - ord('0')
            elif 'A' <= c <= 'Z':
                idx = ord(c) - ord('A') + 10
            elif 'a' <= c <= 'z':
                idx = ord(c) - ord('a') + 36
            elif c == '+' and self.base > 62:
                idx = 62
            elif c == '/' and self.base > 63:
                idx = 63
            else:
                continue

            if idx < self.base:
                filtered.append(DIGIT_MAP[idx])

        return super().insert_text(''.join(filtered), from_undo=from_undo)

class MultiBaseCalculatorApp(App):
    def build(self):
        self.title = "Base-2 to 64 Calculator"

        root = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        root.canvas.before.clear()
        with root.canvas.before:
            Color(0.1, 0.1, 0.15, 1)  # Modern dark background
            Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self.update_bg, size=self.update_bg)

        # Base selection spinner: 2–64
        self.spinner = Spinner(
            text='10',
            values=[str(i) for i in range(2, 65)],
            size_hint=(1, 0.15),
            font_size=dp(20),
            background_color=(0.2, 0.2, 0.3, 1)
        )
        self.spinner.bind(text=self.on_base_change)

        # Input fields with modern styling
        self.entry1 = BaseInput(base=10,
                                hint_text='Input 1 (base 10)',
                                multiline=False,
                                font_size=dp(18),
                                background_color=(0.2, 0.2, 0.3, 1),
                                foreground_color=(1, 1, 1, 1),
                                size_hint=(1, 0.12))
        self.entry2 = BaseInput(base=10,
                                hint_text='Input 2 (base 10)',
                                multiline=False,
                                font_size=dp(18),
                                background_color=(0.2, 0.2, 0.3, 1),
                                foreground_color=(1, 1, 1, 1),
                                size_hint=(1, 0.12))

        # Operation buttons grid with round buttons
        ops = [
            ('+', 'add'), ('−', 'subtract'),
            ('×', 'multiply'), ('÷', 'divide'),
            ('AND', 'and'), ('OR', 'or'),
            ('XOR', 'xor'), ('C', 'clear')
        ]
        ops_layout = GridLayout(cols=4, spacing=dp(10), size_hint=(1, 0.4))
        for label, op in ops:
            btn = RoundButton(text=label, font_size=dp(16), color=(1, 1, 1, 1))
            btn.bind(on_press=lambda inst, o=op: self.on_button(o))
            ops_layout.add_widget(btn)

        # Result label with modern styling
        self.result_label = Label(text='Result:', 
                                 font_size=dp(18), 
                                 size_hint=(1, 0.2),
                                 color=(1, 1, 1, 1),
                                 text_size=(None, None),
                                 halign='center')

        # Assemble UI
        root.add_widget(self.spinner)
        root.add_widget(self.entry1)
        root.add_widget(self.entry2)
        root.add_widget(ops_layout)
        root.add_widget(self.result_label)

        return root
    
    def update_bg(self, instance, value):
        """Update background when size/position changes"""
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(0.1, 0.1, 0.15, 1)
            Rectangle(pos=instance.pos, size=instance.size)

    def on_base_change(self, spinner, value):
        base = int(value)
        hint = f'Input (base {base})'
        for entry in (self.entry1, self.entry2):
            entry.base = base
            entry.text = ''
            entry.hint_text = hint
        self.result_label.text = 'Result:'

    def convert_to_decimal(self, s):
        """Convert from selected base (2–64) to decimal."""
        s = s.strip()
        if not s:
            raise ValueError("Input is empty.")
        base = int(self.spinner.text)

        n = 0
        for c in s:
            idx = DIGIT_MAP.find(c)
            if idx < 0 or idx >= base:
                raise ValueError(f"'{c}' is invalid for base {base}.")
            n = n * base + idx
        return n

    def convert_from_decimal(self, n):
        """Convert decimal to selected base (2–64)."""
        base = int(self.spinner.text)
        sign = '-' if n < 0 else ''
        n = abs(n)

        if n == 0:
            return '0'

        digits = []
        while n > 0:
            idx = n % base
            digits.append(DIGIT_MAP[idx])
            n //= base
        return sign + ''.join(reversed(digits))

    def on_button(self, operation):
        if operation == 'clear':
            self.entry1.text = ''
            self.entry2.text = ''
            self.result_label.text = 'Result:'
            return

        try:
            a = self.convert_to_decimal(self.entry1.text)
            b = self.convert_to_decimal(self.entry2.text)

            if operation == 'add':
                r = a + b
            elif operation == 'subtract':
                r = a - b
            elif operation == 'multiply':
                r = a * b
            elif operation == 'divide':
                if b == 0:
                    raise ZeroDivisionError("Cannot divide by zero.")
                r = a // b
            elif operation == 'and':
                r = a & b
            elif operation == 'or':
                r = a | b
            elif operation == 'xor':
                r = a ^ b
            else:
                raise ValueError("Unknown operation.")

            out_base = self.convert_from_decimal(r)
            out_decimal = str(r)
            base = self.spinner.text
            self.result_label.text = (
                f"Result (base {base}): {out_base}\n"
                f"Result (decimal): {out_decimal}"
            )

        except ZeroDivisionError as zde:
            self.show_error(str(zde))
        except ValueError as ve:
            self.show_error(str(ve))

    def show_error(self, msg):
        popup = Popup(
            title='Error',
            content=Label(text=msg),
            size_hint=(0.6, 0.4)
        )
        popup.open()

if __name__ == '__main__':
    MultiBaseCalculatorApp().run()