from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Empresa, Tinket, Promocion, Avance

# Register your models here.
class EmpresaAdmin(admin.ModelAdmin):
    pass

class TinketAdmin(admin.ModelAdmin):
    pass

class PromocionAdmin(admin.ModelAdmin):
    pass

class AvanceAdmin(admin.ModelAdmin):
    pass

admin.site.register(Avance, AvanceAdmin)
admin.site.register(Tinket, TinketAdmin)
admin.site.register(Empresa, EmpresaAdmin)
admin.site.register(Usuario, UserAdmin)
