# notificaciones/admin.py
from django.contrib import admin
from .models import Personas, Resoluciones, Cargos, Procesos_Vinculacion

# Para que la vista de Procesos sea más útil
class ProcesoVinculacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'persona', 'cargo', 'tipo_proceso', 'estado_proceso', 'fecha_comunicacion')
    list_filter = ('estado_proceso', 'tipo_proceso', 'cargo')
    search_fields = ('persona__nombre_completo', 'persona__cedula', 'resolucion__numero_resolucion', 'cargo__nombre_cargo')
    # Añade los campos de solo lectura que se llenan automáticamente
    readonly_fields = ('fecha_comunicacion', 'fecha_aceptacion', 'fecha_solicitud_examenes', 'fecha_citacion_posesion')
    # Organiza el formulario de edición
    fieldsets = (
        ('Información Central', {
            'fields': ('persona', 'resolucion', 'cargo', 'tipo_proceso', 'estado_proceso')
        }),
        ('Seguimiento y Fechas (Términos)', {
            'fields': ('fecha_comunicacion', 'fecha_maxima_aceptacion', 'fecha_aceptacion', 
                       'fecha_maxima_posesion', 'fecha_solicitud_examenes', 'fecha_citacion_posesion')
        }),
        ('Detalles Adicionales', {
            'fields': ('numero_th', 'email_documentacion_destino', 'documentos_completos')
        }),
    )

class PersonaAdmin(admin.ModelAdmin):
    search_fields = ('nombre_completo', 'cedula', 'email_personal')
    list_display = ('cedula', 'nombre_completo', 'email_personal', 'es_funcionario_antiguo')

class CargoAdmin(admin.ModelAdmin):
    search_fields = ('opep_numero', 'nombre_cargo')
    list_display = ('opep_numero', 'nombre_cargo')

class ResolucionAdmin(admin.ModelAdmin):
    search_fields = ('numero_resolucion',)
    list_display = ('numero_resolucion', 'fecha_resolucion', 'fecha_publicacion')

# Registra los modelos en el admin
admin.site.register(Personas, PersonaAdmin)
admin.site.register(Resoluciones, ResolucionAdmin)
admin.site.register(Cargos, CargoAdmin)
admin.site.register(Procesos_Vinculacion, ProcesoVinculacionAdmin)