from pyramid.threadlocal import get_current_registry


def add_printable_view(config, view_cls, name):
    if not hasattr(config.registry, '_voteit_printable_views'):
        config.registry._voteit_printable_views = {}
    config.registry._voteit_printable_views[name] = view_cls


def get_printable_views(registry=None):
    if registry is None:
        registry = get_current_registry()
    return dict(registry._voteit_printable_views)


def includeme(config):
    config.add_directive('add_printable_view', add_printable_view)
