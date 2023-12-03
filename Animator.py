from pygame import Surface, transform, image

def load_image(path:str, width:int, length:int):
    """
    Load an image from the given path and resize it to the specified size.

    Args:
        path (str): The path to the image file.
        size (int): The desired size of the image.

    Returns:
        pygame.Surface: The scaled image.
    """
    return transform.scale(image.load(path), (width, length))
            
def load_frames(basename:str, file_extension:str, size:int, frame_count:int):
    return [load_image(f"{basename}_{i}.{file_extension}", size, size) for i in range(frame_count)]

def animator(basename: str, file_extension: str, frame_count: int, size):
    """
    Generates frames for animation based on the given parameters.

    Args:
        basename (str): The base name of the animation frames.
        file_extension (str): The file extension of the animation frames.
        frame_count (int): The number of frames in the animation.
        size: The size of each frame.
        loop (bool, optional): Whether the animation should loop. Defaults to True.

    Yields:
        frame: The next frame in the animation.

    """
    frames = tuple([
        load_image(f"{basename}_{i}.{file_extension}", size,size) for i in range(frame_count)
    ])
    index = 0
    while True:
        yield frames[index]
        index = (index + 1) % len(frames)
class StatefulAnimator[T]:
    def __init__(self, states:dict[T, tuple[Surface]], initial_state:T, initial_index=0 ):
        # {walk: [], idle: []}
        # sprite = StatefulAnimator({
        #    idle: load_frames("assets/playeridle", "gif", SIZE, 6),
        #     #other states
        # }, "idle")
        self._state = initial_state
        self.states = states
        self.index = initial_index

    def __iter__(self):
        return self
    @property
    def state(self):
        return self._state  
    @state.setter
    def state(self, state):
        if state not in self.states:
            raise ValueError(f"state {state} not in {self.states}")
        self._state = state
        self.index = 0

    @property
    def frames(self):
        return self.states[self.state]

    def __next__(self):
        frame = self.frames[self.index]
        self.index = (self.index + 1) % len(self.frames)
        return frame

def main():
    '''Run if main module'''
    player = StatefulAnimator(
        initial_state="idle",
        states={
            "idle": load_frames("assets/player/playeridle", "gif", 75,  6),
            "walk": load_frames("assets/player/playerwalk", "gif", 75,  4),
        }, 
    )
    iterator = iter(player)
    while True:
        move = input()
        if move == "idle":
            player.state = "idle"
        elif move == "walk":
            player.state = "walk"
        print(f"state: {player.state}")
        print(next(iterator))
    # user presses A -> player.state = "FACING_WEST_IDLE"

if __name__ == '__main__':
    main()
