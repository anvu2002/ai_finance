class InstanceState():
    _instance_count = 0
    
    def __init__(self):
        InstanceState.increment_instance()

    @classmethod
    def increment_instance(cls):
        cls._instance_count +=1
    
    @classmethod
    def get_count(cls):
        return cls._instance_count
    
a = InstanceState()
b = InstanceState()
instance_count = InstanceState.get_count()

breakpoint()

