__author__ = 'Tonakai'

from PManager.models import ObjectTags, Specialty
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User


def get_user_quality_for_task(task, user_id):
    task_tags_rel = ObjectTags.objects.filter(object_id=task.id,
                                              content_type=ContentType.objects.get_for_model(task))

    tag_ids = [str(tagRel.tag.id) for tagRel in task_tags_rel]

    user_tag_sums = dict()
    if len(tag_ids) > 0:
        for obj1 in ObjectTags.get_weights(tag_ids, ContentType.objects.get_for_model(User).id):
            if obj1.content_object:
                user_tag_sums[str(obj1.content_object.id)] = int(obj1.weight_sum)

        min_tag_count, max_tag_count = False, 0

        for user_id in user_tag_sums:
            if max_tag_count < user_tag_sums[user_id]:
                max_tag_count = user_tag_sums[user_id]
            if min_tag_count > user_tag_sums[user_id] or not min_tag_count:
                min_tag_count = user_tag_sums[user_id]

        if max_tag_count > 0:
            for user_id in user_tag_sums:
                if min_tag_count == max_tag_count:
                    user_tag_sums[user_id] = 1 if user_tag_sums[user_id] == min_tag_count else 0
                else:
                    user_tag_sums[user_id] = float((int(user_tag_sums[user_id]) - int(min_tag_count))) / float(
                        (int(max_tag_count) - int(min_tag_count)))
        return user_tag_sums[user_id] if user_id in user_tag_sums else 0
    return 0


def get_user_rating_for_task(task, user):
    assert user.id > 0

    user_tag_sums = dict()
    task_tags_rel = ObjectTags.objects.filter(object_id=task.id,
                                              content_type=ContentType.objects.get_for_model(task))

    tag_ids = [str(tagRel.tag.id) for tagRel in task_tags_rel]

    if len(tag_ids) > 0:
        for obj1 in ObjectTags.get_weights(tag_ids,
                                           ContentType.objects.get_for_model(User).id, user.id):
            if obj1.content_object:
                user_tag_sums[str(obj1.content_object.id)] = int(obj1.weight_sum)

        return user_tag_sums.get(str(user.id), 0)
    return 0


def get_top_users(task, limit=5, user_filter=None):
    assert task is not None
    assert limit >= 0
    if user_filter:
        user_filter = user_filter.values_list('id', flat=True)
    else:
        user_filter = []
    user_tag_sums = dict()
    task_tags_rel = ObjectTags.objects.filter(object_id=task.id,
                                              content_type=ContentType.objects.get_for_model(task))

    tag_ids = [str(tag_rel.tag.id) for tag_rel in task_tags_rel]

    if len(tag_ids) > 0:
        related_users = ObjectTags.get_weights(tag_ids, ContentType.objects.get_for_model(User).id,
                                               filter_content=user_filter, order_by=('weight_sum', 'DESC'),
                                               limit=limit)
        for obj1 in related_users:
            if obj1.content_object:
                user_tag_sums[str(obj1.content_object.id)] = int(obj1.weight_sum)

    return user_tag_sums


def get_user_quality(arTagsId, userId):
    userTagSums = {}
    if not arTagsId: return []
    sql = 'SELECT SUM(`weight`) as weight_sum, `id`, `object_id`, `content_type_id`' + \
                                       ' from PManager_objecttags WHERE' + \
                                       ' tag_id in (' + ', '.join(str(v) for v in arTagsId) + ')' + \
                                       ' AND content_type_id=\'' + \
                                        str(ContentType.objects.get_for_model(User).id) + \
                                        '\' AND object_id=\'' + \
                                        str(userId) + '\' GROUP BY `tag_id`'

    for obj in ObjectTags.objects.raw(sql):
        userTagSums[obj.tag_id] = int(obj.weight_sum)

    return userTagSums
