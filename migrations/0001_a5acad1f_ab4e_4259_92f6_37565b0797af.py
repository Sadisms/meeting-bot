"""
a5acad1f_ab4e_4259_92f6_37565b0797af
date created: 2022-09-28 05:39:50.176191
"""


def upgrade(migrator):
    with migrator.create_table('oauth_cache') as table:
        table.primary_key('id')
        table.char('user_id')
        table.char('state', null=True)
        table.text('slack_token', null=True)

    with migrator.create_table('meet_user_credentials') as table:
        table.primary_key('id')
        table.char('user_id')
        table.binary('credentials', null=True)


def downgrade(migrator):
    migrator.drop_table('oauth_cache')
    migrator.drop_table('meet_user_credentials')
