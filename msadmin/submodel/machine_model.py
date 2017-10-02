from django.db import models

class Part (models.Model):
    name = models.CharField(max_length=45)

    class Meta:
        db_table = "part"

    def __str__ (self):
        return self.name

class Owner (models.Model):
    name = models.CharField(max_length=45)

    class Meta:
        db_table = "owner"

    def __str__ (self):
        return self.name

class Machine (models.Model):
    name = models.CharField(max_length=45)
    parts = models.ManyToManyField(Part, through='Machine2Part')
    owner = models.ManyToManyField(Owner, through='Machine2Owner')
    class Meta:
        db_table = "machine"

    def __str__ (self):
        return self.name


class Machine2Part (models.Model):
    machine = models.ForeignKey(Machine,db_column='machineId')
    part = models.ForeignKey(Part,db_column='partId')
    class Meta:
        db_table = "machine2part"

class Machine2Owner (models.Model):
    machine = models.ForeignKey(Machine,db_column='machineId')
    owner = models.ForeignKey(Owner,db_column='ownerId')
    class Meta:
        db_table = "machine2owner"