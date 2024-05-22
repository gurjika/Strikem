from django.contrib import admin
from . import models
# Register your models here.


admin.site.register(models.Invitation)
admin.site.register(models.Reservation)
admin.site.register(models.Player)
admin.site.register(models.GameSession)
admin.site.register(models.Matchup)
admin.site.register(models.Message)
admin.site.register(models.PoolTable)
admin.site.register(models.PoolHouse)



