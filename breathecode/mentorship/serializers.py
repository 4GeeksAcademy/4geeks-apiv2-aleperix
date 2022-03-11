import serpy, re, math
from breathecode.utils import ValidationException
from .models import MentorshipSession, MentorshipService, MentorProfile, MentorshipBill
from breathecode.admissions.models import Academy
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from breathecode.utils.datetime_interger import duration_to_str


class GetAcademySmallSerializer(serpy.Serializer):
    id = serpy.Field()
    slug = serpy.Field()
    name = serpy.Field()
    logo_url = serpy.Field()
    icon_url = serpy.Field()


class ProfileSerializer(serpy.Serializer):
    """The serializer schema definition."""
    # Use a Field subclass like IntField if you need more validation.
    avatar_url = serpy.Field()
    github_username = serpy.Field()


class GetSyllabusSmallSerializer(serpy.Serializer):
    """The serializer schema definition."""
    # Use a Field subclass like IntField if you need more validation.
    id = serpy.Field()
    slug = serpy.Field()
    name = serpy.Field()
    logo = serpy.Field()


class GetUserSmallSerializer(serpy.Serializer):
    id = serpy.Field()
    first_name = serpy.Field()
    last_name = serpy.Field()
    email = serpy.Field()
    profile = ProfileSerializer(required=False)


class GETServiceSmallSerializer(serpy.Serializer):
    id = serpy.Field()
    slug = serpy.Field()
    name = serpy.Field()
    status = serpy.Field()


class GETMentorTinyerializer(serpy.Serializer):
    id = serpy.Field()
    slug = serpy.Field()
    user = GetUserSmallSerializer()


class GETMentorTinySerializer(serpy.Serializer):
    id = serpy.Field()
    slug = serpy.Field()
    user = GetUserSmallSerializer()
    service = GETServiceSmallSerializer()
    status = serpy.Field()
    booking_url = serpy.Field()


class GETSessionSmallSerializer(serpy.Serializer):
    id = serpy.Field()
    status = serpy.Field()
    mentor = GETMentorTinySerializer()
    mentee = GetUserSmallSerializer(required=False)
    started_at = serpy.Field()
    ended_at = serpy.Field()
    mentor_joined_at = serpy.Field()
    mentor_left_at = serpy.Field()
    mentee_left_at = serpy.Field()
    accounted_duration = serpy.Field()
    summary = serpy.Field()


class GETServiceBigSerializer(serpy.Serializer):
    id = serpy.Field()
    slug = serpy.Field()
    name = serpy.Field()
    status = serpy.Field()
    academy = GetAcademySmallSerializer()
    logo_url = serpy.Field()
    description = serpy.Field()
    duration = serpy.Field()
    language = serpy.Field()
    allow_mentee_to_extend = serpy.Field()
    allow_mentors_to_extend = serpy.Field()
    created_at = serpy.Field()
    updated_at = serpy.Field()


class GETServiceSmallSerializer(serpy.Serializer):
    id = serpy.Field()
    slug = serpy.Field()
    name = serpy.Field()
    status = serpy.Field()
    academy = GetAcademySmallSerializer()
    logo_url = serpy.Field()
    description = serpy.Field()
    duration = serpy.Field()
    language = serpy.Field()
    allow_mentee_to_extend = serpy.Field()
    allow_mentors_to_extend = serpy.Field()
    created_at = serpy.Field()
    updated_at = serpy.Field()


class GETMentorSmallSerializer(serpy.Serializer):
    id = serpy.Field()
    slug = serpy.Field()
    user = GetUserSmallSerializer()
    service = GETServiceSmallSerializer()
    status = serpy.Field()
    price_per_hour = serpy.Field()
    booking_url = serpy.Field()
    timezone = serpy.Field()
    email = serpy.Field()
    created_at = serpy.Field()
    updated_at = serpy.Field()


class GETBillSmallSerializer(serpy.Serializer):
    """The serializer schema definition."""
    # Use a Field subclass like IntField if you need more validation.
    id = serpy.Field()
    status = serpy.Field()
    total_duration_in_minutes = serpy.Field()
    total_duration_in_hours = serpy.Field()
    total_price = serpy.Field()
    overtime_minutes = serpy.Field()
    paid_at = serpy.Field()
    created_at = serpy.Field()

    mentor = GETMentorTinyerializer()
    reviewer = GetUserSmallSerializer(required=False)


