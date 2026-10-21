from django.db import DatabaseError


def get_admin_course(message):
    """Return the active Admin course matching a user's message."""
    from .models import Course
    from .knowledge import match_course_id, match_course_name

    course_id = match_course_id(message)
    if not course_id:
        return None

    course_name = match_course_name(course_id)
    if not course_name:
        return None

    try:
        courses = Course.objects.filter(is_active=True)
        target = " ".join(course_name.lower().split())

        for course in courses:
            name = " ".join(course.name.lower().split())
            if name == target:
                return course
    except DatabaseError:
        return None

    return None
