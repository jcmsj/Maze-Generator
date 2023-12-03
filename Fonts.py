import pygame


class Fonts:
    materialIcons:pygame.font.Font = None # type: ignore
    textFont: pygame.font.Font = None # type: ignore

    @classmethod
    def init(cls):
        pygame.font.init()
        cls.materialIcons = pygame.font.Font('assets/MaterialIconsOutlined-Regular.otf', 64)
        cls.textFont = pygame.font.Font("assets/pixel.ttf", 24)
