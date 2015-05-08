from fanstatic import Library
from fanstatic import Resource
from voteit.core.fanstaticlib import voteit_main_css

library = Library('voteit_printable', 'static')

printable_css = Resource(library, 'print.css', depends = (voteit_main_css,))
