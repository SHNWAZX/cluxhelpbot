# ============================================================
# handlers/__init__.py — Master handler registration
# ============================================================
from handlers.start          import register_start
from handlers.group_commands import register_group_commands
from handlers.notes          import register_notes
from handlers.rules          import register_rules
from handlers.blacklist      import register_blacklist
from handlers.afk            import register_afk
from handlers.antiflood      import register_antiflood
from handlers.userinfo       import register_userinfo
from handlers.misc           import register_misc


def register_all_handlers(app):
    register_start(app)
    register_group_commands(app)
    register_notes(app)
    register_rules(app)
    register_blacklist(app)
    register_afk(app)
    register_antiflood(app)
    register_userinfo(app)
    register_misc(app)
    print("✅ All handlers registered!")
