from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('voteit.printable')


def includeme(config):
    config.include('.views')
