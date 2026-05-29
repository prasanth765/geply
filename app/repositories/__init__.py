"""
====================================================================
  Project : Geply - AI Interview Platform
  Company : GEP Worldwide
  Author  : Prasanth Ragupathy <prasanth.ragupathy@gep.com>
  File    : __init__.py
  Purpose : Module in the Geply AI Interview Platform by Prasanth Ragupathy.
====================================================================
"""
from app.repositories.base import BaseRepository
from app.repositories.user_repo import UserRepository
from app.repositories.job_repo import JobRepository
from app.repositories.candidate_repo import CandidateRepository
from app.repositories.interview_repo import InterviewRepository
from app.repositories.schedule_repo import ScheduleRepository
from app.repositories.report_repo import ReportRepository
from app.repositories.notification_repo import NotificationRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "JobRepository",
    "CandidateRepository",
    "InterviewRepository",
    "ScheduleRepository",
    "ReportRepository",
    "NotificationRepository",
]
