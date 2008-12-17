from django.views.generic import list_detail

# Display views

def usergroup_list(request):
    pass

def usergroup_detail(request, usergroup_slug):
    pass

# Create, edit delete views

def create_usergroup(request):
    pass

def edit_usergroup(request, usergroup_slug):
    pass

def delete_usergroup(request, usergroup_slug):
    pass

# Group administration views

def add_usergroup_admin(request, usergroup_slug, user_id):
    pass

def delete_usergroup_admin(request, usergroup_slug, user_id):
    pass

# Invitation/application views

def send_group_invitation(request, usergroup_slug, user_id):
    pass

def accept_group_invitation(request, usergroup_slug, secret_key):
    pass

def apply_to_join_group(request, usergroup_slug):
    pass