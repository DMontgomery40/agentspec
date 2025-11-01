def y():
    """
    ---agentspec
    what: |
      test
        deps:
          calls:
            - x
          imports:
            - os

    why: |
      test

        changelog:
          - "- 2025-10-31: test (abc1234)"
        ---/agentspec

    """
    return 0
