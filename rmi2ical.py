#
# rmi2ical.py
#
# (c) 2024 Florian Brandner
#
# Description:
# Connects to a Redmine Server, takes the Issues of a project and generates a
# icalendar TODO List
#
# Notes:
# - The API must be enabled in the admin settings
#
# Helpful links:
#   https://python-redmine.com/resources/issue.html
#   https://icalendar.readthedocs.io/en/latest/
#   https://datatracker.ietf.org/doc/html/rfc5545

from redminelib import Redmine
from icalendar import Calendar, Todo
from redmine_secrets import *
import os

redmine = Redmine(url, username=user, password=password)

try:
    project = redmine.project.get('IT')
except Exception as err:
    print(f"Exception {err=}")
    exit(1)

cal = Calendar()
cal.add('PRODID', '-//Redmine2ical//')
cal.add('version', '1.0')

for issue in project.issues:
    event = Todo()
    event.add("DTSTAMP", issue.created_on)
    event.add("UID", issue.id)
    # Class
    # Completed
    event.add("CREATED", issue.created_on)
    event.add("DESCRIPTION", issue.description)
    # DTStart
    # Geo
    event.add("LAST-MODIFIED", issue.updated_on)
    #
    if issue.due_date is not None:
        event.add("DUE", issue.due_date)


    event.add("PERCENT-COMPLETE", issue.done_ratio)
    event.add("PERCENT", issue.done_ratio)

    # Priority is not used
    # event.add("PRIORITY", issue.priority)

    # TODO: Configurable mapping
    match issue.status.name:
        case "In Bearbeitung":
            event.add("STATUS", "IN-PROCESS")

    event.add("SUMMARY", issue.subject)

    # Relationship: IDs of Children
    if len(issue.children) > 0:
        for child in issue.children:
            event.add("RELATED-TO;RELTYPE=CHILD", child.id)

    # Relationship: ID of Parent
    if hasattr(issue, 'parent'):
        event.add("RELATED-TO;RELTYPE=PARENT", issue.parent.id)

    if hasattr(issue, 'category'):
        event.add("CATEGORIES", issue.category.name)

    event.add("URL", issue.url)



    cal.add_component(event)


# Write result to disc
f = open(os.path.join('Output.ics'), 'wb')
f.write(cal.to_ical())
f.close()

# Mapping:
#   REDMINE             ical-Event
#   created_on          DTSTAMP         required
#   id                  UID             required
#                       CLASS           optional
#                       COMPLETED       optional
#   created_on          CREATED         optional
#   description         DESCRIPTION     optional
#                       DTSTART         optional
#                       GEO             optional
#   updated_on          LAST-MODIFIED   optional
#   -                   LOCATION        optional
#   -                   ORGANIZER       optional
#   done_ratio          PERCENT         optional
#   priority            PRIORITY        optional
#   -                   RECURRENCE-ID   optional
#   -                   SEQ             optional
#   status              STATUS          optional
#   subject             SUMMARY         optional
#   url                 URL             optional
#                       RRULE           optional (only once)
#   due_date            DUE             optional (Not with DURATION)
#   -                   DURATION        optional (Not with DUE, requires DTSTART)
#                       ATTACH          optional, multiple
#   -                   ATTENDEE        optional, multiple
#   category            CATEGORIES      optional, multiple
#                       COMMENT         optional, multiple
#                       CONTACT         optional, multiple
#                       EXDATE          optional, multiple
#                       RSTATUS         optional, multiple
#   children / parent   RELATED         optional, multiple
#                       RESOURCES       optional, multiple
#                       RDATE           optional, multiple
#   allowed_statuses
#   attachments
#   author
#   changesets
#   closed_on
#   estimated_hours
#   internal_id
#   is_private
#   journals            -               Unused
#   manager
#   project
#   relations
#   start_date
#   time_entries
#   total_estimated_hours -             Unused
#   tracker             -               Unused
#   watchers