class BigBillSerializer(serpy.Serializer):
    """The serializer schema definition."""
    # Use a Field subclass like IntField if you need more validation.
    id = serpy.Field()
    status = serpy.Field()
    total_duration_in_minutes = serpy.Field()
    total_duration_in_hours = serpy.Field()
    total_price = serpy.Field()
    overtime_minutes = serpy.Field()
    overtime_hours = serpy.MethodField()
    paid_at = serpy.Field()
    sessions = serpy.MethodField()
    public_url = serpy.MethodField()
    created_at = serpy.Field()
    academy = GetAcademySmallSerializer(required=False)

    mentor = GETMentorSmallSerializer()
    reviewer = GetUserSmallSerializer(required=False)

    def get_overtime_hours(self, obj):
        return round(obj.overtime_minutes / 60, 2)

    def get_sessions(self, obj):
        _sessions = obj.mentorshipsession_set.order_by('created_at').all()
        print('session', _sessions)
        return BillSessionSmallSerializer(_sessions, many=True).data

    def get_public_url(self, obj):
        return '/v1/mentorship/academy/bill/1/html'


class GETMentorBigSerializer(serpy.Serializer):
    id = serpy.Field()
    slug = serpy.Field()
    user = GetUserSmallSerializer()
    service = GETServiceBigSerializer()
    status = serpy.Field()
    price_per_hour = serpy.Field()
    booking_url = serpy.Field()
    timezone = serpy.Field()
    syllabus = serpy.MethodField()
    email = serpy.Field()
    created_at = serpy.Field()
    updated_at = serpy.Field()

    def get_syllabus(self, obj):
        return map(lambda s: s.slug, obj.syllabus.all())


class GETSessionReportSerializer(serpy.Serializer):
    id = serpy.Field()
    status = serpy.Field()
    started_at = serpy.Field()
    ended_at = serpy.Field()
    starts_at = serpy.Field()
    ends_at = serpy.Field()
    mentor_joined_at = serpy.Field()
    mentor_left_at = serpy.Field()
    mentee_left_at = serpy.Field()
    accounted_duration = serpy.Field()
    mentor = GETMentorBigSerializer()
    mentee = GetUserSmallSerializer(required=False)


class GETSessionBigSerializer(serpy.Serializer):
    id = serpy.Field()
    name = serpy.Field()
    status = serpy.Field()
    mentor = GETMentorSmallSerializer()
    mentee = GetUserSmallSerializer(required=False)
    latitude = serpy.Field()
    longitude = serpy.Field()
    is_online = serpy.Field()
    online_meeting_url = serpy.Field()
    online_recording_url = serpy.Field()
    agenda = serpy.Field()
    summary = serpy.Field()
    started_at = serpy.Field()
    accounted_duration = serpy.Field()
    ended_at = serpy.Field()
    created_at = serpy.Field()


