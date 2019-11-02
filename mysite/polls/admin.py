from django.contrib import admin

from .models import Question, Choice


# class QuestionAdmin(admin.ModelAdmin):
#     fields = ['pub_date', 'question_text']

# class ChoiceInline(admin.StackedInline):
#     model = Choice
#     extra = 3

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3

# class QuestionAdmin(admin.ModelAdmin):
#     fieldsets = [
#         (None,                  {'fields': ['question_text']}),
#         ('Date information',    {'fields': ['pub_date']}),
#     ]

class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,                  {'fields': ['question_text']}),
        ('Date information',    {'fields': ['pub_date']}),
    ]
    inlines = [ChoiceInline]

admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
