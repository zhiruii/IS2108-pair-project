from datetime import time, timedelta

from django.db import transaction
from django.shortcuts import render
from enrolments.models import Lesson, EnrolmentRequest, Package
from enrolments.utils import expire_overdue_requests
from listings.models import Listing
from django.utils import timezone

from accounts.models import Child, TutorProfile, User
from ml.models import PriceFlag
from ratings.models import Dispute, Rating

def index(request):
    context = {}
    if request.user.is_authenticated and request.user.role == "PARENT":
        expire_overdue_requests()

        lessons = Lesson.objects.filter(
            package__enrolment_request__child__parent=request.user
        )

        upcoming_lessons = lessons.filter(
            status="SCHEDULED", date__gte=timezone.localdate()
        ).order_by("date", "start_time")
        
        next_lesson = upcoming_lessons.first()
        
        to_pay = EnrolmentRequest.objects.filter(
            child__parent=request.user,
            status="ACCEPTED"
        ).order_by("pay_by")
        
        pending_count = EnrolmentRequest.objects.filter(
            child__parent=request.user,
            status="PENDING"
        ).count()
        
        to_rate = Package.objects.filter(
            enrolment_request__child__parent=request.user,
        ).exclude(
            lessons__status="SCHEDULED" # exclude if still have lessons left
        ).exclude(
            ratings__rater=request.user # already rated
        ).select_related("enrolment_request__listing", "enrolment_request__child__parent")
        
        context={'next_lesson': next_lesson, 'to_pay': to_pay, 'pending_count': pending_count, 'to_rate': to_rate}

    elif request.user.is_authenticated and request.user.role == "TUTOR":
        expire_overdue_requests()

        lessons = Lesson.objects.filter(
            package__enrolment_request__listing__tutor__user=request.user
        )

        next_lesson = lessons.filter(
            status="SCHEDULED", date__gte=timezone.localdate()
        ).order_by("date", "start_time").first()

        to_mark = lessons.filter(
            status="SCHEDULED", date__lt=timezone.localdate()   # BEFORE today
        ).count()

        request_count = EnrolmentRequest.objects.filter(
            listing__tutor__user=request.user,         # requests on this tutor's listings
            status="PENDING"
        ).count()
        
        to_rate = Package.objects.filter(
            enrolment_request__listing__tutor__user=request.user,
        ).exclude(
            lessons__status="SCHEDULED" # exclude if still have lessons left
        ).exclude(
            ratings__rater=request.user # already rated
        ).select_related("enrolment_request__listing__tutor__user", "enrolment_request__child")

        flagged = Listing.objects.filter(
            tutor__user=request.user,
            price_flag__isnull=False,
        ).exclude(status="CLOSED").select_related("price_flag")
        
        context = {"next_lesson": next_lesson, "to_mark": to_mark, "request_count": request_count, "to_rate": to_rate, "flagged": flagged}
    
    return render(request, 'index.html', context)


def last_weekday(weekday):
    today = timezone.localdate()
    offset = (today.weekday() - weekday) % 7
    return today - timedelta(days=offset)

def next_weekday(weekday):
    tomorrow = timezone.localdate() + timedelta(days=1)
    offset = (weekday - tomorrow.weekday()) % 7
    return tomorrow + timedelta(days=offset)


