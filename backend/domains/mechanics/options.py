"""Request-local mechanics options without changing shared circuit orchestration."""


class MechanicsOptions:
    def __init__(self, domain, options):
        self.domain = domain
        self.options = dict(options)
        self.name = domain.name
        self.stages = domain.stages

    def analyze(self, image, options, progress):
        return self.domain.analyze(image, {**options, **self.options}, progress)
