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

# class Animator:
#     def __init__(self, basename: str, file_extension: str, frame_count: int, size, loop=True):
#         self.basename = basename
#         self.file_extension = file_extension
#         self.frame_count = frame_count
#         self.size = size
#         self.loop = loop
#         self.frames = tuple([
#             load_frames()
#         ])
#         self.index = 0

#     def __iter__(self):
#         return self

#     def __next__(self):
#         if self.loop:
#             frame = self.frames[self.index]
#             self.index = (self.index + 1) % len(self.frames)
#             return frame
#         else:
#             if self.index < len(self.frames):
#                 frame = self.frames[self.index]
#                 self.index += 1
#                 return frame
#             else:
#                 raise StopIteration
            
def load_frames(basename:str, file_extension:str, size:int, frame_count:int):
    return [load_image(f"{basename}_{i}.{file_extension}", size, size) for i in range(frame_count)]

class StatefulAnimator[T]:
    def __init__(self, states:dict[T, tuple[Surface]], initial_state:T, loop=True, initial_index=0 ):
        # {walk: [], idle: []}
        # sprite = StatefulAnimator({
        #    idle: load_frames("assets/playeridle", "gif", SIZE, 6),
        #     #other states
        # }, "idle")
    
        self.state = initial_state
        self.states = states
        self.loop = loop
        self.index = initial_index

    def __iter__(self):
        return self

    @property
    def frames(self):
        return self.states[self.state]
    
    def __next__(self):
        if self.loop:
            frame = self.frames[self.index]
            self.index = (self.index + 1) % len(self.frames)
            return frame
        else:
            if self.index < len(self.frames):
                frame = self.frames[self.index]
                self.index += 1
                return frame
            else:
                raise StopIteration


def main():
    '''Run if main module'''
    player = StatefulAnimator(
        initial_state="idle",
        states={
            "idle": load_frames("assets/player/playeridle", "gif", 75, 6),
        }, 
    )
    # user presses A -> player.state = "FACING_WEST_IDLE"
    print(player)

if __name__ == '__main__':
    main()
