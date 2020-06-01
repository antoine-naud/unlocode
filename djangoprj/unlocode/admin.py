from django.contrib import admin

from .models import Unlocode


class UnlocodeAdmin(admin.ModelAdmin):
    fields = ('locode', 'namewodiacritics', 'functions',)
    list_display = ('id', 'locode', 'name', 'namewodiacritics', 'subdiv', 'functions', 'status', 'date', 'iata')

    class Meta:
        ordering = ['locode']


admin.site.register(Unlocode, UnlocodeAdmin)
