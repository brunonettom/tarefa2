import pygame
import sys
import random
import time
import math
import os
import csv
from collections import defaultdict

# Initialize pygame
pygame.init()

# Get display info
display_info = pygame.display.Info()
MAX_SCREEN_WIDTH = display_info.current_w
MAX_SCREEN_HEIGHT = display_info.current_h
DEFAULT_WIDTH = min(1024, MAX_SCREEN_WIDTH - 100)  # Default windowed mode size
DEFAULT_HEIGHT = min(768, MAX_SCREEN_HEIGHT - 100)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (100, 100, 255)
GREEN = (100, 200, 100)
RED = (255, 100, 100)

# Font settings
FONT_LARGE = pygame.font.Font(None, 48)
FONT_MEDIUM = pygame.font.Font(None, 36)
FONT_SMALL = pygame.font.Font(None, 28)
FONT_TINY = pygame.font.Font(None, 22)

# Create resizable window
screen = pygame.display.set_mode((DEFAULT_WIDTH, DEFAULT_HEIGHT), pygame.RESIZABLE)
SCREEN_WIDTH = DEFAULT_WIDTH
SCREEN_HEIGHT = DEFAULT_HEIGHT

pygame.display.set_caption("Aprendizagem de Gramática Artificial (AGL)")

# Track fullscreen state
is_fullscreen = False

# Fix the toggle_fullscreen function to properly handle DEFAULT_WIDTH/HEIGHT
def toggle_fullscreen():
    global screen, SCREEN_WIDTH, SCREEN_HEIGHT, is_fullscreen, DEFAULT_WIDTH, DEFAULT_HEIGHT
    is_fullscreen = not is_fullscreen
    
    if is_fullscreen:
        # Save window size before going fullscreen
        if SCREEN_WIDTH != MAX_SCREEN_WIDTH:
            DEFAULT_WIDTH = SCREEN_WIDTH
        if SCREEN_HEIGHT != MAX_SCREEN_HEIGHT:
            DEFAULT_HEIGHT = SCREEN_HEIGHT
        
        # Switch to fullscreen
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        SCREEN_WIDTH = MAX_SCREEN_WIDTH
        SCREEN_HEIGHT = MAX_SCREEN_HEIGHT
    else:
        # Return to windowed mode with previous size
        screen = pygame.display.set_mode((DEFAULT_WIDTH, DEFAULT_HEIGHT), pygame.RESIZABLE)
        SCREEN_WIDTH = DEFAULT_WIDTH
        SCREEN_HEIGHT = DEFAULT_HEIGHT

# Input field class for configuration
class InputField:
    def __init__(self, x, y, width, height, text="", label="", value=0, min_value=0, max_value=100):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.label = label
        self.value = value
        self.min_value = min_value
        self.max_value = max_value
        self.active = False
        self.color_inactive = GRAY
        self.color_active = BLUE
        self.color = self.color_inactive
        self.input_text = str(value)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Toggle active state
            self.active = self.rect.collidepoint(event.pos)
            self.color = self.color_active if self.active else self.color_inactive
            
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    # Apply the value when Enter is pressed
                    try:
                        new_value = int(self.input_text)
                        self.value = max(self.min_value, min(self.max_value, new_value))
                        self.input_text = str(self.value)
                    except ValueError:
                        # If conversion fails, revert to current value
                        self.input_text = str(self.value)
                    self.active = False
                    self.color = self.color_inactive
                    
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                    
                elif event.unicode.isdigit():
                    self.input_text += event.unicode
                    
    def draw(self, surface):
        # Draw label centered above the input field
        if len(self.label) > 30 and SCREEN_WIDTH < 1200:
            label_surface = FONT_SMALL.render(self.label, True, BLACK)
        else:
            label_surface = FONT_MEDIUM.render(self.label, True, BLACK)
        
        # Center the label above the input field
        label_x = self.rect.centerx - label_surface.get_width() // 2
        label_y = self.rect.top - label_surface.get_height() - 5
        surface.blit(label_surface, (label_x, label_y))
        
        # Draw input box
        pygame.draw.rect(surface, WHITE, self.rect)  # Fill with white
        pygame.draw.rect(surface, self.color, self.rect, 2)
        
        # Center the text in the input box
        text_surface = FONT_MEDIUM.render(self.input_text, True, BLACK)
        text_x = self.rect.centerx - text_surface.get_width() // 2
        text_y = self.rect.centery - text_surface.get_height() // 2
        surface.blit(text_surface, (text_x, text_y))
        
        # Draw min-max info centered vertically
        min_max_text = f"({self.min_value}-{self.max_value})"
        min_max_surface = FONT_SMALL.render(min_max_text, True, GRAY)
        min_max_x = self.rect.right + 10
        min_max_y = self.rect.centery - min_max_surface.get_height() // 2
        surface.blit(min_max_surface, (min_max_x, min_max_y))

