from django.contrib import admin
from .models import User, StudentProfile, Profession, MentorProfile, TestResults

class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'user_type', 'is_admin')
    search_fields = ('email', 'username')
    readonly_fields = ('date_joined',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Permissions', {'fields': ('is_admin', 'is_staff', 'is_active', 'is_superuser')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )

    ordering = ('email',)

admin.site.register(User, UserAdmin)
admin.site.register(StudentProfile)
admin.site.register(TestResults)
admin.site.register(Profession)
admin.site.register(MentorProfile)