class BillSessionSmallSerializer(serpy.Serializer):
    id = serpy.Field()
    status = serpy.Field()
    status_message = serpy.Field()
    mentor = GETMentorSmallSerializer()
    mentee = GetUserSmallSerializer(required=False)
    started_at = serpy.Field()
    ended_at = serpy.Field()
    mentor_joined_at = serpy.Field()
    mentor_left_at = serpy.Field()
    mentee_left_at = serpy.Field()
    summary = serpy.Field()
    accounted_duration = serpy.Field()

    tooltip = serpy.MethodField()
    duration_string = serpy.MethodField()
    billed_str = serpy.MethodField()
    extra_time = serpy.MethodField()
    mentor_late = serpy.MethodField()
    mente_joined = serpy.MethodField()

    def get_tooltip(self, obj):

        message = f'This mentorship should last no longer than {int(obj.mentor.service.duration.seconds/60)} min. <br />'
        if obj.started_at is None:
            message += 'The mentee never joined the session. <br />'
        else:
            message += f'Started on {obj.started_at.strftime("%m/%d/%Y at %H:%M:%S")}. <br />'
            if obj.mentor_joined_at is None:
                message += f'The mentor never joined'
            elif obj.mentor_joined_at > obj.started_at:
                message += f'The mentor joined {duration_to_str(obj.mentor_joined_at - obj.started_at)} before. <br />'
            elif obj.started_at > obj.mentor_joined_at:
                message += f'The mentor joined {duration_to_str(obj.started_at - obj.mentor_joined_at)} after. <br />'

            if obj.ended_at is not None:
                message += f'The mentorship lasted {duration_to_str(obj.ended_at - obj.started_at)}. <br />'
                if (obj.ended_at - obj.started_at) > obj.mentor.service.duration:
                    extra_time = (obj.ended_at - obj.started_at) - obj.mentor.service.duration
                    message += f'With extra time of {duration_to_str(extra_time)}. <br />'
                else:
                    message += f'No extra time detected <br />'
            else:
                message += f'The mentorship has not ended yet. <br />'
                if obj.ends_at is not None:
                    message += f'But it was supposed to end after {duration_to_str(obj.ends_at - obj.started_at)} <br />'

        return message

    def get_duration_string(self, obj):

        if obj.started_at is None:
            return 'Never started'

        end_date = obj.ended_at
        if end_date is None:
            return 'Never ended'

        if obj.started_at > end_date:
            return 'Ended before it started'

        if (end_date - obj.started_at).days > 1:
            return f'Many days'

        return duration_to_str(obj.ended_at - obj.started_at)

    def get_billed_str(self, obj):
        return duration_to_str(obj.accounted_duration)

    def get_accounted_duration_string(self, obj):
        return duration_to_str(obj.accounted_duration)

    def get_extra_time(self, obj):

        if obj.started_at is None or obj.ended_at is None:
            return None

        if (obj.ended_at - obj.started_at).days > 1:
            return f'Many days of extra time, probably it was never closed'

        if (obj.ended_at - obj.started_at) > obj.mentor.service.duration:
            extra_time = (obj.ended_at - obj.started_at) - obj.mentor.service.duration
            return f'Extra time of {duration_to_str(extra_time)}, the expected duration was {duration_to_str(obj.mentor.service.duration)}'
        else:
            return None

    def get_mentor_late(self, obj):

        if obj.started_at is None or obj.mentor_joined_at is None:
            return None

        if obj.started_at > obj.mentor_joined_at and (obj.started_at - obj.mentor_joined_at).seconds > (60 *
                                                                                                        4):
            return f'The mentor joined {duration_to_str(obj.started_at - obj.mentor_joined_at)} after. <br />'
        else:
            return None

    def get_mente_joined(self, obj):

        if obj.started_at is None:
            return 'Session did not start because mentee never joined'
        else:
            return None


class ServicePOSTSerializer(serializers.ModelSerializer):
    class Meta:
        model = MentorshipService
        exclude = ('created_at', 'updated_at', 'academy')

    def validate(self, data):

        academy = Academy.objects.filter(id=self.context['academy_id']).first()
        if academy is None:
            raise ValidationException(f'Academy {self.context["academy"]} not found',
                                      slug='academy-not-found')

        return {**data, 'academy': academy}


class ServicePUTSerializer(serializers.ModelSerializer):
    class Meta:
        model = MentorshipService
        exclude = ('created_at', 'updated_at', 'academy', 'slug')

    def validate(self, data):

        academy = Academy.objects.filter(id=self.context['academy_id']).first()
        if academy is None:
            raise ValidationException(f'Academy {self.context["academy"]} not found',
                                      slug='academy-not-found')

        if 'slug' in data:
            raise ValidationException('The service slug cannot be updated', slug='service-cannot-be-updated')

        return {**data, 'academy': academy}


class MentorSerializer(serializers.ModelSerializer):
    class Meta:
        model = MentorProfile
        exclude = ('created_at', 'updated_at')


class MentorUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MentorProfile
        exclude = ('created_at', 'updated_at', 'user', 'token')

    def validate(self, data):

        if 'user' in data:
            raise ValidationException('Mentor user cannot be updated, please create a new mentor instead',
                                      slug='user-read-only')
        if 'token' in data:
            raise ValidationException('Mentor token cannot be updated', slug='token-read-only')

        if 'academy' in data:
            raise ValidationException('Mentor academy cannot be updated', slug='academy-read-only')

        return data


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MentorshipSession
        exclude = ('created_at', 'updated_at')


class MentorshipBillPUTSerializer(serializers.ModelSerializer):
    class Meta:
        model = MentorshipBill
        exclude = ('created_at', 'updated_at', 'academy', 'mentor', 'reviewer', 'total_duration_in_minutes',
                   'total_duration_in_hours', 'total_price', 'overtime_minutes')

    def validate(self, data):

        academy = Academy.objects.filter(id=self.context['academy_id']).first()
        if academy is None:
            raise ValidationException(f'Academy {self.context["academy_id"]} not found',
                                      slug='academy-not-found')

        return {**data, 'academy': academy}
