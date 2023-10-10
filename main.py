import pygame
import sqlite3
from random import randrange

import settings
from button import Button


class Snake:

    def __init__(self):
        """Setting up pygame and calling menu method to start events"""
        pygame.init()
        self.SCREEN = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
        self.clock = pygame.time.Clock()
        self.create_records_table()
        self.menu()

    @staticmethod
    def create_records_table():
        """Method which creates table for storing records"""
        with sqlite3.connect("snake.db") as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS records (score INTEGER);")

    @staticmethod
    def select_best_score():
        """Method which returns maximal score of the table"""
        with sqlite3.connect("snake.db") as conn:
            cursor = conn.cursor()
            best_score = cursor.execute(
                "SELECT ifnull(MAX(score), 0) FROM records"
            ).fetchone()[0]
            return best_score

    @staticmethod
    def font(size):
        """Method for convenient font setup"""
        return pygame.font.SysFont("times new roman", size)

    def menu(self):
        # Main window of the game

        pygame.display.set_caption("Меню")

        self.SCREEN.fill(pygame.Color("#ECECEC"))
        record = self.font(100).render(f"Рекорд: {self.select_best_score()}", True, "#4e89ef")
        record_rect = record.get_rect(center=(640, 100))
        self.SCREEN.blit(record, record_rect)

        play_button = Button(
            pos=(640, 250),
            text_input="Играть",
            font=self.font(75),
            color="black",
        )
        reset_button = Button(
            pos=(640, 400),
            text_input="Сбросить",
            font=self.font(75),
            color="black",
        )
        quit_button = Button(
            pos=(640, 550),
            text_input="Выйти",
            font=self.font(75),
            color="black",
        )
        play_button.update(self.SCREEN)
        reset_button.update(self.SCREEN)
        quit_button.update(self.SCREEN)

        while True:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if play_button.is_pressed(mouse_pos):
                        return self.play()
                    if reset_button.is_pressed(mouse_pos):
                        return self.reset()
                    if quit_button.is_pressed(mouse_pos):
                        exit()
            pygame.display.update()
            self.clock.tick(60)

    def play(self):
        # Game logic

        pygame.display.set_caption("Змейка")

        objects_size = settings.OBJECTS_SIZE
        apple = randrange(0, settings.WIDTH, objects_size), randrange(0, settings.HEIGHT, objects_size)
        snake_speed = settings.SNAKE_SPEED
        snake_length = 1
        snake_x, snake_y = settings.WIDTH // 2, settings.HEIGHT // 2
        snake = [(snake_x, snake_y)]
        snake_direction = ""
        dx = dy = 0
        score = 0
        score_font = self.font(45)

        while True:
            self.SCREEN.fill(pygame.Color("#ECECEC"))
            # drawing snake
            for i, j in snake:
                pygame.draw.rect(
                    self.SCREEN,
                    pygame.Color("green"),
                    (i, j, objects_size, objects_size)
                )
            # drawing apple
            pygame.draw.rect(self.SCREEN, pygame.Color("red"), (*apple, objects_size, objects_size))
            # showing score
            render_score = score_font.render(
                f"Счет: {score}", True, pygame.Color("#4e89ef")
            )
            self.SCREEN.blit(render_score, (10, 10))
            # moving snake
            snake_x += dx * objects_size
            snake_y += dy * objects_size
            snake.append((snake_x, snake_y))
            snake = snake[-snake_length:]
            # eating apple
            if snake[-1] == apple:
                apple = randrange(0, settings.WIDTH, objects_size), randrange(0, settings.HEIGHT, objects_size)
                snake_length += 1
                snake_speed += 1
                score += 1
            # check if game is over
            if (
                snake_x < 0 or
                snake_x > settings.WIDTH - objects_size or
                snake_y < 0 or
                snake_y > settings.HEIGHT - objects_size or
                len(snake) != len(set(snake))
            ):
                if score > self.select_best_score():
                    with sqlite3.connect("snake.db") as conn:
                        cursor = conn.cursor()
                        cursor.execute(f"INSERT INTO records VALUES ({score})")
                        record = self.font(75).render(
                            "Новый рекорд!!!", True, "#4e89ef"
                        )
                        record_rect = record.get_rect(center=(640, 120))
                        self.SCREEN.blit(record, record_rect)

                restart_button = Button(
                    pos=(640, 250),
                    text_input="Рестарт",
                    font=self.font(75),
                    color="black",
                )
                menu_button = Button(
                    pos=(640, 400),
                    text_input="Меню",
                    font=self.font(75),
                    color="black",
                )
                restart_button.update(self.SCREEN)
                menu_button.update(self.SCREEN)

                while True:
                    mouse_pos = pygame.mouse.get_pos()
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            exit()
                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            if restart_button.is_pressed(mouse_pos):
                                return self.play()
                            if menu_button.is_pressed(mouse_pos):
                                return self.menu()
                    pygame.display.update()
                    self.clock.tick(60)

            # We determine the direction of the snake and block the
            # possibility of movement in the opposite direction
            key = pygame.key.get_pressed()
            if key[pygame.K_w] and snake_direction != "DOWN":
                dx, dy = 0, -1
                snake_direction = "UP"
            elif key[pygame.K_s] and snake_direction != "UP":
                dx, dy = 0, 1
                snake_direction = "DOWN"
            elif key[pygame.K_a] and snake_direction != "RIGHT":
                dx, dy = -1, 0
                snake_direction = "LEFT"
            elif key[pygame.K_d] and snake_direction != "LEFT":
                dx, dy = 1, 0
                snake_direction = "RIGHT"

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()

            pygame.display.update()
            self.clock.tick(snake_speed)

    def reset(self):
        # Erasing data from the records table
        pygame.display.set_caption("Сброс рекорда")

        with sqlite3.connect("snake.db") as conn:
            conn.execute("DELETE FROM records")

        self.SCREEN.fill(pygame.Color("#ECECEC"))
        reset_font = self.font(45).render(
            "Рекорд сброшен. Нажмите Escape чтобы вернуться в меню", True, "black"
        )
        reset_rect = reset_font.get_rect(center=(640, 260))
        self.SCREEN.blit(reset_font, reset_rect)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return self.menu()

            pygame.display.update()
            self.clock.tick(60)


if __name__ == "__main__":
    Snake()