@transaction.atomic
def loadData(request):
    accounts = [
        ('staff@demo.com', 'Sam Staff', 'Admin'),
        ('tutor1@demo.com', 'Amy Tan', 'Tutor'),
        ('tutor2@demo.com', 'Daniel Ong', 'Tutor'),
        ('parent1@demo.com', 'Bob Lim', 'Parent')
    ]

    if User.objects.filter(email = 'staff@demo.com').exists():
        return render(request, 'load_data.html', {'already_loaded': True, 'accounts': accounts})

    now = timezone.now()
    today = timezone.localdate()
    yesterday = today - timedelta(days=1)

    staff = User.objects.create_user(username='staff@demo.com', email='staff@demo.com', password='demo1234',
                                     first_name='Sam', last_name='Staff', role='STAFF', is_staff=True)
    amy_user = User.objects.create_user(username='tutor1@demo.com', email='tutor1@demo.com', password='demo1234',
                                        first_name='Amy', last_name='Tan', role='TUTOR')
    daniel_user = User.objects.create_user(username='tutor2@demo.com', email='tutor2@demo.com', password='demo1234',
                                           first_name='Daniel', last_name='Ong', role='TUTOR')

    amy = TutorProfile.objects.create(user=amy_user, bio='NIE-trained Mathematics tutor',
                                      qualification='NIE', years_experience=8, teaching_mode='HYBRID')
    daniel = TutorProfile.objects.create(user=daniel_user, bio='Degree holder science tutor',
                                       qualification='DEGREE', years_experience=3, teaching_mode='ONLINE')
    bob = User.objects.create_user(username='parent1@demo.com', email='parent1@demo.com', password='demo1234',
                                   first_name='Bob', last_name='Lim', role='PARENT')
    ben = Child.objects.create(parent=bob, first_name='Ben', last_name='Lim', level='P4')
    beth = Child.objects.create(parent=bob, first_name='Beth', last_name='Lim', level='S2')

    l1 = Listing.objects.create(tutor=amy, subject='MATH', level='P4', weekday=yesterday.weekday(),
                                start_time=time(14, 0), end_time=time(15, 0), mode='ONLINE',
                                rate_per_hour='50.00', status='FILLED')
    l2 = Listing.objects.create(tutor=amy, subject='E_MATH', level='S2', weekday=2,
                                start_time=time(17, 0), end_time=time(18, 0), mode='HYBRID',
                                rate_per_hour='60.00', status='RESERVED')
    l3 = Listing.objects.create(tutor=daniel, subject='SCIENCE', level='P4', weekday=4,
                                start_time=time(15, 0), end_time=time(16, 0), mode='IN_PERSON',
                                rate_per_hour='120.00', status='OPEN')
    l4 = Listing.objects.create(tutor=daniel, subject='E_MATH', level='S2', weekday=5,
                                start_time=time(10, 0), end_time=time(11, 0), mode='ONLINE',
                                rate_per_hour='70.00', status='CLOSED')
    l5 = Listing.objects.create(tutor=amy, subject='ENGLISH', level='S2', weekday=1,
                                start_time=time(16, 0), end_time=time(17, 0), mode='IN_PERSON',
                                rate_per_hour='45.00', status='FILLED')
    l6 = Listing.objects.create(tutor=daniel, subject='MATH', level='P4', weekday=3,
                                start_time=time(17, 0), end_time=time(18, 0), mode='HYBRID',
                                rate_per_hour='55.00', status='FILLED')

    p1_first = yesterday - timedelta(days=7)
    q1 = EnrolmentRequest.objects.create(child=ben, listing=l1, start_date=p1_first,
                                         status='PAID', decided_at=now)
    p1 = Package.objects.create(enrolment_request=q1, start_date=p1_first,
                                end_date=p1_first + timedelta(days=21), lesson_count=4,
                                total_price='200.00', status='ACTIVE')
    p1_statuses = ['COMPLETED', 'SCHEDULED', 'SCHEDULED', 'SCHEDULED']
    for week in range(4):
        Lesson.objects.create(package=p1, date=p1_first + timedelta(days=7 * week),
                              start_time=time(14, 0), end_time=time(15, 0),
                              status=p1_statuses[week],
                              completed_at=now if p1_statuses[week] == 'COMPLETED' else None,
                              price='50.00', commission='2.50', tutor_amount='47.50')

    p2_first = last_weekday(1) - timedelta(days=21)
    q2 = EnrolmentRequest.objects.create(child=beth, listing=l5, start_date=p2_first,
                                         status='PAID', decided_at=now)
    p2 = Package.objects.create(enrolment_request=q2, start_date=p2_first,
                                end_date=p2_first + timedelta(days=21), lesson_count=4,
                                total_price='180.00', status='COMPLETED')
    for week in range(4):
        Lesson.objects.create(package=p2, date=p2_first + timedelta(days=7 * week),
                              start_time=time(16, 0), end_time=time(17, 0),
                              status='COMPLETED', completed_at=now,
                              price='45.00', commission='2.25', tutor_amount='42.75')

    p3_first = last_weekday(3) - timedelta(days=21)
    q3 = EnrolmentRequest.objects.create(child=ben, listing=l6, start_date=p3_first,
                                         status='PAID', decided_at=now)
    p3 = Package.objects.create(enrolment_request=q3, start_date=p3_first,
                                end_date=p3_first + timedelta(days=21), lesson_count=4,
                                total_price='220.00', status='COMPLETED')
    for week in range(4):
        Lesson.objects.create(package=p3, date=p3_first + timedelta(days=7 * week),
                              start_time=time(17, 0), end_time=time(18, 0),
                              status='COMPLETED', completed_at=now,
                              price='55.00', commission='2.75', tutor_amount='52.25')
    EnrolmentRequest.objects.create(child=beth, listing=l2, start_date=next_weekday(2),
                                status='ACCEPTED', decided_at=now, pay_by=now + timedelta(hours=48),
                                message='Beth needs help with her E-Math before prelims.')
    EnrolmentRequest.objects.create(child=ben, listing=l3, start_date=next_weekday(4),
                                    status='PENDING', message='Ben is keen to improve his Science.')
    EnrolmentRequest.objects.create(child=beth, listing=l4, start_date=next_weekday(5),
                                    status='DECLINED', decided_at=now,
                                    decline_reason='Tutor unavailable')
    EnrolmentRequest.objects.create(child=beth, listing=l4, start_date=next_weekday(5) + timedelta(days=7),
                                    status='WITHDRAWN',
                                    withdraw_reason='Schedule clash with another class.')
    EnrolmentRequest.objects.create(child=beth, listing=l4, start_date=next_weekday(5) + timedelta(days=14),
                                    status='EXPIRED', decided_at=now - timedelta(days=4),
                                    pay_by=now - timedelta(days=2))

    r1 = Rating.objects.create(rater=bob, rated_tutor=amy, package=p2, stars=1)
    r2 = Rating.objects.create(rater=daniel_user, rated_parent=bob, package=p3, stars=4)


    Dispute.objects.create(rating=r1, rating_summary=str(r1), raised_by=amy_user, status='OPEN',
                           reason='This rating does not match the lessons we had. Please review.')
    Dispute.objects.create(rating=r2, rating_summary=str(r2), raised_by=bob, status='REJECTED',
                           reason='I think this rating is too low.',
                           admin_note='The rating is consistent with the lesson record.',
                           resolved_by=staff, resolved_at=now)
    Dispute.objects.create(rating=None, rating_summary='1/5 rating from Bob Lim to Daniel Ong',
                           raised_by=daniel_user, status='UPHELD',
                           reason='The rating was left after a missed lesson that I had rescheduled.',
                           admin_note='Rating removed by staff',
                           resolved_by=staff, resolved_at=now)
    
    
    PriceFlag.objects.create(listing=l3, flagged_by=staff,
                             note='Rate looks far above the typical P4 Science rate.')

    return render(request, 'load_data.html', {'already_loaded': False, 'accounts': accounts})