# Configuration class for experiment parameters
class ExperimentConfig:
    def __init__(self):
        # Default parameters
        self.min_sequence_length = 3
        self.max_sequence_length = 8
        self.training_count = 15
        self.test_count_grammatical = 10
        self.test_count_nongrammatical = 10
        self.min_edits = 1
        self.max_edits = 2
        
        # UI elements for configuration
        self.input_fields = {}
        self.buttons = {}
        
        # Create UI elements
        self.create_ui_elements()
    
    def create_ui_elements(self):
        # Setup a centered layout with a box border
        box_width = int(SCREEN_WIDTH * 0.8)  # 80% of screen width
        box_height = int(SCREEN_HEIGHT * 0.7)  # 70% of screen height
        box_x = (SCREEN_WIDTH - box_width) // 2
        box_y = 120
        self.box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        
        # Input fields - adjust based on screen size
        field_width = min(120, SCREEN_WIDTH // 10)
        field_height = 40
        
        # Calculate column positions for a two-column layout
        left_col_x = box_x + box_width // 4 
        right_col_x = box_x + box_width * 3 // 4
        
        # Vertical spacing based on box height
        v_start = box_y + 60
        v_spacing = (box_height - 120) // 4
        
        # Left column of input fields
        self.input_fields["min_length"] = InputField(
            left_col_x - field_width // 2, v_start, 
            field_width, field_height, 
            label="Comprimento Mínimo da Sequência",
            value=self.min_sequence_length, min_value=2, max_value=6
        )
        
        self.input_fields["max_length"] = InputField(
            left_col_x - field_width // 2, v_start + v_spacing, 
            field_width, field_height, 
            label="Comprimento Máximo da Sequência",
            value=self.max_sequence_length, min_value=4, max_value=12
        )
        
        self.input_fields["training_count"] = InputField(
            left_col_x - field_width // 2, v_start + v_spacing*2, 
            field_width, field_height, 
            label="Número de Itens de Treinamento",
            value=self.training_count, min_value=5, max_value=30
        )
        
        self.input_fields["min_edits"] = InputField(
            left_col_x - field_width // 2, v_start + v_spacing*3, 
            field_width, field_height, 
            label="Distância de Edição Mínima",
            value=self.min_edits, min_value=1, max_value=3
        )
        
        # Right column of input fields
        self.input_fields["test_count_gram"] = InputField(
            right_col_x - field_width // 2, v_start,
            field_width, field_height, 
            label="Itens de Teste (gramaticais)",
            value=self.test_count_grammatical, min_value=5, max_value=20
        )
        
        self.input_fields["test_count_nongram"] = InputField(
            right_col_x - field_width // 2, v_start + v_spacing, 
            field_width, field_height, 
            label="Itens de Teste (não gramaticais)",
            value=self.test_count_nongrammatical, min_value=5, max_value=20
        )
        
        self.input_fields["max_edits"] = InputField(
            right_col_x - field_width // 2, v_start + v_spacing*2, 
            field_width, field_height, 
            label="Distância de Edição Máxima",
            value=self.max_edits, min_value=1, max_value=4
        )
        
        # Start button centered at bottom of screen
        button_y = box_y + box_height + 50
        self.buttons["start"] = Button(SCREEN_WIDTH//2 - 100, button_y, 
                                      200, 50, "Iniciar Experimento")
    
    def handle_events(self):
        """Handle events for configuration screen"""
        global SCREEN_WIDTH, SCREEN_HEIGHT, screen, is_fullscreen
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_F11:  # Toggle fullscreen with F11 key
                    toggle_fullscreen()
                    # Recreate UI elements for new screen size
                    self.create_ui_elements()
                    
            if event.type == pygame.VIDEORESIZE:
                # Handle window resize
                if not is_fullscreen:
                    SCREEN_WIDTH, SCREEN_HEIGHT = event.size
                    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                    # Recreate UI elements for new screen size
                    self.create_ui_elements()
                    
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check start button click directly here
                if self.buttons["start"].rect.collidepoint(event.pos):
                    print("Start button clicked!")  # Debug output
                    self._update_parameters_from_inputs()
                    return True  # Signal that config is complete
                
                # Pass the event to input fields as well
                mouse_click = True
        
        # Handle input fields after checking buttons
        if mouse_click:
            for field in self.input_fields.values():
                field.handle_event(event)  # This will cause an error - event undefined
        
        # Update buttons hover state
        for button in self.buttons.values():
            button.update(mouse_pos)
            
        return False  # Config not complete
    
    def _update_parameters_from_inputs(self):
        """Update configuration parameters from input fields"""
        # Update parameters from input fields
        self.min_sequence_length = self.input_fields["min_length"].value
        self.max_sequence_length = self.input_fields["max_length"].value
        self.training_count = self.input_fields["training_count"].value
        self.test_count_grammatical = self.input_fields["test_count_gram"].value
        self.test_count_nongrammatical = self.input_fields["test_count_nongram"].value
        self.min_edits = self.input_fields["min_edits"].value
        self.max_edits = self.input_fields["max_edits"].value
        
        # Validate values to ensure min <= max
        if self.min_sequence_length > self.max_sequence_length:
            self.min_sequence_length = self.max_sequence_length - 1
        
        if self.min_edits > self.max_edits:
            self.min_edits = self.max_edits
    
    def draw(self, screen):
        """Draw the configuration screen"""
        # Draw title
        title = FONT_LARGE.render("Configuração do Experimento AGL", True, BLUE)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        # Draw explanation text
        explanation = FONT_SMALL.render("Ajuste os parâmetros do experimento abaixo:", True, BLACK)
        screen.blit(explanation, (SCREEN_WIDTH//2 - explanation.get_width()//2, 100))
        
        # Draw border box
        pygame.draw.rect(screen, BLUE, self.box_rect, 2, border_radius=5)
        
        # Draw each input field
        for field in self.input_fields.values():
            field.draw(screen)
        
        # Draw start button
        self.buttons["start"].draw(screen)
        
        # Draw note about default values
        note = FONT_SMALL.render("Os valores padrão são baseados na literatura de AGL.", True, GRAY)
        note_y = self.buttons["start"].rect.top - 40
        screen.blit(note, (SCREEN_WIDTH//2 - note.get_width()//2, note_y))
        
        # Draw help text for fullscreen
        help_text = FONT_TINY.render("Pressione F11 para alternar entre tela cheia e janela", True, GRAY)
        screen.blit(help_text, (SCREEN_WIDTH - help_text.get_width() - 10, 10))

# Finite-state grammar for generating sequences
# Using a simple grammar with states 0-4 and transitions labeled with letters
class FiniteStateGrammar:
    def __init__(self):
        # Define states and transitions
        self.transitions = {
            0: [('X', 1), ('V', 3)],
            1: [('P', 1), ('T', 2)],
            2: [('V', 3), ('X', 5)],
            3: [('T', 2), ('S', 4)],
            4: [('P', 3), ('X', 5)],
            5: []  # Terminal state
        }
        self.start_state = 0
        self.end_states = [5]
    
    def generate_sequence(self, min_length=3, max_length=8):
        """Generate a grammatical sequence with specified length constraints"""
        current_state = self.start_state
        sequence = []
        
        # First try: generate a standard sequence following the grammar
        while current_state not in self.end_states and len(sequence) < max_length:
            if not self.transitions[current_state]:  # No transitions available
                break
                
            # Choose a random transition from current state
            symbol, next_state = random.choice(self.transitions[current_state])
            sequence.append(symbol)
            current_state = next_state
        
        # If sequence is too short, continue it when possible or restart
        if len(sequence) < min_length:
            # Try extending it if not at a terminal state
            if current_state not in self.end_states and self.transitions[current_state]:
                # Continue from current state until min length or terminal state
                return self.generate_sequence(min_length, max_length)
            else:
                # If we can't extend, we might need to try a different path
                return self.generate_sequence(min_length, max_length)
            
        return ''.join(sequence)
    
    def generate_non_grammatical(self, grammatical_sequences, min_edits=1, max_edits=2):
        """Generate non-grammatical sequences by modifying grammatical ones
        with controlled edit distance and preserving similar chunk strength"""
        base = random.choice(grammatical_sequences)
        edits = random.randint(min_edits, min(max_edits, len(base)))
        
        # Possible letters
        letters = ['X', 'P', 'T', 'V', 'S']
        
        # Copy the base sequence
        new_seq = list(base)
        
        # Get bi/trigrams from original sequence for chunk strength comparison
        original_bigrams = self._get_ngrams(base, 2)
        original_trigrams = self._get_ngrams(base, 3)
        
        # Try multiple times to generate a sequence with appropriate properties
        attempts = 0
        max_attempts = 10
        
        while attempts < max_attempts:
            # Create a working copy for this attempt
            attempt_seq = new_seq.copy()
            
            # Apply random edits
            for _ in range(edits):
                edit_type = random.choice(['replace', 'insert', 'delete'])
                
                if edit_type == 'replace' and len(attempt_seq) > 0:
                    pos = random.randint(0, len(attempt_seq) - 1)
                    new_letter = random.choice([l for l in letters if l != attempt_seq[pos]])
                    attempt_seq[pos] = new_letter
                    
                elif edit_type == 'insert' and len(attempt_seq) < 10:
                    pos = random.randint(0, len(attempt_seq))
                    attempt_seq.insert(pos, random.choice(letters))
                    
                elif edit_type == 'delete' and len(attempt_seq) > 2:
                    pos = random.randint(0, len(attempt_seq) - 1)
                    attempt_seq.pop(pos)
            
            candidate = ''.join(attempt_seq)
            
            # Verify this is actually non-grammatical
            if not self.is_grammatical(candidate):
                # Check chunk strength similarity
                candidate_bigrams = self._get_ngrams(candidate, 2)
                candidate_trigrams = self._get_ngrams(candidate, 3)
                
                # Calculate bigram/trigram similarity (simple overlap measure)
                bigram_overlap = len(set(original_bigrams) & set(candidate_bigrams)) / max(1, len(set(original_bigrams)))
                trigram_overlap = len(set(original_trigrams) & set(candidate_trigrams)) / max(1, len(set(original_trigrams)))
                
                # We want some overlap but not too much
                # Accept if intermediate chunk strength similarity
                if 0.2 <= bigram_overlap <= 0.6 and 0.1 <= trigram_overlap <= 0.5:
                    return candidate
            
            attempts += 1
        
        # If all attempts fail, return the last attempt (better than nothing)
        return ''.join(attempt_seq)
    
    def _get_ngrams(self, sequence, n):
        """Extract n-grams from a sequence"""
        return [sequence[i:i+n] for i in range(len(sequence) - n + 1)]
    
    def is_grammatical(self, sequence):
        """Check if a sequence follows the grammar rules"""
        current_state = self.start_state
        
        for symbol in sequence:
            valid_transitions = [(s, next_state) for (s, next_state) in self.transitions[current_state] if s == symbol]
            
            if not valid_transitions:
                return False
                
            # Take the first valid transition
            _, current_state = valid_transitions[0]
        
        return current_state in self.end_states or any(self.transitions[current_state])

# Button class for UI interaction
class Button:
    def __init__(self, x, y, width, height, text, color=BLUE, hover_color=None, text_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color or (color[0]-30, color[1]-30, color[2]-30)
        self.text_color = text_color
        self.is_hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=5)  # Border
        
        # Adjust font size if text is too large for button
        font_size = 36
        custom_font = pygame.font.Font(None, font_size)
        text_surf = custom_font.render(self.text, True, self.text_color)
        
        # If text is too wide, reduce font size
        while text_surf.get_width() > self.rect.width - 20 and font_size > 18:
            font_size -= 2
            custom_font = pygame.font.Font(None, font_size)
            text_surf = custom_font.render(self.text, True, self.text_color)
        
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    # Simplified is_clicked method that we won't use directly
    def is_clicked(self, mouse_pos, mouse_click):
        return self.is_hovered and mouse_click

# AGL Experiment class
class AGLExperiment:
    def __init__(self, config=None):
        self.grammar = FiniteStateGrammar()
        self.state = "config" if config is None else "instructions"
        self.config = config or ExperimentConfig()
        self.training_sequences = []
        self.test_sequences = []
        self.test_answers = []
        self.current_sequence_idx = 0
        self.confidence_ratings = []
        self.display_time = 0
        self.start_time = 0
        self.reaction_times = []
        
        # UI elements
        self.buttons = {}
        
        # Results
        self.results = {
            'hits': 0,
            'misses': 0,
            'false_alarms': 0,
            'correct_rejections': 0,
            'dprime': 0,
            'accuracy': 0,
            'mean_confidence': 0,
            'mean_rt': 0,
        }
        
        # Only generate stimuli and create buttons after configuration is done
        if self.state == "instructions":
            # Generate training sequences
            self.generate_stimuli()
            # Create buttons
            self.create_buttons()
    
    def create_buttons(self):
        # Calculate button positions based on screen dimensions
        bottom_margin = min(100, SCREEN_HEIGHT // 8)
        
        # Start button for instructions screen - position it further from text
        button_y = SCREEN_HEIGHT - bottom_margin - 50
        self.buttons["start"] = Button(SCREEN_WIDTH//2 - 100, button_y, 
                                      200, 50, "Começar")
                                      
        # Training navigation
        self.buttons["next"] = Button(SCREEN_WIDTH - 150, button_y, 
                                     120, 50, "Próximo")
                                     
        # Test response buttons - ensure separation
        button_width = min(220, SCREEN_WIDTH // 4)
        button_spacing = min(80, SCREEN_WIDTH // 10)
        
        # Position the buttons lower on the screen with plenty of space
        response_button_y = button_y - 100  # 100px above the bottom buttons
        
        self.buttons["grammatical"] = Button(SCREEN_WIDTH//2 - button_width - button_spacing//2, 
                                           response_button_y, 
                                           button_width, 60, "Gramatical")
        
        self.buttons["non_grammatical"] = Button(SCREEN_WIDTH//2 + button_spacing//2, 
                                               response_button_y, 
                                               button_width, 60, "Não Gramatical")
                                               
        # Confidence rating buttons - improved spacing calculation
        conf_button_width = min(60, SCREEN_WIDTH // 12)
        total_buttons_width = conf_button_width * 5
        total_spacing = SCREEN_WIDTH // 2  # Use half screen width for all buttons
        
        # Calculate gap between buttons
        conf_spacing = (total_spacing - total_buttons_width) // 5
        
        # Position first button
        start_x = (SCREEN_WIDTH - total_spacing) // 2
        
        for i in range(1, 6):
            x_pos = start_x + (i-1) * (conf_button_width + conf_spacing)
            self.buttons[f"conf_{i}"] = Button(x_pos, button_y, 
                                             conf_button_width, 60, str(i))
                                             
        # Final button
        self.buttons["finish"] = Button(SCREEN_WIDTH//2 - 100, button_y, 
                                       200, 50, "Finalizar")
    
    def generate_stimuli(self):
        # Generate grammatical sequences for training
        self.training_sequences = []
        
        # Ensure we get enough unique training sequences
        attempts = 0
        max_attempts = 100
        
        while len(self.training_sequences) < self.config.training_count and attempts < max_attempts:
            seq = self.grammar.generate_sequence(
                min_length=self.config.min_sequence_length, 
                max_length=self.config.max_sequence_length
            )
            if seq not in self.training_sequences:
                self.training_sequences.append(seq)
            attempts += 1
            
        # If we couldn't generate enough unique sequences, fill with duplicates
        while len(self.training_sequences) < self.config.training_count:
            self.training_sequences.append(random.choice(self.training_sequences))
        
        # Generate test sequences:
        # New grammatical sequences
        test_grammatical = []
        attempts = 0
        
        while len(test_grammatical) < self.config.test_count_grammatical and attempts < max_attempts:
            seq = self.grammar.generate_sequence(
                min_length=self.config.min_sequence_length, 
                max_length=self.config.max_sequence_length
            )
            if seq not in self.training_sequences and seq not in test_grammatical:
                test_grammatical.append(seq)
            attempts += 1
            
        # If we couldn't generate enough unique sequences, relax the constraint of not being in training
        while len(test_grammatical) < self.config.test_count_grammatical:
            seq = self.grammar.generate_sequence(
                min_length=self.config.min_sequence_length, 
                max_length=self.config.max_sequence_length
            )
            if seq not in test_grammatical:
                test_grammatical.append(seq)
        
        # Non-grammatical sequences
        test_non_grammatical = []
        attempts = 0
        
        while len(test_non_grammatical) < self.config.test_count_nongrammatical and attempts < max_attempts:
            seq = self.grammar.generate_non_grammatical(
                self.training_sequences,
                min_edits=self.config.min_edits,
                max_edits=self.config.max_edits
            )
            if not self.grammar.is_grammatical(seq) and seq not in test_non_grammatical:
                test_non_grammatical.append(seq)
            attempts += 1
            
        # If we couldn't generate enough unique non-grammatical sequences, try again with relaxed constraints
        while len(test_non_grammatical) < self.config.test_count_nongrammatical:
            seq = ''.join(random.choice(['X', 'P', 'T', 'V', 'S']) for _ in range(
                random.randint(self.config.min_sequence_length, self.config.max_sequence_length)))
            if not self.grammar.is_grammatical(seq) and seq not in test_non_grammatical:
                test_non_grammatical.append(seq)
        
        # Combine and shuffle test sequences
        self.test_sequences = [(seq, True) for seq in test_grammatical] + [(seq, False) for seq in test_non_grammatical]
        random.shuffle(self.test_sequences)
    
    def calculate_results(self):
        # Calculate hits, misses, false alarms, and correct rejections
        for i, (_, is_grammatical) in enumerate(self.test_sequences):
            user_response = self.test_answers[i]
            
            if is_grammatical and user_response:  # Hit
                self.results['hits'] += 1
            elif is_grammatical and not user_response:  # Miss
                self.results['misses'] += 1
            elif not is_grammatical and user_response:  # False alarm
                self.results['false_alarms'] += 1
            elif not is_grammatical and not user_response:  # Correct rejection
                self.results['correct_rejections'] += 1
        
        # Calculate d-prime (sensitivity index)
        # Using standard formulas from signal detection theory
        hit_rate = self.results['hits'] / (self.results['hits'] + self.results['misses'])
        if hit_rate == 1: hit_rate = 0.99  # Adjust perfect scores
        if hit_rate == 0: hit_rate = 0.01
            
        fa_rate = self.results['false_alarms'] / (self.results['false_alarms'] + self.results['correct_rejections'])
        if fa_rate == 1: fa_rate = 0.99
        if fa_rate == 0: fa_rate = 0.01
            
        self.results['dprime'] = self._calculate_dprime(hit_rate, fa_rate)
        self.results['criterion'] = self._calculate_criterion(hit_rate, fa_rate)
        self.results['hit_rate'] = hit_rate
        self.results['fa_rate'] = fa_rate
        
        # Calculate accuracy
        total_trials = len(self.test_sequences)
        correct_responses = self.results['hits'] + self.results['correct_rejections']
        self.results['accuracy'] = correct_responses / total_trials
        
        # Calculate mean confidence rating
        if self.confidence_ratings:
            self.results['mean_confidence'] = sum(self.confidence_ratings) / len(self.confidence_ratings)
            
            # Analyze confidence for hits vs. misses (implicit vs explicit knowledge)
            hit_confidences = []
            miss_confidences = []
            fa_confidences = []
            cr_confidences = []
            
            for i, ((_, is_grammatical), user_response) in enumerate(zip(self.test_sequences, self.test_answers)):
                conf = self.confidence_ratings[i]
                
                if is_grammatical and user_response:  # Hit
                    hit_confidences.append(conf)
                elif is_grammatical and not user_response:  # Miss
                    miss_confidences.append(conf)
                elif not is_grammatical and user_response:  # False alarm
                    fa_confidences.append(conf)
                elif not is_grammatical and not user_response:  # Correct rejection
                    cr_confidences.append(conf)
            
            # Save mean confidence by response type
            self.results['hit_confidence'] = sum(hit_confidences) / max(1, len(hit_confidences))
            self.results['miss_confidence'] = sum(miss_confidences) / max(1, len(miss_confidences))
            self.results['fa_confidence'] = sum(fa_confidences) / max(1, len(fa_confidences))
            self.results['cr_confidence'] = sum(cr_confidences) / max(1, len(cr_confidences))
            
            # Calculate low confidence correct responses (potential implicit knowledge)
            low_conf_correct = sum(1 for i, ((_, is_grammatical), user_response) in 
                                enumerate(zip(self.test_sequences, self.test_answers))
                                if ((is_grammatical and user_response) or 
                                   (not is_grammatical and not user_response)) and
                                   self.confidence_ratings[i] <= 2)
                                   
            self.results['low_conf_correct'] = low_conf_correct
            self.results['low_conf_accuracy'] = low_conf_correct / total_trials
        
        # Calculate mean reaction time
        if self.reaction_times:
            self.results['mean_rt'] = sum(self.reaction_times) / len(self.reaction_times)
    
    def _calculate_dprime(self, hit_rate, fa_rate):
        """Calculate d-prime sensitivity index"""
        z_hit = self._norm_inv_cdf(hit_rate)
        z_fa = self._norm_inv_cdf(fa_rate)
        return z_hit - z_fa
    
    def _calculate_criterion(self, hit_rate, fa_rate):
        """Calculate criterion (response bias)"""
        z_hit = self._norm_inv_cdf(hit_rate)
        z_fa = self._norm_inv_cdf(fa_rate)
        return -(z_hit + z_fa) / 2
    
    def _norm_inv_cdf(self, p):
        """Approximation of the inverse cumulative distribution function for standard normal"""
        # Simple approximation
        if p < 0.5:
            t = math.sqrt(-2.0 * math.log(p))
            return -((0.010328 * t + 0.802853) * t + 2.515517) / ((0.001308 * t + 0.189269) * t + 1.0)
        else:
            t = math.sqrt(-2.0 * math.log(1.0 - p))
            return ((0.010328 * t + 0.802853) * t + 2.515517) / ((0.001308 * t + 0.189269) * t + 1.0)
    
    def handle_events(self):
        global SCREEN_WIDTH, SCREEN_HEIGHT, screen
        
        # Handle configuration state separately
        if self.state == "config":
            # Let config handle its events
            config_complete = self.config.handle_events()
            if config_complete:
                print("Moving to instructions state")  # Debug output
                # Move to instructions state
                self.state = "instructions"
                # Generate stimuli and create buttons with new configuration
                self.generate_stimuli()
                self.create_buttons()
            return
        
        # For all other states, handle button clicks
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        
        # Process events for non-config states
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_F11:
                    toggle_fullscreen()
                    self.create_buttons()
                    
            if event.type == pygame.VIDEORESIZE:
                if not is_fullscreen:
                    SCREEN_WIDTH, SCREEN_HEIGHT = event.size
                    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                    self.create_buttons()
                    
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True
                # Direct button click checking for each state
                if self.state == "instructions" and self.buttons["start"].rect.collidepoint(event.pos):
                    self.state = "training"
                    self.current_sequence_idx = 0
                    self.display_time = pygame.time.get_ticks()
                    return
                    
                elif self.state == "training" and self.buttons["next"].rect.collidepoint(event.pos):
                    self.current_sequence_idx += 1
                    if self.current_sequence_idx >= len(self.training_sequences):
                        self.state = "test_instructions"
                    self.display_time = pygame.time.get_ticks()
                    return
                    
                elif self.state == "test_instructions" and self.buttons["start"].rect.collidepoint(event.pos):
                    self.state = "testing"
                    self.current_sequence_idx = 0
                    self.start_time = pygame.time.get_ticks()
                    return
                    
                elif self.state == "testing":
                    if len(self.test_answers) == self.current_sequence_idx:
                        if self.buttons["grammatical"].rect.collidepoint(event.pos):
                            rt = (pygame.time.get_ticks() - self.start_time) / 1000.0
                            self.reaction_times.append(rt)
                            self.test_answers.append(True)
                            self.state = "confidence"
                            return
                        elif self.buttons["non_grammatical"].rect.collidepoint(event.pos):
                            rt = (pygame.time.get_ticks() - self.start_time) / 1000.0
                            self.reaction_times.append(rt)
                            self.test_answers.append(False)
                            self.state = "confidence"
                            return
                            
                elif self.state == "confidence":
                    for i in range(1, 6):
                        if self.buttons[f"conf_{i}"].rect.collidepoint(event.pos):
                            self.confidence_ratings.append(i)
                            if self.current_sequence_idx < len(self.test_sequences) - 1:
                                self.current_sequence_idx += 1
                                self.state = "testing"
                                self.start_time = pygame.time.get_ticks()
                            else:
                                self.state = "results"
                                self.calculate_results()
                            return
                            
                elif self.state == "results" and self.buttons["finish"].rect.collidepoint(event.pos):
                    self.save_results()
                    pygame.quit()
                    sys.exit()
                    
        # Update button hover states
        for button in self.buttons.values():
            button.update(mouse_pos)

    def draw(self):
        """Draw the current state of the experiment"""
        screen.fill(WHITE)
        
        if self.state == "config":
            # Draw configuration screen
            self.config.draw(screen)
        
        elif self.state == "instructions":
            self.draw_instructions()
            self.buttons["start"].draw(screen)
        
        elif self.state == "training":
            self.draw_training()
            self.buttons["next"].draw(screen)
        
        elif self.state == "test_instructions":
            self.draw_test_instructions()
            self.buttons["start"].draw(screen)
        
        elif self.state == "testing":
            self.draw_testing()
            self.buttons["grammatical"].draw(screen)
            self.buttons["non_grammatical"].draw(screen)
        
        elif self.state == "confidence":
            self.draw_confidence()
            for i in range(1, 6):
                self.buttons[f"conf_{i}"].draw(screen)
        
        elif self.state == "results":
            self.draw_results()
            self.buttons["finish"].draw(screen)
        
        # Draw fullscreen help in all screens
        if self.state != "config":  # Already drawn in config screen
            help_text = FONT_TINY.render("F11: Alternar tela cheia", True, GRAY)
            screen.blit(help_text, (SCREEN_WIDTH - help_text.get_width() - 10, 10))
            
        pygame.display.flip()
    
    def draw_instructions(self):
        """Draw instructions screen"""
        # Draw title
        title = FONT_LARGE.render("Aprendizagem de Gramática Artificial", True, BLACK)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        # Calculate safe area for instructions text to avoid button overlap
        bottom_limit = self.buttons["start"].rect.top - 60  # Space above button
        
        # Draw instructions - adjust for screen size
        instructions = [
            "Neste experimento, você verá sequências de letras.",
            "As sequências são geradas seguindo regras específicas, formando uma 'gramática artificial'.",
            "Sua tarefa será memorizar estas sequências na fase de treino.",
            "Depois, você julgará novas sequências como 'gramaticais' (seguem as regras) ou",
            "'não gramaticais' (violam as regras), e indicará seu nível de confiança.",
            "",
            "Nenhuma instrução sobre as regras será dada.",
            "Tente identificar os padrões ocultos nas sequências durante o treinamento!"
        ]
        
        # Adjust font size and line spacing based on available space
        font_to_use = FONT_MEDIUM
        line_spacing = 40
        
        # Calculate total height needed and available space
        total_height = len(instructions) * line_spacing
        available_height = bottom_limit - 150  # From y=150 to bottom_limit
        
        # If not enough space, use smaller font
        if total_height > available_height:
            font_to_use = FONT_SMALL
            line_spacing = 30
        
        # If still not enough space, use tiny font
        if len(instructions) * line_spacing > available_height:
            font_to_use = FONT_TINY
            line_spacing = 20
    
        # Start closer to top if needed
        y_pos = 150
        if y_pos + total_height > bottom_limit:
            y_pos = max(100, bottom_limit - total_height)
    
        # Render text, ensuring it's centered
        for line in instructions:
            instr_text = font_to_use.render(line, True, BLACK)
            text_x = SCREEN_WIDTH//2 - instr_text.get_width()//2
            screen.blit(instr_text, (text_x, y_pos))
            y_pos += line_spacing
    
        # Only draw the note if there's room, and center it
        if y_pos + 30 < bottom_limit:
            note = FONT_SMALL.render("Este experimento investiga como as pessoas adquirem conhecimento implícito.", True, GRAY)
            screen.blit(note, (SCREEN_WIDTH//2 - note.get_width()//2, y_pos))
    
    def draw_training(self):
        """Draw training screen"""
        # Draw phase title
        title = FONT_LARGE.render("Fase de Treinamento", True, BLUE)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        # Draw instruction
        instr = FONT_MEDIUM.render("Memorize esta sequência:", True, BLACK)
        screen.blit(instr, (SCREEN_WIDTH//2 - instr.get_width()//2, 120))
        
        # Draw sequence - center it
        sequence = self.training_sequences[self.current_sequence_idx]
        seq_text = FONT_LARGE.render(sequence, True, BLACK)
        screen.blit(seq_text, (SCREEN_WIDTH//2 - seq_text.get_width()//2, SCREEN_HEIGHT//2 - 30))
        
        # Draw progress - ensure it doesn't overlap with the sequence
        progress = FONT_SMALL.render(f"Sequência {self.current_sequence_idx + 1} de {len(self.training_sequences)}", 
                                    True, GRAY)
        progress_y = min(SCREEN_HEIGHT//2 + 50, self.buttons["next"].rect.top - 60)
        screen.blit(progress, (SCREEN_WIDTH//2 - progress.get_width()//2, progress_y))
    
    def draw_test_instructions(self):
        """Draw test instructions screen"""
        # Draw title
        title = FONT_LARGE.render("Instruções para a Fase de Teste", True, BLUE)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        # Calculate safe area for instructions text
        bottom_limit = self.buttons["start"].rect.top - 60  # Space above button
        
        # Draw instructions - adjust for screen size
        instructions = [
            "Agora, você verá novas sequências de letras.",
            "Para cada sequência, decida se ela segue as mesmas regras",
            "das sequências que você viu na fase de treinamento.",
            "",
            "Responda se a sequência é 'gramatical' (segue as regras) ou",
            "'não gramatical' (viola as regras).",
            "",
            "Em seguida, indique seu nível de confiança na decisão (1-5).",
            "A escala de confiança é muito importante:",
            "1 = Apenas adivinhando; 5 = Totalmente certo",
            "",
            "Por favor, use toda a escala de confiança e seja honesto(a)!",
            "Pronto para começar?"
        ]
        
        # Adjust font size and spacing based on available space
        font_to_use = FONT_MEDIUM
        line_spacing = 35
        
        # Calculate total needed height
        total_height = len(instructions) * line_spacing
        available_height = bottom_limit - 130  # From y=130 to bottom limit
        
        # If not enough space, switch to smaller font
        if total_height > available_height:
            font_to_use = FONT_SMALL
            line_spacing = 25
            
        # If still not enough space, use tiny font and simplified instructions
        if len(instructions) * line_spacing > available_height:
            font_to_use = FONT_TINY
            line_spacing = 20
            instructions = [
                "Você verá novas sequências de letras.",
                "Decida se a sequência segue as regras do treinamento.",
                "",
                "Responda 'gramatical' ou 'não gramatical'.",
                "Depois indique sua confiança (1-5).",
                "1 = Adivinhando; 5 = Certeza",
                "",
                "Pronto para começar?"
            ]
        
        y_pos = 130
        for line in instructions:
            instr_text = font_to_use.render(line, True, BLACK)
            screen.blit(instr_text, (SCREEN_WIDTH//2 - instr_text.get_width()//2, y_pos))
            y_pos += line_spacing
    
    def draw_testing(self):
        """Draw testing screen"""
        # Draw phase title
        title = FONT_LARGE.render("Fase de Teste", True, BLUE)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        # Draw instruction
        instr = FONT_MEDIUM.render("Esta sequência é gramatical?", True, BLACK)
        screen.blit(instr, (SCREEN_WIDTH//2 - instr.get_width()//2, 120))
        
        # Draw sequence - ensure it's visible and centered
        sequence, _ = self.test_sequences[self.current_sequence_idx]
        seq_text = FONT_LARGE.render(sequence, True, BLACK)
        screen.blit(seq_text, (SCREEN_WIDTH//2 - seq_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        
        # Draw progress - position it to avoid overlapping with buttons
        progress = FONT_SMALL.render(f"Sequência {self.current_sequence_idx + 1} de {len(self.test_sequences)}", 
                                    True, GRAY)
        # Position progress text where it won't overlap with buttons
        safe_y = min(SCREEN_HEIGHT//2 + 30, self.buttons["grammatical"].rect.top - 80)
        screen.blit(progress, (SCREEN_WIDTH//2 - progress.get_width()//2, safe_y))
    
    def draw_confidence(self):
        """Draw confidence rating screen"""
        # Draw instruction
        title = FONT_LARGE.render("Nível de Confiança", True, BLUE)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        # Draw question
        instr = FONT_MEDIUM.render("Qual é o seu nível de confiança nesta resposta?", True, BLACK)
        screen.blit(instr, (SCREEN_WIDTH//2 - instr.get_width()//2, 150))
        
        # Calculate safe position for scale labels
        lowest_button_y = min(self.buttons[f"conf_{i}"].rect.top for i in range(1, 6))
        low_conf_y = lowest_button_y - 80
        
        # Draw scale labels
        low_conf = FONT_SMALL.render("1 = Baixa confiança (Adivinhando)", True, BLACK)
        high_conf = FONT_SMALL.render("5 = Alta confiança (Certeza)", True, BLACK)
        
        # Center the explanation text
        center_x = SCREEN_WIDTH // 2
        screen.blit(low_conf, (center_x - low_conf.get_width() // 2, low_conf_y))
        screen.blit(high_conf, (center_x - high_conf.get_width() // 2, low_conf_y + 30))
    
    def draw_results(self):
        """Draw results screen"""
        # Draw title
        title = FONT_LARGE.render("Resultados do Experimento", True, BLUE)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        # Adjust layout based on screen size
        if SCREEN_WIDTH < 800 or SCREEN_HEIGHT < 600:
            self.draw_results_single_column()
        else:
            self.draw_results_two_columns()
            
    def draw_results_single_column(self):
        """Draw results in a single column for smaller screens"""
        # For smaller screens, draw results in a single column
        results_text = [
            f"Acurácia: {self.results['accuracy']*100:.1f}%",
            f"d': {self.results['dprime']:.2f}",
            f"Critério (C): {self.results.get('criterion', 0):.2f}",
            f"Hits: {self.results['hits']}/{self.results['hits'] + self.results['misses']}",
            f"CR: {self.results['correct_rejections']}/{self.results['false_alarms'] + self.results['correct_rejections']}",
            f"Taxa de Hits: {self.results.get('hit_rate', 0)*100:.1f}%",
            f"Taxa de FA: {self.results.get('fa_rate', 0)*100:.1f}%",
            f"Confiança: {self.results['mean_confidence']:.1f}/5",
            f"Tempo: {self.results['mean_rt']:.2f}s"
        ]  # Close the list here
        
        # Use smaller font and spacing for small screens
        font_to_use = FONT_SMALL if SCREEN_HEIGHT >= 500 else FONT_TINY
        line_spacing = 30 if SCREEN_HEIGHT >= 500 else 20
        
        y_pos = 120
        for line in results_text:
            result_line = font_to_use.render(line, True, BLACK)
            screen.blit(result_line, (SCREEN_WIDTH//2 - result_line.get_width()//2, y_pos))
            y_pos += line_spacing
            
        # Draw interpretation if there's space
        if SCREEN_HEIGHT >= 500:
            y_pos += 20
            note_title = font_to_use.render("Aprendizado Implícito:", True, GREEN)
            screen.blit(note_title, (SCREEN_WIDTH//2 - note_title.get_width()//2, y_pos))
            
            y_pos += line_spacing
            if self.results.get('low_conf_correct', 0) > len(self.test_sequences) * 0.3:
                note = font_to_use.render("Evidência de aprendizado implícito.", True, BLACK)
            else:
                note = font_to_use.render("Sem evidências fortes de aprendizado implícito.", True, BLACK)
            screen.blit(note, (SCREEN_WIDTH//2 - note.get_width()//2, y_pos))
        
        # Draw message about saved results if there's space
        if y_pos + 60 < self.buttons["finish"].rect.top:
            message = FONT_TINY.render("Resultados completos salvos em CSV.", True, GRAY)
            screen.blit(message, (SCREEN_WIDTH//2 - message.get_width()//2, y_pos + 40))
            
    def draw_results_two_columns(self):
        """Draw results in two columns for larger screens"""
        # For larger screens, draw results in two columns
        # Draw results - column 1 (left side)
        results_text_col1 = [
            f"Acurácia: {self.results['accuracy']*100:.1f}%",
            f"Índice de Sensibilidade (d'): {self.results['dprime']:.2f}",
            f"Viés de Resposta (C): {self.results.get('criterion', 0):.2f}",
            f"Hits: {self.results['hits']} de {self.results['hits'] + self.results['misses']}",
            f"CR: {self.results['correct_rejections']} de {self.results['false_alarms'] + self.results['correct_rejections']}",
            f"Confiança Média: {self.results['mean_confidence']:.1f} / 5"
        ]
        
        # Column 2 (right side)
        results_text_col2 = [
            f"Taxa de Hits: {self.results.get('hit_rate', 0)*100:.1f}%",
            f"Taxa de FA: {self.results.get('fa_rate', 0)*100:.1f}%",
            f"Conf. em Hits: {self.results.get('hit_confidence', 0):.1f} / 5",
            f"Conf. em CR: {self.results.get('cr_confidence', 0):.1f} / 5",
            f"Acertos com Baixa Conf.: {self.results.get('low_conf_correct', 0)}",
            f"Tempo de Reação Médio: {self.results['mean_rt']:.2f}s"
        ]
        
        # Use a larger font size for better readability on big screens
        font_to_use = FONT_MEDIUM
        line_spacing = 35
        
        # Calculate column widths and x positions
        col_width = SCREEN_WIDTH // 2 - 40
        col1_x = 20
        col2_x = SCREEN_WIDTH // 2 + 20
        
        # Draw column 1
        y_pos = 120
        for line in results_text_col1:
            result_line = font_to_use.render(line, True, BLACK)
            screen.blit(result_line, (col1_x + 10, y_pos))
            y_pos += line_spacing
        
        # Draw column 2
        y_pos = 120
        for line in results_text_col2:
            result_line = font_to_use.render(line, True, BLACK)
            screen.blit(result_line, (col2_x + 10, y_pos))
            y_pos += line_spacing
        
        # Draw overall accuracy in the middle of the two columns
        overall_acc = FONT_LARGE.render(f"Acurácia Geral: {self.results['accuracy']*100:.1f}%", True, BLUE)
        screen.blit(overall_acc, (SCREEN_WIDTH//2 - overall_acc.get_width()//2, 80))
        
        # Draw message about saved results at the bottom
        message = FONT_TINY.render("Resultados completos salvos em CSV.", True, GRAY)
        screen.blit(message, (SCREEN_WIDTH//2 - message.get_width()//2, SCREEN_HEIGHT - 30))

    def save_results(self):
        """Save the results to a CSV file"""
        # Create results directory if it doesn't exist
        os.makedirs("results", exist_ok=True)
        
        # Define CSV file path
        file_path = os.path.join("results", "agl_experiment_results.csv")
        
        # Write results to CSV
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # Write header
            writer.writerow([
                "Acurácia", "d'", "Critério (C)", "Hits", "Misses", "False Alarms",
                "Correct Rejections", "Taxa de Hits", "Taxa de FA",
                "Confiança Média", "Tempo de Reação Médio", "Acertos com Baixa Conf."
            ])
            
            # Write data row
            writer.writerow([
                f"{self.results['accuracy']*100:.1f}%",
                f"{self.results['dprime']:.2f}",
                f"{self.results.get('criterion', 0):.2f}",
                self.results['hits'],
                self.results['misses'],
                self.results['false_alarms'],
                self.results['correct_rejections'],
                f"{self.results.get('hit_rate', 0)*100:.1f}%",
                f"{self.results.get('fa_rate', 0)*100:.1f}%",
                f"{self.results['mean_confidence']:.1f} / 5",
                f"{self.results['mean_rt']:.2f}s",
                self.results.get('low_conf_correct', 0)
            ])
        
        print(f"Results saved to {file_path}")

# Run the experiment
experiment = AGLExperiment()
while True:
    experiment.handle_events()
    experiment.draw()
