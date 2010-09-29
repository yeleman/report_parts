#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

import datetime

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as __
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

import eav
from eav.registry import EavConfig
from eav.models import Attribute

from .fields import TimedeltaField


class ReportType(models.Model):

    class Meta:
        verbose_name = __("report type")
        verbose_name_plural  = __("report types")

    name = models.CharField(__(u"name"), max_length=128, unique=True)
    parts = models.ManyToManyField(Attribute, verbose_name=__(u'parts'))
    delay = TimedeltaField(blank=True, null=True)
    
    
class Report(models.Model):
    """
        Let you define how many results of which type you expect and check
        is the report is complete 
    """
    
    class Meta:
        verbose_name = __("report")
        verbose_name_plural  = __("reports")

    type = models.ForeignKey(ReportType, verbose_name=__(u'report type'))
    completed = models.DateTimeField(__(u"completed"), blank=True, null=True)
    updated = models.DateTimeField(__(u"updated"), auto_now=True)
    created = models.DateTimeField(__(u"created"), 
                                   default=datetime.datetime.now,
                                   editable=False)
    
    
    def save(self, *args, **kwargs):
        if self.pk and self.is_completed():
            self.completed = datetime.datetime.now()
        models.Model.save(self, *args, **kwargs)
    
    
    def is_completed(self):
        """
            Return True if the report is completly filled, which means that
            all the attributes listed in ReportType have a non False value
        """
        progress = self.progress
        return progress[0] == progress[1]
    
    
    @property
    def progress(self):
        """
            Return the number of parts of the report completed over the 
            number that are not.
        """
        attrs = self.type.parts.all()
        return (sum(int(bool(getattr(self.status, a.slug))) for a in attrs),
               len(attrs))
           
               
    @property
    def summary(self):
        """
            Return the number of parts of the report completed over the 
            number that are not.
        """
        attrs = self.type.parts.all()
        return dict((a.slug, getattr(self.status, a.slug)) for a in attrs)
        
        
    def is_outdated(self, delta=None):
        """
            Check if the last part of the report have been made a certain time
            ago.
        """
        t = delta or self.type.delay 
        try:
            return datetime.datetime.now() > self.updated + t
        except TypeError:
            return False
    
    
class ReportEavConfig(EavConfig):
    eav_attr = 'status'

eav.register(Report, ReportEavConfig)
