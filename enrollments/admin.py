from django.contrib import admin
from .models import Enrollment

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    # इनरोलमेन्टको जानकारीहरू कोलममा देखाउन
    list_display = ('user', 'course', 'is_trial', 'start_date', 'expiry_date', 'is_active', 'get_status')
    
    # सक्रिय छ कि छैन, ट्रायल हो कि होइन र कुन कोर्स हो भनेर फिल्टर गर्न
    list_filter = ('is_active', 'is_trial', 'course', 'start_date')
    
    # विद्यार्थीको नाम वा कोर्सको नामबाट खोज्न
    search_fields = ('user__username', 'user__email', 'course__title')
    
    # मितिहरू आफैं नचलाउनु होला (Expiry date save method ले मिलाउँछ)
    readonly_fields = ('start_date',)

    # सप्तरंगी स्टेटस देखाउन एउटा सानो फंक्सन (वैकल्पिक)
    def get_status(self, obj):
        from django.utils import timezone
        if obj.expiry_date < timezone.now():
            return "Expired"
        return "Active"
    get_status.short_description = "Validity Status"