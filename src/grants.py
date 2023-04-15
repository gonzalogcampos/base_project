import hashlib

import log as Log
from db import Database

DATABASE = Database()
USERS_TABLE = 'users'
GROUPS_TABLE = 'user_groups'
USER = None
SALT = "29fwD78qx"


def signin(user, password):
    if DATABASE.get_by_id(USERS_TABLE, user):
        Log.warning("User {} already exists.".format(user))
        return False

    hashed = hashlib.md5((str(password)+SALT).encode()).hexdigest()
    result = DATABASE.add_item(USERS_TABLE, {'password': hashed}, id=user)
    if result:
        DATABASE.save()
    return result


def login(user, password):
    user_data = DATABASE.get_by_id(USERS_TABLE, user)
    if not user_data:
        Log.warning("Wrong user {}.".format(user))
        return False

    hashed = hashlib.md5((str(password)+SALT).encode()).hexdigest()
    if user_data.get('password') == hashed:
        global USER
        Log.info("User logged {}.".format(user))
        USER = user
        return True

    Log.warning("Login {} with wrong password.".format(user))
    return False


def logout():
    global USER
    USER = None


def get_user():
    return USER


def get_groups():
    DATABASE.find(GROUPS_TABLE, [get_user in 'users']).keys()


def change_password(current_password, new_password):
    if not USER:
        Log.warning("For changing the password login first.")
        return False

    user_data = DATABASE.get_by_id(USERS_TABLE, USER)
    if not user_data:
        Log.warning("Wrong user {}".format(USER))

    hashed = hashlib.md5((str(current_password)+SALT).encode()).hexdigest()
    if user_data.get('password') == hashed:
        Log.info("Changing password of user {}.".format(USER))
        user_data['password'] = hashlib.md5((str(new_password)+SALT).encode()).hexdigest()
        DATABASE.set_item(USERS_TABLE, USER, user_data)
        DATABASE.save()

    Log.warning("Wrong password.")
    return False


def check_grants(func):
    def wrapper_func(*args, **kwargs):
        user = get_user()
        func_name = func.__name__
        if func_name not in (DATABASE.get_by_id(USERS_TABLE, user) or {}).get('grants', []) and user!='admin':
            Log.error("No grants for user {} to do {}".format(user, func_name))
        else:
            func(*args, **kwargs)

    return wrapper_func


@check_grants
def delete_user(user):
    DATABASE.rem_item(USERS_TABLE, user)
    DATABASE.save()


@check_grants
def create_group(group):
    DATABASE.add_item(GROUPS_TABLE, {'users': []}, id=group)
    DATABASE.save()


@check_grants
def delete_group(group):
    DATABASE.rem_item(GROUPS_TABLE, group)
    DATABASE.save()


@check_grants
def add_users_to_group(group, users):
    group_value = DATABASE.get_by_id(GROUPS_TABLE, group)
    if not group_value:
        Log.error("Group {} does not exit.".format(group))

    Log.info("Adding {} to group {}.".format(users, group))
    group_value['users'] = list(set(group_value.get('users', []) + users))
    DATABASE.set_item(GROUPS_TABLE, group, group_value)
    DATABASE.save()

def remove_users_from_group(group, users):
    group_value = DATABASE.get_by_id(GROUPS_TABLE, group)
    if not group_value:
        Log.error("Group {} does not exit.".format(group))

    Log.info("Adding {} to group {}.".format(users, group))
    group_value['users'] = list(set(group_value.get('users', [])) - set(users))


@check_grants
def add_grants(actions=None, users=None, groups=None):
    actions = actions or []
    users = users or []
    groups = groups or []
    Log.info("Adding grants to users: {} and groups: {} to do {}".format(users, groups, actions))
    for user in users:
        user_data = DATABASE.get_by_id(USERS_TABLE, user)
        if not user_data:
            Log.warning("User {} not found.".format(user))
        if 'grants' not in user_data:
            user_data['grants'] = []
        user_data['grants'] += actions
        user_data['grants'] = list(set(user_data['grants']))
        DATABASE.set_item(USERS_TABLE, user, user_data)

    for group in groups:
        group_data = DATABASE.get_by_id(GROUPS_TABLE, group)
        if not group_data:
            Log.warning("Group {} not found.".format(group))
        if 'grants' not in group_data:
            group_data['grants'] = []
        group_data['grants'] += actions
        group_data['grants'] = list(set(group_data['grants']))
        DATABASE.set_item(GROUPS_TABLE, group, group_data)

    DATABASE.save()


@check_grants
def revoke_grants(actions=None, users=None, groups=None):
    actions = set(actions or [])
    users = users or []
    groups = groups or []
    Log.info("Revoking grants to users: {} and groups: {} to do {}".format(users, groups, actions))
    for user in users:
        user_data = DATABASE.get_by_id(USERS_TABLE, user)
        if not user_data:
            Log.warning("User {} not found.".format(user))
        if 'grants' not in user_data:
            user_data['grants'] = []
        user_data['grants'] = list(set(user_data['grants']) - actions)
        DATABASE.set_item(USERS_TABLE, user, user_data)

    for group in groups:
        group_data = DATABASE.get_by_id(GROUPS_TABLE, group)
        if not group_data:
            Log.warning("Group {} not found.".format(group))
        if 'grants' not in group_data:
            group_data['grants'] = []
        group_data['grants'] = list(set(group_data['grants']) - actions)
        DATABASE.set_item(GROUPS_TABLE, group, group_data)

    DATABASE.save()

if __name__ == '__main__':
    Log.debug('User: {}'.format(get_user()))
    signin('user1', None)
    Log.debug('User: {}'.format(get_user()))
    login('user1', 'wrong_password')
    Log.debug('User: {}'.format(get_user()))
    login('user1', None)
    Log.debug('User: {}'.format(get_user()))
    logout()
    Log.debug('User: {}'.format(get_user()))

    signin('admin', '00000')
    login('admin', '00000')
    add_grants(actions=['add_grants', 'revoke_grants'], users=['admin', 'user1'])
    revoke_grants(actions=['revoke_grants'], users=['user1'])
    delete_group('mantainers')
    create_group('mantainers')
    add_users_to_group('mantainers', ['user1'])
    add_grants(actions=['create_group', 'add_users_to_group'], groups=['mantainers'])
    logout()
