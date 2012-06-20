# -*- coding: utf-8 -*-
"""
Project activity calculator.

Updates project activity via a cron task. Actual implementation
is in ActivityCalculator class.
"""
from multiproject.core.configuration import Configuration
from multiproject.home.activity import ActivityCalculator


def main():
    conf = Configuration.instance()
    try:
        module = ActivityCalculator()
        module.update_project_activity()
    except Exception:
        conf.log.exception("Failed to update project activity")

if __name__ == '__main__':
    main()
