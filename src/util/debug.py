from rlbot.utils.rendering.rendering_manager import DEFAULT_GROUP_ID, RenderingManager


class Renderer:
    def __init__(self, renderer: RenderingManager, group_id: str=DEFAULT_GROUP_ID):
        self.renderer = renderer
        self.group_id = group_id

    def __enter__(self):
        self.renderer.begin_rendering(group_id=self.group_id)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.renderer.end_rendering()

    def __getattribute__(self, name):
        if name in ('renderer', 'group_id'):
            return object.__getattribute__(self, name)
        
        return getattr(self.renderer, name)
