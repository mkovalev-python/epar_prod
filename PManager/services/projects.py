__author__ = 'rayleigh'
from PManager.models.tasks import PM_Project


def get_project_by_id(project_id):
    if project_id is None:
        return None
    try:
        project = PM_Project.objects.get(pk=int(project_id))
        return project
    except ValueError:
        return None
    except TypeError:
        return None
    except PM_Project.DoesNotExist:
        return None
