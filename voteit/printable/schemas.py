import colander

from voteit.core import _

# @colander.deferred
# def selectable_agenda_items(node, kw):
#     pass
# 
# @colander.deferred
# def all_agenda_items_keys(node, kw):
#     pass
# 
# class PrintableMeetingSchema(colander.Schema):
#     title = _("Print meeting")
# 
#     agenda_items = colander.SchemaNode(colander.Set(),
#                                        widget = selectable_agenda_items,
#                                        default = )