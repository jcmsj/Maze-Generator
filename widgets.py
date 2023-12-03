import pygame
import sys
from typing import Callable
from typing import TypeVar

T = TypeVar("T")
class Val[T]:
    def __init__(self, val:T, observers=None):
        self._val:T = val
        self.observers:list[Callable[[T], None]] = observers if observers is not None else []

    def __repr__(self):
        return f"Val({self._val})"

    def __str__(self):
        return str(self._val)

    def __eq__(self, other):
        return self._val == other.value

    def __hash__(self):
        return hash(self._val)
    def set(self, val:T):
        self._val = val
        for observer in self.observers:
            observer(self._val)

    @property
    def value(self) -> T:
        return self._val
    
class BoolVal(Val[bool]):
    def toggle(self):
        self.set(not self._val)
    def to_true(self):
        self.set(True)
    def to_false(self):
        self.set(False)

    def __bool__(self):
        """
        assuming you have:\n
        v = BoolVal(False)\n
        when we do:\n
        if v:
            <some code>
        intereter will call this method and return self._val.\n
        So in the above code, the inner block won't be called.
        """
        return self._val
    
class TextField:
    def __init__(self, screen, text:str,location: tuple[int,int], font:pygame.font.Font, color:tuple[int,int,int], background_color:tuple[int,int,int], onSubmit: Callable[[str], None|bool] | None = None  ):
        """
        Represents a text field on the screen.

        Args:
            screen: The pygame screen surface.
            text: The initial text of the field.
            x: The x-coordinate of the field.
            y: The y-coordinate of the field.
            font: The font used for rendering the text.
            color: The color of the text.
            background_color: The background color of the field.
            onSubmit: A callback function that is called when the text is submitted. The callback should accepts a string paremeter and can return None or a boolean value. If it returns True, the text will not be updated.
        """
        self.screen = screen
        self.text = text
        self.location = location
        self.font = font
        self.color = color
        self.background_color = background_color
        self.field = self.font.render(self.text, True, self.color, self.background_color)
        self.textRect = self.field.get_rect()
        self.textRect.center = location
        self.focused = False
        self.onSubmit = onSubmit
        self.previous_text = self.text

    def draw(self):
        """
        Draws the text field on the screen.
        """
        self.screen.blit(self.field, self.textRect)

    def update(self, text:str):
        """
        Updates the text of the field.

        Args:
            text: The new text for the field.
        """

        self.text = text
        self.field = self.font.render(self.text, True, self.color, self.background_color)
        self.textRect = self.field.get_rect()
        self.textRect.center = self.location

    def listen(self, event:pygame.event.Event):
        """
        Listens for events and updates the field accordingly.

        Args:
            event: The pygame event to handle.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.focused = self.textRect.collidepoint(event.pos)
            if self.focused:
                self.previous_text = self.text
                print("TextField: Onfocused")

        if self.focused and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                print("TextField: OnUnfocused")
                self.focused = False
                self.update(self.previous_text)
            if event.key == pygame.K_RETURN:
                print("TextField: onSubmit")
                self.focused = False
                if self.onSubmit is not None:
                    should_reject = self.onSubmit(self.text)
                    if should_reject:
                        self.update(self.previous_text)
            if event.key == pygame.K_BACKSPACE:
                self.update(self.text[:-1])
            elif event.unicode.isalnum():
                self.update(self.text + event.unicode)

class Text:
    def __init__(
        self,
        label: str,
        screen: pygame.Surface,
        font: pygame.font.Font,
        center: tuple[int,int],
        color: tuple[int,int,int],
        background: tuple[int,int,int],
        anti_aliasing: bool = True,
    ):
        """
        Represents a text on the screen.

        Args:
            label: The label of the text.
            rect: The rectangle of the text.
            color: The color of the text.
            hover_color: The color of the text when hovered.
            onclick: The callback function that is called when the text is clicked.
            screen: The pygame screen surface.
        """
        self.anti_aliasing = anti_aliasing
        self.label = font.render(label, self.anti_aliasing, color, background)
        self._label = label
        self.rect = self.label.get_rect()
        self.rect.center = center
        self.color = color
        self.screen = screen

    def draw(self) -> None:
        """
        Draws the text on the screen.

        Args:
            screen: The pygame screen surface.
        """
        self.screen.blit(self.label, self.rect)
 
class Button:
    # accept a Text
    def __init__(self,onclick:Callable[[], None], text:Text ):
        self.text = text
        self.onclick = onclick

    def draw(self):
        self.text.draw()

    def listen(self, event:pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONUP:
            if self.text.rect.collidepoint(event.pos):
                print(f"Btn[{self.text._label}]: onClick")
                self.onclick()

class RadioButton:
    
    def __init__(self, assigned, text, x, y, checked =False, onclick = None):
        self.assigned = assigned
        self.text = text
        self.checked = checked
        self.onclick = onclick
        self.font = pygame.font.Font(None, 24)
        self.label = self.font.render(self.text, 1, (255,255,255))
        self.rect = pygame.Rect(x, y, 12, 12)
        self.text_rect = pygame.Rect(x + 20, y, self.label.get_width(), self.label.get_height())
    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 0 if self.checked else 1)
        screen.blit(self.label, (self.rect.x + 20, self.rect.y))
    def listen(self, event:pygame.event.Event):
        if self.onclick == None:
            return
        
        if event.type == pygame.MOUSEBUTTONUP:
            if self.rect.collidepoint(event.pos) or self.text_rect.collidepoint(event.pos):
                print("onClick")
                self.onclick()
                    
