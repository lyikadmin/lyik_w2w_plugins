from lyikpluginmanager import ContextModel
class DocPluginConfig:
    """
    Singleton for holding context(ContextModel) passed to plugin, for easy access!
    """
    context: ContextModel | None = None

    _instance = None

    def __new__(cls,context=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.context =context
            
        return cls._instance
    def is_none(self): 
        return self.context is None