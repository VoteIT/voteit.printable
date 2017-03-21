from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('voteit.printable')


def includeme(config):
    config.add_translation_dirs('voteit.printable:locale/')
    config.include('.models')
    config.include('.schemas')
    config.include('.views')
