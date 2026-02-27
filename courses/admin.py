from django.contrib import admin

# Register your models here.
from .models import * 
# admin.site.register(Course)

class CourseAdmin(admin.ModelAdmin):
    list_display = ('id','title','description')
admin.site.register(Course,CourseAdmin)

class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id','title')
admin.site.register(Subject,SubjectAdmin)

class UnitAdmin(admin.ModelAdmin):
    list_display = ('id','title')
admin.site.register(Unit,UnitAdmin)


class TopicAdmin(admin.ModelAdmin):
    list_display = ('id','title')
admin.site.register(Topic,TopicAdmin)

# admin.site.register(Topic)
