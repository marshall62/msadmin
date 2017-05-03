from django.contrib import admin
from .models import *

# Register your models here.
# This defines the admin page structures.

# Intervention Selector Params shows the id but it isn't editable
# class ISParamAdmin(admin.ModelAdmin):
#
#     def get_readonly_fields(self, request, obj=None):
#         return self.readonly_fields + ('id',)
#
# admin.site.register(InterventionSelectorParam,ISParamAdmin)

# Note:  Many-to-many relationships involve a third "mapping" table which contains the id of table-1 and id of table-2.
#  To get the correct set-up look at the StrategyComponent in models.py.  It has many-to-many with sc_param and interventionSelector

# The below sets up the ability to include the intervention selectors in the admin form
# that edits the StrategyComponent. Add some controls to the InterventionSelector form to allow editing the
# StrategyComponents, see https://docs.djangoproject.com/en/dev/ref/contrib/admin/#working-with-many-to-many-intermediary-models
class SCISMapInline(admin.TabularInline):
    model = SCISMap
    extra = 1
    unique_together = (("strategyComponent", "interventionSelector"),)


# sets up many-to-many from strategyComponent to sc_param through sc_param_map
class SCParamMapInLine(admin.TabularInline):
    model = SCParamMap
    extra = 1


# StrategyComponents have 2 in-line editors: one for interventionSelectors (thru SCISMapInLine) and
# one for StrategyComponentParams (thru SCParamMapInLine)
class StrategyComponentAdmin(admin.ModelAdmin):
    inlines = [
        SCISMapInline, SCParamMapInLine
    ]

    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields + ('id',)


admin.site.register(StrategyComponent, StrategyComponentAdmin)

# The below sets up the ability to include the parameters (InterventionSelectorParam) of an intervention selector in the admin form
# that edits the InterventionSelector
# class ISParamInline(admin.TabularInline):
#     model = InterventionSelectorParam
#     fields = ('name', 'value')


# An intervention selector param that is connected to the SCISMap
class ISParamInline(admin.TabularInline):
    model = InterventionSelectorParam
    fields = ('name', 'value')

# Defines an inline viewer for use in intervention selector so that it will display the strategy component but not allow
# editing of it
class SCISMapInline_ReadOnly(admin.TabularInline):
    model = SCISMap
    extra = 1
    can_delete = False
    unique_together = (("strategyComponent", "interventionSelector"),)
    # readonly_fields = ('name',)

    # Remove ability to add/delete the rows
    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

# Intervention Selectors have two inline editors for the tables is_param and strategyComponent.
# This second one is somewhat dubious but would allow someone to quickly see where a particular intervention is used.   I'd like to remove
# the ability to edit it though; would prefer read-only
class InterventionSelectorAdmin(admin.ModelAdmin):
    inlines = [
        # ISParamInline, SCISMapInline_ReadOnly
         SCISMapInline_ReadOnly
    ]
    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields + ('id',)


admin.site.register(InterventionSelector, InterventionSelectorAdmin)





#
class StrategyComponentParamAdmin (admin.ModelAdmin):
    #  This would give us pulldown menus on the StrategyComponentParams to see the StrategyComponent they go to
    # inlines=[
    #     SCParamMapInLine,
    # ]
    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields + ('id',)

admin.site.register(StrategyComponentParam,StrategyComponentParamAdmin)

# The admin form for the SCISMap shows the pairing of SC and IS.  This is the place to set each IS's params (because
# the params for each IS depend on the SC).  So we include an inline tabular in the form so it can include the is_param table.
class SCISMapAdmin (admin.ModelAdmin):
    inlines = [ISParamInline]


# Defines an inline viewer for use in intervention selector so that it will display the strategy component but not allow
# editing of it
class ClassSCParam_Inline(admin.TabularInline):
    model = ClassSCParam
    extra = 1


# This is a partial solution to a problem with the admin editors for the various classXXX forms.   I don't want users creating new classes.
# This turns off all ability to create Classes from forms that ref the class table as  a foreign key.  The problem with this solution
# is that I can't even create a class from top level.
class ClassAdmin (admin.ModelAdmin):
    def has_add_permission (self, req):
        return False
    def has_change_permission (self, req, obj=None):
        return False

# class ClassSCParamAdmin (admin.ModelAdmin):
#     inlines = [  ClassSCParam_Inline    ]

class ClassSCISMapAdmin (admin.ModelAdmin):
    model = ClassSCISMap

class ClassISParamAdmin (admin.ModelAdmin):
    model = ClassISParam

admin.site.register(SCISMap,SCISMapAdmin)

admin.site.register(ClassSCParam)
admin.site.register(ClassISParam, ClassISParamAdmin)
admin.site.register(ClassSCISMap,ClassSCISMapAdmin)
admin.site.register(Class,ClassAdmin)

admin.site.register(InterventionSelectorParam)
admin.site.register(Strategy)
