from django.db import models


class Hierarchy(models.Model):
    protein_id = models.CharField(max_length=9, primary_key=True, unique=True)

# class Class(models.Model):
#     protein_class = models.IntegerField(primary_key=True, unique=True)
#     class_description = models.CharField(max_length=300)
#
#
# class Architecture(models.Model):
#     protein_architecture = models.IntegerField(primary_key=True, unique=True)
#     _description = models.CharField(max_length=300)
#
#
# class TopologyFold(models.Model):
#     protein_topology_fold = models.IntegerField(primary_key=True, unique=True)
#     topology_fold_description = models.CharField(max_length=300)
#
#
# class HomologySuperFamily(models.Model):
#     protein_homology_sf = models.IntegerField(primary_key=True, unique=True)
#     homology_sf_description = models.CharField(max_length=300)


class AllProteins(models.Model):
    protein_id = models.ForeignKey(Hierarchy, on_delete=models.CASCADE, related_name='details')
    protein_key = models.IntegerField()
    key_occurrence = models.IntegerField(null=True)
    aacd0 = models.CharField(max_length=3)
    position0 = models.IntegerField()
    aacd1 = models.CharField(max_length=3)
    position1 = models.IntegerField()
    aacd2 = models.CharField(max_length=3)
    position2 = models.IntegerField()
    classT1 = models.IntegerField()
    theta = models.FloatField()
    classL1 = models.IntegerField()
    maxDist = models.FloatField()
    x0 = models.FloatField()
    y0 = models.FloatField()
    z0 = models.FloatField()
    x1 = models.FloatField()
    y1 = models.FloatField()
    z1 = models.FloatField()
    x2 = models.FloatField()
    y2 = models.FloatField()
    z2 = models.FloatField()

    # class Meta:
    #     index_together = ['protein_id', 'protein_key']


class Comparison(models.Model):
    protein_one = models.ForeignKey(Hierarchy, on_delete=models.CASCADE, related_name="comparison_one")
    protein_two = models.ForeignKey(Hierarchy, on_delete=models.CASCADE, related_name="comparison_two")
    similarity_value = models.FloatField()

# class Position(models.Model):
#     protein_id = models.ForeignKey(
#         Hierarchy,
#         on_delete=models.CASCADE)
#     amino_acid_name = models.CharField(max_length=20)
#     seq_id = models.CharField(max_length=5, null=True)
#     x_coord = models.FloatField(default=0.0)
#     y_coord = models.FloatField(default=0.0)
#     z_coord = models.FloatField(default=0.0)
