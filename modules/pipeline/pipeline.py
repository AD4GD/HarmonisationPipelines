class Pipeline(object):
    """
    Initializes a Pipeline instance.
    """
    def __init__(self):
        self.actions = []   # empty list where the actions will be appended before the execution.

    def append_actions(self, action):
        """
        Function that appends an action to the existing list of actions for Pipeline instance.
        :param action: func -> function that should be appended to the queue of actions.
        """
        self.actions.append(action)

    def run_pipeline(self):
        """
        Function that executes Pipeline queued actions, one after another.
        """
        for action in self.actions:
            action()   # fires action/function.