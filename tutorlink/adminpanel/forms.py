from accounts.forms import UserProfileForm


class AdminUserForm(UserProfileForm):
    class Meta(UserProfileForm.Meta):
        fields = UserProfileForm.Meta.fields + ['is_active']
