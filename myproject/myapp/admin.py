# myapp/admin.py
from django.contrib import admin
from .models import SkillProfile, ExchangeRequest, Chat, Review, Job, Skill

admin.site.register(SkillProfile)
admin.site.register(ExchangeRequest)
admin.site.register(Chat)



@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'reviewed', 'rating', 'created_at')
    search_fields = ('reviewer__username', 'reviewed__username', 'comment')
    
    
from django.contrib import admin
from .models import Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'created_at')
    search_fields = ('title', 'company', 'location')
    
    
    
from django.contrib import admin
from .models import Skill

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', 'description')
    
