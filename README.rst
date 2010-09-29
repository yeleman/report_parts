report parts is a Django tool to follow the completion of a report.

Setup
=============

- Put this dir in the PYTHON PATH
- add report_parts to your INSTALLED_APPS
- syncdb
- optionnally, runs 'django-admin.py compilemessage' to get french translation

Usage
======

- Create attributes (easier in the admin, provide them as fixtures in your app)
  in the EAV for each part of you report::
  
     >>> stats = Attribute.objects.create(name='stats', datatype=Attribute.TYPE_BOOLEAN)
     >>> introduction = Attribute.objects.create(name='introduction', datatype=Attribute.TYPE_BOOLEAN)
  
  You can choose TYPE_OBJECT to map a django model.

- Create a report type (easier in the admin, provide it as fixtures in your app)
  using this attributes as parts::

     >>> rtype = ReportType.objects.create(name='Thesis')
     >>> rtype.parts.add(stats)
     >>> rtype.parts.add(introduction)
     >>> import datetime
     >>> rtype.delay = datetime.timedelta(minutes=3)
     >>> rtype.save()

- Then create your report::

    >>> report, created = Report.get_or_create(rt=rtype)
    >>> report.status.stats = True
    >>> report.is_completed()
    False
    >>> report.progress
    >>> (1, 2)
    >>> report.is_outdated() # it would be True in 4 minutes
    False
    >>> report.status.introduction = True
    >>> report.is_completed()
    True
    >>> report.progress
    >>> (2, 2)
    >>> self.summury
    {'introduction': True, 'stats': True}
    
You can filter reports by attaching eav attributes to it that are not a part
of the rapport, they will be ignored. This is why report doesn't come with
any attributes to filter it since they can be many variants.

If you use TYPE_OBJECT, then each part will be a reference to the associated
Django model.


Known limitations
=================

There are some issues with django-nose and django-eav. Django-nose should 
be deactivated when you use them.
