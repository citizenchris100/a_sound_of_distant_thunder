"""
Character Questionnaire System for A Sound of Distant Thunder
Implements the character class selection through a personality quiz.
"""
import pygame
import logging
import random

# Configure logging
logger = logging.getLogger("CharacterQuestionnaire")

class CharacterQuestion:
    """Class representing a question in the character questionnaire"""
    def __init__(self, text, options, class_points):
        """
        Initialize a character question.
        
        Args:
            text (str): Question text
            options (list): List of answer options
            class_points (dict): Points awarded to each class for each option
        """
        self.text = text
        self.options = options
        self.class_points = class_points

class CharacterQuestionnaire:
    """
    System for determining player character class through a personality quiz.
    """
    def __init__(self, game_engine, asset_manager):
        """
        Initialize the character questionnaire.
        
        Args:
            game_engine: GameEngine instance
            asset_manager: AssetManager instance
        """
        self.game_engine = game_engine
        self.asset_manager = asset_manager
        
        # Questionnaire state
        self.questions = []
        self.current_question = 0
        self.selected_option = -1
        self.class_scores = {
            "merc": 0,
            "soldier": 0,
            "ranger": 0,
            "spy": 0
        }
        self.visible = False
        
        # Visual elements
        self.font_title = None
        self.font_question = None
        self.font_option = None
        self.background_color = (20, 20, 40)
        self.title_color = (200, 200, 255)
        self.question_color = (255, 255, 255)
        self.option_color = (200, 200, 200)
        self.selected_color = (100, 100, 200)
        self.border_color = (100, 100, 150)
        
        # Initialize questions
        self._init_questions()
        
        logger.info("Character Questionnaire initialized")
    
    def _init_questions(self):
        """Initialize the list of questions"""
        # Question 1: Combat preference
        self.questions.append(CharacterQuestion(
            "When faced with a challenging situation, what's your preferred approach?",
            [
                "Take aim and fire - keeping a safe distance is key.",
                "Charge in with your best weapon and overwhelm them with force.",
                "Analyze the situation carefully first, then strike with precision.",
                "Find a clever, indirect solution that avoids direct confrontation."
            ],
            {
                0: {"merc": 3, "soldier": 1, "ranger": 1, "spy": 0},
                1: {"merc": 1, "soldier": 3, "ranger": 1, "spy": 0},
                2: {"merc": 0, "soldier": 1, "ranger": 3, "spy": 1},
                3: {"merc": 0, "soldier": 0, "ranger": 0, "spy": 3}
            }
        ))
        
        # Question 2: Social approach
        self.questions.append(CharacterQuestion(
            "When meeting potential allies, how do you typically approach them?",
            [
                "Direct and businesslike - let's talk terms and get to work.",
                "Disciplined and formal - respect and order are important.",
                "Cautious but friendly - actions speak louder than words.",
                "Charming and perceptive - gathering information while appearing casual."
            ],
            {
                0: {"merc": 3, "soldier": 1, "ranger": 0, "spy": 1},
                1: {"merc": 1, "soldier": 3, "ranger": 0, "spy": 0},
                2: {"merc": 0, "soldier": 1, "ranger": 3, "spy": 1},
                3: {"merc": 1, "soldier": 0, "ranger": 0, "spy": 3}
            }
        ))
        
        # Question 3: Equipment preference
        self.questions.append(CharacterQuestion(
            "Which piece of equipment would you never leave behind?",
            [
                "A reliable pistol with plenty of ammunition.",
                "Heavy-duty body armor and a combat knife.",
                "A versatile hunting knife and survival gear.",
                "Specialized tools for bypassing security systems."
            ],
            {
                0: {"merc": 3, "soldier": 1, "ranger": 0, "spy": 1},
                1: {"merc": 1, "soldier": 3, "ranger": 1, "spy": 0},
                2: {"merc": 0, "soldier": 1, "ranger": 3, "spy": 1},
                3: {"merc": 1, "soldier": 0, "ranger": 0, "spy": 3}
            }
        ))
        
        # Question 4: Problem-solving approach
        self.questions.append(CharacterQuestion(
            "You encounter a locked door blocking your path. What's your first instinct?",
            [
                "Shoot the lock or hinges to break it open.",
                "Bust it down with brute force.",
                "Look for an alternative route or environmental solution.",
                "Try to pick the lock or hack the electronic security."
            ],
            {
                0: {"merc": 3, "soldier": 1, "ranger": 0, "spy": 1},
                1: {"merc": 1, "soldier": 3, "ranger": 0, "spy": 0},
                2: {"merc": 0, "soldier": 0, "ranger": 3, "spy": 1},
                3: {"merc": 0, "soldier": 0, "ranger": 1, "spy": 3}
            }
        ))
        
        # Question 5: Background
        self.questions.append(CharacterQuestion(
            "Before joining this mission, your background primarily involved:",
            [
                "Contract work for various corporations and private entities.",
                "Formal military service and structured operations.",
                "Wilderness expeditions and survival in harsh environments.",
                "Covert operations requiring discretion and social intelligence."
            ],
            {
                0: {"merc": 3, "soldier": 0, "ranger": 1, "spy": 1},
                1: {"merc": 1, "soldier": 3, "ranger": 0, "spy": 1},
                2: {"merc": 0, "soldier": 1, "ranger": 3, "spy": 0},
                3: {"merc": 1, "soldier": 0, "ranger": 0, "spy": 3}
            }
        ))
    
    def start(self):
        """Start the questionnaire"""
        self.visible = True
        self.current_question = 0
        self.selected_option = -1
        self.class_scores = {
            "merc": 0,
            "soldier": 0,
            "ranger": 0,
            "spy": 0
        }
        
        # Initialize fonts if needed
        if not self.font_title:
            self.font_title = self.asset_manager.get_font("title") or pygame.font.Font(None, 36)
        if not self.font_question:
            self.font_question = self.asset_manager.get_font("dialog") or pygame.font.Font(None, 28)
        if not self.font_option:
            self.font_option = self.asset_manager.get_font("ui") or pygame.font.Font(None, 24)
        
        logger.info("Character questionnaire started")
    
    def update(self, dt):
        """
        Update questionnaire state.
        
        Args:
            dt (float): Time delta in seconds
        """
        if not self.visible:
            return
    
    def render(self, surface):
        """
        Render the questionnaire to the given surface.
        
        Args:
            surface (pygame.Surface): Surface to render on
        """
        if not self.visible:
            return
            
        # Get screen dimensions
        screen_width, screen_height = surface.get_size()
        
        # Fill background
        surface.fill(self.background_color)
        
        # Draw title
        title_text = "Character Questionnaire"
        title_surface = self.font_title.render(title_text, True, self.title_color)
        title_rect = title_surface.get_rect(center=(screen_width // 2, 50))
        surface.blit(title_surface, title_rect)
        
        # Draw progress
        progress_text = f"Question {self.current_question + 1} of {len(self.questions)}"
        progress_surface = self.font_option.render(progress_text, True, self.option_color)
        progress_rect = progress_surface.get_rect(center=(screen_width // 2, 90))
        surface.blit(progress_surface, progress_rect)
        
        # Draw current question
        if self.current_question < len(self.questions):
            question = self.questions[self.current_question]
            
            # Draw question text
            self._render_wrapped_text(
                surface,
                question.text,
                self.font_question,
                self.question_color,
                pygame.Rect(100, 150, screen_width - 200, 100)
            )
            
            # Draw options
            for i, option in enumerate(question.options):
                option_rect = pygame.Rect(100, 250 + i * 60, screen_width - 200, 50)
                
                # Draw option background
                if i == self.selected_option:
                    pygame.draw.rect(surface, self.selected_color, option_rect, 0)
                
                # Draw option border
                pygame.draw.rect(surface, self.border_color, option_rect, 2)
                
                # Draw option text
                self._render_wrapped_text(
                    surface,
                    option,
                    self.font_option,
                    self.option_color,
                    pygame.Rect(option_rect.left + 10, option_rect.top + 5, option_rect.width - 20, option_rect.height - 10)
                )
    
    def _render_wrapped_text(self, surface, text, font, color, rect):
        """
        Render text with word wrapping.
        
        Args:
            surface (pygame.Surface): Surface to render on
            text (str): Text to render
            font (pygame.font.Font): Font to use
            color (tuple): Text color (r, g, b)
            rect (pygame.Rect): Rectangle to contain the text
        """
        words = text.split(' ')
        space_width = font.size(' ')[0]
        x, y = rect.left, rect.top
        
        for word in words:
            word_surface = font.render(word, True, color)
            word_width, word_height = word_surface.get_size()
            
            if x + word_width >= rect.right:
                x = rect.left
                y += word_height
                
            surface.blit(word_surface, (x, y))
            x += word_width + space_width
    
    def handle_mouse_click(self, event):
        """
        Handle mouse click events.
        
        Args:
            event (pygame.event.Event): Mouse click event
            
        Returns:
            bool: True if event was handled, False otherwise
        """
        if not self.visible:
            return False
            
        # Get screen dimensions
        screen_width, screen_height = pygame.display.get_surface().get_size()
        
        # Check if click was on an option
        if self.current_question < len(self.questions):
            question = self.questions[self.current_question]
            
            for i, _ in enumerate(question.options):
                option_rect = pygame.Rect(100, 250 + i * 60, screen_width - 200, 50)
                
                if option_rect.collidepoint(event.pos):
                    # Select option
                    self.selected_option = i
                    return True
            
            # Check if click was on continue button (if option selected)
            if self.selected_option >= 0:
                continue_rect = pygame.Rect(screen_width // 2 - 100, screen_height - 100, 200, 50)
                
                if continue_rect.collidepoint(event.pos):
                    self._answer_question()
                    return True
        
        return False
    
    def handle_key_press(self, event):
        """
        Handle keyboard events.
        
        Args:
            event (pygame.event.Event): Key press event
            
        Returns:
            bool: True if event was handled, False otherwise
        """
        if not self.visible:
            return False
            
        # Number keys select options
        if event.key >= pygame.K_1 and event.key <= pygame.K_9:
            option_index = event.key - pygame.K_1
            
            if self.current_question < len(self.questions):
                question = self.questions[self.current_question]
                
                if option_index < len(question.options):
                    self.selected_option = option_index
                    return True
        
        # Enter key confirms selection
        elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
            if self.selected_option >= 0:
                self._answer_question()
                return True
        
        return False
    
    def _answer_question(self):
        """Process the selected answer and move to the next question"""
        if self.current_question < len(self.questions) and self.selected_option >= 0:
            # Get current question
            question = self.questions[self.current_question]
            
            # Add points based on selected option
            option_points = question.class_points.get(self.selected_option, {})
            
            for class_name, points in option_points.items():
                self.class_scores[class_name] += points
            
            # Move to next question
            self.current_question += 1
            self.selected_option = -1
            
            # Check if questionnaire is complete
            if self.current_question >= len(self.questions):
                self._complete_questionnaire()
    
    def _complete_questionnaire(self):
        """Complete the questionnaire and determine the character class"""
        # Find class with highest score
        highest_score = -1
        highest_class = None
        
        for class_name, score in self.class_scores.items():
            if score > highest_score:
                highest_score = score
                highest_class = class_name
            elif score == highest_score:
                # Tie breaker - random selection
                if random.random() < 0.5:
                    highest_class = class_name
        
        # Default to random if all scores are 0
        if highest_class is None:
            highest_class = random.choice(list(self.class_scores.keys()))
        
        logger.info(f"Questionnaire complete. Selected class: {highest_class}")
        
        # Hide questionnaire
        self.visible = False
        
        # Start new game with selected class
        self.game_engine.initialize_new_game(highest_class)


class CharacterSelectionScreen:
    """
    Screen for selecting character class directly or via questionnaire.
    """
    def __init__(self, game_engine, asset_manager):
        """
        Initialize the character selection screen.
        
        Args:
            game_engine: GameEngine instance
            asset_manager: AssetManager instance
        """
        self.game_engine = game_engine
        self.asset_manager = asset_manager
        
        # Screen state
        self.visible = False
        self.selected_class = None
        
        # Character classes
        self.classes = {
            "merc": {
                "name": "Mercenary",
                "description": "Specialists in firearms and tactical combat. Mercs are pragmatic and efficient, getting the job done with minimal fuss.",
                "stats": {
                    "defence": "Average",
                    "strength": "Low",
                    "gun_skill": "High",
                    "luck": "Average",
                    "charm": "Low",
                    "stealth": "High"
                }
            },
            "soldier": {
                "name": "Soldier",
                "description": "Well-rounded fighters with military training. Soldiers are disciplined and dependable, with experience in structured operations.",
                "stats": {
                    "defence": "High",
                    "strength": "High",
                    "gun_skill": "Average",
                    "luck": "Average",
                    "charm": "Average",
                    "stealth": "Low"
                }
            },
            "ranger": {
                "name": "Ranger",
                "description": "Masters of melee combat and survival. Rangers are resourceful and adaptable, able to thrive in harsh environments.",
                "stats": {
                    "defence": "Average",
                    "strength": "High",
                    "gun_skill": "Low",
                    "luck": "Average",
                    "charm": "Average",
                    "stealth": "Average"
                }
            },
            "spy": {
                "name": "Spy",
                "description": "Experts in deception and intelligence gathering. Spies are charming and perceptive, adept at manipulating social situations.",
                "stats": {
                    "defence": "Low",
                    "strength": "Low",
                    "gun_skill": "Low",
                    "luck": "High",
                    "charm": "High",
                    "stealth": "High"
                }
            }
        }
        
        # Visual elements
        self.font_title = None
        self.font_heading = None
        self.font_text = None
        self.font_button = None
        self.background_color = (20, 20, 40)
        self.title_color = (200, 200, 255)
        self.text_color = (255, 255, 255)
        self.button_color = (60, 60, 100)
        self.selected_color = (100, 100, 200)
        self.highlight_color = (120, 120, 220)
        
        # Create questionnaire
        self.questionnaire = CharacterQuestionnaire(game_engine, asset_manager)
        
        logger.info("Character Selection Screen initialized")
    
    def show(self):
        """Show the character selection screen"""
        self.visible = True
        self.selected_class = None
        
        # Initialize fonts if needed
        if not self.font_title:
            self.font_title = self.asset_manager.get_font("title") or pygame.font.Font(None, 48)
        if not self.font_heading:
            self.font_heading = self.asset_manager.get_font("dialog") or pygame.font.Font(None, 36)
        if not self.font_text:
            self.font_text = self.asset_manager.get_font("ui") or pygame.font.Font(None, 24)
        if not self.font_button:
            self.font_button = self.asset_manager.get_font("ui") or pygame.font.Font(None, 28)
        
        logger.info("Character Selection Screen shown")
    
    def update(self, dt):
        """
        Update screen state.
        
        Args:
            dt (float): Time delta in seconds
        """
        if not self.visible:
            return
            
        # Update questionnaire if active
        if self.questionnaire.visible:
            self.questionnaire.update(dt)
    
    def render(self, surface):
        """
        Render the screen to the given surface.
        
        Args:
            surface (pygame.Surface): Surface to render on
        """
        if not self.visible:
            return
            
        # If questionnaire is active, render it instead
        if self.questionnaire.visible:
            self.questionnaire.render(surface)
            return
            
        # Get screen dimensions
        screen_width, screen_height = surface.get_size()
        
        # Fill background
        surface.fill(self.background_color)
        
        # Draw title
        title_text = "Choose Your Character"
        title_surface = self.font_title.render(title_text, True, self.title_color)
        title_rect = title_surface.get_rect(center=(screen_width // 2, 50))
        surface.blit(title_surface, title_rect)
        
        # Draw class options
        class_width = (screen_width - 150) // 2
        class_height = 200
        
        positions = [
            (50, 120),  # Merc
            (75 + class_width, 120),  # Soldier
            (50, 140 + class_height),  # Ranger
            (75 + class_width, 140 + class_height)  # Spy
        ]
        
        for i, (class_id, class_data) in enumerate(self.classes.items()):
            # Draw class box
            class_rect = pygame.Rect(positions[i][0], positions[i][1], class_width, class_height)
            
            # Fill based on selection
            if class_id == self.selected_class:
                pygame.draw.rect(surface, self.selected_color, class_rect, 0)
            else:
                pygame.draw.rect(surface, self.button_color, class_rect, 0)
                
            # Draw border
            pygame.draw.rect(surface, self.highlight_color, class_rect, 2)
            
            # Draw class name
            name_surface = self.font_heading.render(class_data["name"], True, self.text_color)
            name_rect = name_surface.get_rect(midtop=(class_rect.centerx, class_rect.top + 20))
            surface.blit(name_surface, name_rect)
            
            # Draw class description
            description_rect = pygame.Rect(
                class_rect.left + 10,
                name_rect.bottom + 10,
                class_rect.width - 20,
                60
            )
            self._render_wrapped_text(
                surface,
                class_data["description"],
                self.font_text,
                self.text_color,
                description_rect
            )
            
            # Draw stats
            stats_y = description_rect.bottom + 10
            for stat, value in class_data["stats"].items():
                stat_text = f"{stat.capitalize()}: {value}"
                stat_surface = self.font_text.render(stat_text, True, self.text_color)
                surface.blit(stat_surface, (class_rect.left + 10, stats_y))
                stats_y += self.font_text.get_linesize()
        
        # Draw buttons
        button_y = screen_height - 100
        
        # Direct selection button
        if self.selected_class:
            select_rect = pygame.Rect(screen_width // 2 - 210, button_y, 200, 50)
            pygame.draw.rect(surface, self.button_color, select_rect, 0)
            pygame.draw.rect(surface, self.highlight_color, select_rect, 2)
            
            select_text = "Select Character"
            select_surface = self.font_button.render(select_text, True, self.text_color)
            select_rect_center = select_surface.get_rect(center=select_rect.center)
            surface.blit(select_surface, select_rect_center)
        
        # Questionnaire button
        quiz_rect = pygame.Rect(screen_width // 2 + 10, button_y, 200, 50)
        pygame.draw.rect(surface, self.button_color, quiz_rect, 0)
        pygame.draw.rect(surface, self.highlight_color, quiz_rect, 2)
        
        quiz_text = "Take Questionnaire"
        quiz_surface = self.font_button.render(quiz_text, True, self.text_color)
        quiz_rect_center = quiz_surface.get_rect(center=quiz_rect.center)
        surface.blit(quiz_surface, quiz_rect_center)
    
    def _render_wrapped_text(self, surface, text, font, color, rect):
        """
        Render text with word wrapping.
        
        Args:
            surface (pygame.Surface): Surface to render on
            text (str): Text to render
            font (pygame.font.Font): Font to use
            color (tuple): Text color (r, g, b)
            rect (pygame.Rect): Rectangle to contain the text
        """
        words = text.split(' ')
        space_width = font.size(' ')[0]
        x, y = rect.left, rect.top
        
        for word in words:
            word_surface = font.render(word, True, color)
            word_width, word_height = word_surface.get_size()
            
            if x + word_width >= rect.right:
                x = rect.left
                y += word_height
                
            # Stop if we run out of vertical space
            if y + word_height >= rect.bottom:
                break
                
            surface.blit(word_surface, (x, y))
            x += word_width + space_width
    
    def handle_mouse_click(self, event):
        """
        Handle mouse click events.
        
        Args:
            event (pygame.event.Event): Mouse click event
            
        Returns:
            bool: True if event was handled, False otherwise
        """
        if not self.visible:
            return False
            
        # If questionnaire is active, handle it
        if self.questionnaire.visible:
            return self.questionnaire.handle_mouse_click(event)
            
        # Get screen dimensions
        screen_width, screen_height = pygame.display.get_surface().get_size()
        
        # Check if click was on a class
        class_width = (screen_width - 150) // 2
        class_height = 200
        
        positions = [
            (50, 120),  # Merc
            (75 + class_width, 120),  # Soldier
            (50, 140 + class_height),  # Ranger
            (75 + class_width, 140 + class_height)  # Spy
        ]
        
        class_ids = list(self.classes.keys())
        
        for i, position in enumerate(positions):
            class_rect = pygame.Rect(position[0], position[1], class_width, class_height)
            
            if class_rect.collidepoint(event.pos):
                self.selected_class = class_ids[i]
                return True
        
        # Check if click was on select button
        if self.selected_class:
            select_rect = pygame.Rect(screen_width // 2 - 210, screen_height - 100, 200, 50)
            
            if select_rect.collidepoint(event.pos):
                logger.info(f"Character class selected: {self.selected_class}")
                
                # Hide selection screen
                self.visible = False
                
                # Start new game with selected class
                self.game_engine.initialize_new_game(self.selected_class)
                
                return True
        
        # Check if click was on questionnaire button
        quiz_rect = pygame.Rect(screen_width // 2 + 10, screen_height - 100, 200, 50)
        
        if quiz_rect.collidepoint(event.pos):
            # Start questionnaire
            self.questionnaire.start()
            
            return True
        
        return False
    
    def handle_key_press(self, event):
        """
        Handle keyboard events.
        
        Args:
            event (pygame.event.Event): Key press event
            
        Returns:
            bool: True if event was handled, False otherwise
        """
        if not self.visible:
            return False
            
        # If questionnaire is active, handle it
        if self.questionnaire.visible:
            return self.questionnaire.handle_key_press(event)
            
        # Number keys select classes
        if event.key >= pygame.K_1 and event.key <= pygame.K_4:
            class_index = event.key - pygame.K_1
            class_ids = list(self.classes.keys())
            
            if class_index < len(class_ids):
                self.selected_class = class_ids[class_index]
                return True
        
        # Enter key confirms selection
        elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
            if self.selected_class:
                logger.info(f"Character class selected: {self.selected_class}")
                
                # Hide selection screen
                self.visible = False
                
                # Start new game with selected class
                self.game_engine.initialize_new_game(self.selected_class)
                
                return True
        
        # Q key starts questionnaire
        elif event.key == pygame.K_q:
            # Start questionnaire
            self.questionnaire.start()
            
            return True
        
        return False
    
    def hide(self):
        """Hide the character selection screen"""
        self.visible = False
        self.questionnaire.visible = False