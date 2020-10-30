# import django_tables2 as tables
from django.utils.translation import ugettext_lazy as _
from .models import (HealthcareProvider, Case, Doctor, Room)
from crispy_forms.bootstrap import StrictButton, InlineField, FormActions, Div, Field
from crispy_forms.layout import Layout, Submit, Fieldset
from django.forms.models import modelform_factory
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from django.utils import timezone
from django import forms
from .helpers import WithPageTitle, TheHelper, colw, clearfix
import datetime
from collections import defaultdict
import pytz
from .timezone import mytz,  time2localdate, localdatenow
from .forms import NextMonthsForm

## mm 

import time 

from dateutil import relativedelta

class PatientRecord:
    def __init__(self,patient_name,date):
        self.patient_name = patient_name
        self.date = date

    def get_name(self):
        return  self.patient_name
    def get_date(self):
        return  self.date

def rooms_by_date_info(cases, start, time_span):
    """ time_span: number of days to look at. """


    assert isinstance(start, datetime.date)
    
    days=[start+timezone.timedelta(days=d) for d in range(time_span)]

    rooms = Room.objects.order_by("name")
    # caps = Room.objects.order_by("capacity")


    room_names=[str(room) for room in rooms]
    # room_caps=[str(room) for Room.capacity in rooms]
    # print(room_caps)

    room_occupancies = [[roomname, [[] for i in range(time_span)]] for roomname in room_names]
    # print(room_occupancies)

    for n, day in enumerate(days):

        for case in cases:
            treat_begin=case.stay_begin()
            treat_end=case.stay_end()

            # .astimezone() converts date to local timezone
            if ((day>=treat_begin) and
                (day< treat_end)):
                csr=str(case.stay_room)
                # print(csr)
                if csr not in room_names:
                  # user has no room assigned - skip
                  continue
                # p = PatientRecord(case.patient_name(),case.treatment_date())
                # room_occupancies[room_names.index(csr)][1][n].append(p)
                room_occupancies[room_names.index(csr)][1][n].append(case.patient_name())
                # FIXME: highly inefficient!
                room_occupancies[room_names.index(csr)][1][n].sort()
    # for i in room_occupancies:
    #     print(i)

    return room_occupancies, days[:time_span]


class RoomsMonthView(TemplateView, WithPageTitle):
  
    
    page_title=_("Rooms by month")
    template_name="opplan/roomsovertime.html"

    
    def get_context_data(self, **kwargs):
        context=super(RoomsMonthView, self).get_context_data(**kwargs)

        self.month_select_form = NextMonthsForm(data=self.request.GET)
        week_groups=[]
        now=localdatenow()

        if self.month_select_form.is_valid():
            data = self.month_select_form["month"].data
            if data is not None:
                s = data.split("-")
                year, month = int(s[0]), int(s[1])
                now = datetime.date(year, month, 1)

        try:
          this_month = self.request.GET['month']
        except:
          this_month = time.strftime("%Y-%m", time.localtime(time.time()))

        try:
          this_y = int(this_month.split("-")[0])
          this_m = int(this_month.split("-")[1])
          # reset to beginning of month
          now = datetime.date(this_y, this_m, 1)
        except:
          now = datetime.date(now.year, now.month, 1)


        # and start at latest monday before now
        # now=now-timezone.timedelta(days=now.weekday())
        year_show = str(now.year)
        # print(year_show)
        if not now.month == 1:
            t = datetime.datetime(now.year, now.month - 1, 1,  tzinfo=pytz.UTC)
        else:
            t = datetime.datetime(now.year,12, 1, tzinfo=pytz.UTC)
        if not now.month == 12:
            d = datetime.datetime(now.year, now.month + 1, 28,  tzinfo=pytz.UTC)
        else:
            d = datetime.datetime(now.year, 1, 28,  tzinfo=pytz.UTC)
        print(t,d)
        # m_show = now.month + 1
        cases = Case.objects.filter(is_hidden=False, treatment_time__year=year_show, treatment_time__range=(t,d))
        # for case in cases:
        #     print(case.treatment_date(),case.id, case.stay_duration)


        for week in range(5):
            room_occupancies, days=rooms_by_date_info(
                cases,
                now+timezone.timedelta(days=7*week), 7)
            week_groups.append((room_occupancies, days))

        context["week_groups"]=week_groups
        # print(week_groups)
        context["month_select_form"]= self.month_select_form


        try:
          this_month = self.request.GET['month']
        except:
          this_month = time.strftime("%Y-%m", time.localtime(time.time()))
          
        st = "%s-01" % this_month
        
        ts = time.mktime(datetime.datetime.strptime(st, "%Y-%m-%d").timetuple())
        
        this_ts = datetime.date.fromtimestamp(ts)

        
        prev_month = this_ts +  relativedelta.relativedelta(months=-1)
        next_month = this_ts +  relativedelta.relativedelta(months=1)

        pm = prev_month.strftime("%Y-%m")
        nm = next_month.strftime("%Y-%m")

        
        context["next_month"] = nm
        context["prev_month"] = pm
    

        return context
