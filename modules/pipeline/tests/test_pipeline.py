from modules.pipeline import pipeline


def test_pipeline():
    test_pipe = pipeline.Pipeline()

    def action_1():
        return

    def action_2():
        return

    test_pipe.append_actions(action_1)
    test_pipe.append_actions(action_2)
    assert test_pipe.actions == [action_1, action_2]
