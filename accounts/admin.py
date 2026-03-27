from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # एडमिन प्यानलको लिस्टमा देखिने कोलमहरू
    list_display = ('username', 'email', 'role', 'is_active', 'date_joined')
    
    # साइडबारमा फिल्टर गर्ने अप्सन
    list_filter = ('role', 'is_staff', 'is_active')
    
    # युजरनेम र ईमेलबाट खोज्न मिल्ने
    search_fields = ('username', 'email')
    
    # नयाँ युजर थप्दा वा एसाइन गर्दा रोल छान्ने सुबिधा
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Info', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Extra Info', {'fields': ('role',)}),
    )

    # विशेष गरी 'STUDENT' हरू मात्र फिल्टर गरेर हेर्न एउटा custom display नाम दिन सकिन्छ