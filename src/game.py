import pygame
import json
import sys
from lines import Line
from notes import Note
from clock import GameClock
class Game:
    def __init__(self, screen, chart_path, config):
        self.screen = screen
        self.config = config
        self.lines = []
        self.notes = []
        self.load_chart(chart_path)
        self.clock = GameClock(config['fps'])
        self.chart_finished = False

    def load_chart(self, chart_path):
        with open(chart_path, 'r') as file:
            chart_data = json.load(file)
        
        # Convert key_bindings values to actual Pygame key constants
        key_bindings = {k: getattr(pygame, v) for k, v in self.config['key_bindings'].items()}
        
        for line_data in chart_data['lines']:
            key_binding = line_data['key_binding']
            if key_binding not in key_bindings:
                raise KeyError(f"Key binding '{key_binding}' not found in config key_bindings.")
            self.lines.append(Line(
                start_pos=line_data['start_pos'],
                end_pos=line_data['end_pos'],
                key_binding=key_bindings[key_binding],
                movement=line_data['movement']
            ))
        self.note_data = chart_data['notes']

    def run(self):
        running = True
        start_time = pygame.time.get_ticks()

        while running:
            current_time = pygame.time.get_ticks() - start_time

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    for line in self.lines:
                        if event.key == line.key_binding:
                            # Check for note collision here (basic placeholder)
                            pass

            # Update line positions based on movement data
            for line in self.lines:
                line.update_position(current_time)

            # Check if it's time to add a new note
            for note_data in self.note_data:
                if current_time >= note_data['time'] and 'spawned' not in note_data:
                    line_index = note_data['line']
                    note_pos = list(self.lines[line_index].start_pos)
                    self.lines[line_index].add_note(Note(note_pos, self.config['note_speed']))
                    note_data['spawned'] = True  # Mark the note as spawned

            # Check if all notes have been processed
            if all('spawned' in note_data for note_data in self.note_data) and all(len(line.notes) == 0 for line in self.lines):
                self.chart_finished = True

            if self.chart_finished:
                running = False

            self.screen.fill((0, 0, 0))
            
            for line in self.lines:
                line.draw(self.screen)
                line.update_notes()
                for note in line.notes:
                    note.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick()

        pygame.quit()
        sys.exit()