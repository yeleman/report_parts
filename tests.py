#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

from django.test import TestCase

from .models import ReportType, Report

from eav.models import Attribute

import datetime

class BasicTests(TestCase):


    def setUp(self):
        self.attribute = Attribute.objects.create(name='one',  
                                                  datatype=Attribute.TYPE_INT)
        self.report_type = ReportType.objects.create(name='test')
        self.report = Report.objects.create(type=self.report_type)

    def test_create_report_type(self):
        
        rt = ReportType(name='test2')
        rt.save()
        
        
    def test_you_can_add_parts_to_a_report(self):
    
        self.report_type.parts.add(self.attribute)
        self.report_type.parts.add(Attribute.objects.create(name='two', 
                                              datatype=Attribute.TYPE_FLOAT))
        self.assertEqual(self.report_type.parts.count(), 2)
        
        
    def test_reports_must_have_have_a_report_type(self):
        report = Report(type=self.report_type)
        report.save()
        
        
    def test_report_can_be_used_with_the_eav(self):
        self.report.status.one = 1
        self.report.save()
        report = Report.objects.get(pk=self.report.pk)
        self.assertEqual(report.status.one, 1)
        
        self.assertEqual(Report.objects.get(status__one=1), self.report)
        
        
    def test_filling_all_attributes_from_attribute_type_make_it_completed(self):
        self.report_type.parts.add(self.attribute)
        self.report_type.parts.add(Attribute.objects.create(name='two', 
                                              datatype=Attribute.TYPE_FLOAT))
        self.report.status.one = 1
        self.assertFalse(self.report.is_completed())
        self.assertFalse(self.report.completed)
        self.report.status.two = 2.0
        self.report.save()
        self.assertTrue(self.report.is_completed())
        self.assertTrue(self.report.completed)
        self.assertEqual(self.report.completed.timetuple()[:-2],
                        datetime.datetime.today().timetuple()[:-2])
     
     
    def test_you_can_have_progress_on_a_report(self):
        self.report_type.parts.add(self.attribute)
        self.report_type.parts.add(Attribute.objects.create(name='two', 
                                              datatype=Attribute.TYPE_FLOAT))
        self.report.status.one = 1
        self.assertEqual(self.report.progress, (1, 2)) 
        
     
    def test_you_can_have_summary_on_a_report(self):
        self.report_type.parts.add(self.attribute)
        self.report_type.parts.add(Attribute.objects.create(name='two', 
                                              datatype=Attribute.TYPE_FLOAT))
        self.report.status.one = 1
        self.assertEqual(self.report.summary, {'one': 1, 'two': None})
        
    
    def test_you_can_ask_the_report_to_be_filled_in_a_delay(self):
        report = self.report
        self.assertFalse(report.is_outdated(datetime.timedelta(5)))
        
        report.updated =  report.updated - datetime.timedelta(10)
        self.assertTrue(report.is_outdated(datetime.timedelta(10)))
        
        self.assertFalse(report.is_outdated())
        
        self.report_type.delay = datetime.timedelta(10)
        self.report_type.save()
        
        self.assertTrue(report.is_outdated())
               
