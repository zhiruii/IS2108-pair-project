from django.core.management.base import BaseCommand

from accounts.models import Child, TutorProfile, User

from datetime import time, timedelta
from django.utils import timezone
from enrolments.models import EnrolmentRequest, Lesson, Package
from listings.models import Listing

PASSWORD = 'demo1234'

STAFF = {'email': 'staff@demo.com', 'first_name': 'Sam', 'last_name': 'Staff'}

TUTORS = [
    {
        'email': 'tutor1@demo.com', 'first_name': 'Amy', 'last_name': 'Tan',
        'bio': 'NIE-trained maths tutor focused on exam technique.',
        'qualification': 'NIE', 'years_experience': 8, 'teaching_mode': 'HYBRID',
    },
    {
        'email': 'tutor2@demo.com', 'first_name': 'Daniel', 'last_name': 'Ong',
        'bio': 'Degree holder teaching science online.',
        'qualification': 'DEGREE', 'years_experience': 3, 'teaching_mode': 'ONLINE',
    },
    {
        'email': 'tutor3@demo.com', 'first_name': 'Priya', 'last_name': 'Nair',
        'bio': 'University student tutoring English in person.',
        'qualification': 'STUDENT', 'years_experience': 1, 'teaching_mode': 'IN_PERSON',
    },
]

PARENT = {'email': 'parent1@demo.com', 'first_name': 'Bob', 'last_name': 'Lim'}

CHILDREN = [
    {'first_name': 'Ben', 'last_name': 'Lim', 'level': 'P4'},
    {'first_name': 'Beth', 'last_name': 'Lim', 'level': 'S2'},
]


class Command(BaseCommand):
    help = 'Create demo users, tutor profiles and children'

    def make_user(self, data, role):
        user = User.objects.filter(email=data['email']).first()
        if user:
            self.stdout.write(f'skipped {data["email"]} (already exists)')
            return user
        user = User.objects.create_user(
            username=data['email'],
            email=data['email'],
            password=PASSWORD,
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=role,
            is_staff=(role == 'STAFF'),
        )
        self.stdout.write(f'created {data["email"]}')
        return user

    def handle(self, *args, **options):
        self.make_user(STAFF, 'STAFF')

        for data in TUTORS:
            tutor = self.make_user(data, 'TUTOR')
            TutorProfile.objects.get_or_create(
                user=tutor,
                defaults={
                    'bio': data['bio'],
                    'qualification': data['qualification'],
                    'years_experience': data['years_experience'],
                    'teaching_mode': data['teaching_mode'],
                },
            )

        parent = self.make_user(PARENT, 'PARENT')
        for data in CHILDREN:
            Child.objects.get_or_create(
                parent=parent,
                first_name=data['first_name'],
                last_name=data['last_name'],
                defaults={'level': data['level']},
            )

        # test data, all just tutor1 and parent1
        today = timezone.localdate()
        tutor = TutorProfile.objects.get(user__email='tutor1@demo.com')
        ben = Child.objects.get(parent=parent, first_name='Ben')
        beth = Child.objects.get(parent=parent, first_name='Beth')

        # Three listings by tutor1
        paid_listing, _ = Listing.objects.get_or_create(
            tutor=tutor, subject='MATH', weekday=0,
            defaults={'level': 'P4', 'start_time': time(16, 0), 'end_time': time(17, 0),
                      'mode': 'ONLINE', 'rate_per_hour': 50, 'status': 'FILLED'},
        )

        accepted_listing_to_be_paid, _ = Listing.objects.get_or_create(
            tutor=tutor, subject='E_MATH', weekday=2,
            defaults={'level': 'S2', 'start_time': time(17, 0), 'end_time': time(18, 0),
                      'mode': 'ONLINE', 'rate_per_hour': 60, 'status': 'RESERVED'},
        )
        pending_listing, _ = Listing.objects.get_or_create(
            tutor=tutor, subject='SCIENCE', weekday=4,
            defaults={'level': 'P4', 'start_time': time(15, 0), 'end_time': time(16, 0),
                      'mode': 'IN_PERSON', 'rate_per_hour': 45, 'status': 'OPEN'},
        )

        # One request in each state
        paid_request, _ = EnrolmentRequest.objects.get_or_create(
            child=ben, listing=paid_listing,
            defaults={'start_date': today - timedelta(days=7), 'status': 'PAID'},
        )
        #Accepted request
        EnrolmentRequest.objects.get_or_create(
            child=beth, listing=accepted_listing_to_be_paid,
            defaults={'start_date': today + timedelta(days=7), 'status': 'ACCEPTED',
                      'decided_at': timezone.now(), 'pay_by': timezone.now() + timedelta(hours=48)},
        )
        #Pending request
        EnrolmentRequest.objects.get_or_create(
            child=ben, listing=pending_listing,
            defaults={'start_date': today + timedelta(days=7), 'status': 'PENDING'},
        )

        # A package for the paid request, 4 weekly lessons, 1 done for now
        package, _ = Package.objects.get_or_create(
            enrolment_request=paid_request,
            defaults={'start_date': today - timedelta(days=7), 'end_date': today + timedelta(days=14),
                      'lesson_count': 4, 'total_price': 200},
        )
        # Lesson 1 done 7 days ago
        Lesson.objects.get_or_create(
            package=package, date=today - timedelta(days=7),
            defaults={'start_time': time(16, 0), 'end_time': time(17, 0), 'status': 'COMPLETED',
                      'completed_at': timezone.now() - timedelta(days=7),
                      'price': 50, 'commission': 5, 'tutor_amount': 45},
        )
        # Lessons 2 to 4 just scheduled
        Lesson.objects.get_or_create(
            package=package, date=today,
            defaults={'start_time': time(16, 0), 'end_time': time(17, 0), 'status': 'SCHEDULED',
                      'price': 50, 'commission': 5, 'tutor_amount': 45},
        )
        Lesson.objects.get_or_create(
            package=package, date=today + timedelta(days=7),
            defaults={'start_time': time(16, 0), 'end_time': time(17, 0), 'status': 'SCHEDULED',
                      'price': 50, 'commission': 5, 'tutor_amount': 45},
        )
        Lesson.objects.get_or_create(
            package=package, date=today + timedelta(days=14),
            defaults={'start_time': time(16, 0), 'end_time': time(17, 0), 'status': 'SCHEDULED',
                      'price': 50, 'commission': 5, 'tutor_amount': 45},
        )

        self.stdout.write(self.style.SUCCESS(f'Demo data ready. Password for all: {PASSWORD}'))
