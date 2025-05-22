import pytest
import pygame
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from DuckHunt import Player, NormalDuck, FastDuck, FakeDuck, BonusDuck, DuckFactory


pygame.init()


@pytest.fixture
def dummy_duck():
    return NormalDuck()


def test_player_initial_bullets_and_score():
    player = Player()
    assert player.bullets == 5
    assert player.score == 0


def test_player_successful_shoot():
    player = Player()
    duck = NormalDuck()
    duck.rect.topleft = (100, 100)

    # Створимо прямокутник точки, яка потрапляє у прямокутник качки
    position = (duck.rect.centerx, duck.rect.centery)

    hit = player.shoot(position, [duck])

    assert hit is True
    assert duck.is_hit is True
    assert player.score >= 1


def test_player_miss_shot():
    player = Player()
    duck = NormalDuck()
    duck.rect.topleft = (100, 100)

    position = (0, 0)  # координати явно поза качкою
    hit = player.shoot(position, [duck])

    assert hit is False
    assert player.score == 0
    assert duck.is_hit is False


def test_factory_creates_valid_duck():
    duck = DuckFactory.create_duck()
    assert isinstance(duck, (NormalDuck, FastDuck, FakeDuck, BonusDuck))


def test_bonus_duck_restore_miss():
    player = Player()
    player.bullets = 2
    duck = BonusDuck()
    duck.rect.topleft = (100, 100)
    position = (duck.rect.centerx, duck.rect.centery)

    player.shoot(position, [duck])
    assert player.bullets == 3  # bullets restored by 1


def test_fake_duck_negative_score():
    player = Player()
    duck = FakeDuck()
    duck.rect.topleft = (100, 100)
    position = (duck.rect.centerx, duck.rect.centery)

    player.shoot(position, [duck])
    assert player.score == -1


def test_duck_movement():
    duck = NormalDuck()
    initial_x = duck.x
    initial_y = duck.y

    duck.move()
    assert duck.x != initial_x or duck.y != initial_y
