# Sprint 1 Report — GradeTracker

**Team 1:** Anthony Alperov and Netonna Udezeh  
**Sprint:** September 15 – October 12, 2026  
**Team Meetings:** October 10, 11, 12, and 13, 2026  
**Sprint Review and Retrospective:** October 13, 2026  
**Video Link:** https://www.youtube.com/watch?v=DUCu_yaBcDs  
**GitHub Repository:** https://github.com/anthonyalperov/CptS322-GradeTracker

## What's New (User Facing)

During Sprint 1, our team focused on building two of the main features for GradeTracker.

- **Student Views Grades (Issue #1):** Students can retrieve their grades through our backend API. The response includes their scores and the courses associated with those grades.
- **Instructor Enters Grades (Issue #2):** Instructors can submit grades through our API. Before saving a grade, the system checks that the instructor teaches the course, the student is enrolled, and the score is between 0 and 100.

Both features are currently working through our FastAPI backend. We haven't implemented a full user interface or login system yet, but these features give us a foundation to build on in future sprints.

## Work Summary (Developer Facing)

For our first sprint, we wanted to focus on getting the basic grade management functionality working before moving on to more advanced features.

We started by organizing our eight planned features in GitHub Projects and selecting two that we felt were important to complete first.

Netonna worked on allowing students to view their grades, while Anthony worked on allowing instructors to enter grades. We developed our features separately and used GitHub pull requests to bring everything together.

We used Python and FastAPI for the backend, SQLite for storing information, and PyTest to check that our code worked correctly. After merging our work, we ran our tests to make sure everything was still functioning as expected.

One thing we could have done better was keeping up with our documentation. We forgot to take screenshots of our Kanban board at the beginning and middle of the sprint. Although we still have our GitHub activity and final board, this is something we'll improve in Sprint 2.

Overall, Sprint 1 helped us get more comfortable working together, managing our code through GitHub, and following a software engineering workflow.

## Unfinished Work

We completed both features that we committed to for Sprint 1, so we don't have any unfinished sprint issues.

We still have six other features in our Product Backlog and Icebox. These were not part of our Sprint 1 commitments and will be considered for future sprints.

Some of our planned functionality includes updating grades, managing courses and enrollment, user authentication, and providing feedback.

## Completed Issues/User Stories

### Issue #1 — Student Views Grades

**Assigned to:** Netonna Udezeh  
**Story Points:** 3  
**Status:** Completed

Netonna implemented the backend functionality that allows student grade information to be retrieved from the database. This includes the student's scores and corresponding course names.

[GitHub Issue #1](https://github.com/anthonyalperov/CptS322-GradeTracker/issues/1)

### Issue #2 — Instructor Enters Grades

**Assigned to:** Anthony Alperov  
**Story Points:** 5  
**Status:** Completed

Anthony implemented the feature that allows instructors to enter grades for students. The system checks instructor assignment, student enrollment, and valid grade values before saving the information to our SQLite database.

We also wrote tests to make sure the feature handled valid and invalid requests correctly.

[GitHub Issue #2](https://github.com/anthonyalperov/CptS322-GradeTracker/issues/2)  
[Pull Request #9](https://github.com/anthonyalperov/CptS322-GradeTracker/pull/9)

### Sprint Completion

We completed both of our planned Sprint 1 features, totaling **8 out of 8 committed story points**.

This also means we completed **2 out of our 8 total planned features**, meeting the 25% completion requirement for Sprint 1.

## Incomplete Issues/User Stories

Neither of our committed Sprint 1 issues was left incomplete.

The remaining six features are still in our Product Backlog and Icebox because we planned to work on them in later sprints.

## Code Files for Review

These are some of the main files we worked with during Sprint 1:

- [main.py](https://github.com/anthonyalperov/CptS322-GradeTracker/blob/main/code/backend/main.py) — Contains our FastAPI endpoints for entering and viewing grades.
- [database.py](https://github.com/anthonyalperov/CptS322-GradeTracker/blob/main/code/backend/database.py) — Sets up our SQLite database and tables.
- [seed.py](https://github.com/anthonyalperov/CptS322-GradeTracker/blob/main/code/backend/seed.py) — Adds sample information to the database for testing and demonstrations.
- [test_grades.py](https://github.com/anthonyalperov/CptS322-GradeTracker/blob/main/tests/test_grades.py) — Contains automated tests for grade entry and validation.

## Sprint Review

We held our Sprint Review on October 13, 2026.

During the review, we went over the features we completed and looked at how they worked together.

Anthony's feature allows instructors to enter grades, and Netonna's feature allows those grades to be retrieved for students. Both features use the same SQLite database, which helped us demonstrate how our work connects.

We also reviewed our GitHub Issues and confirmed that both planned features were completed and merged into the main branch.

Overall, we were able to meet our main Sprint 1 goal and establish a working backend foundation for GradeTracker.

## Retrospective Summary

We held our Sprint Retrospective on October 13, 2026.

### What Went Well

One thing that went well was dividing the work between the two of us. We each had a clear feature to focus on, which made it easier to organize our responsibilities.

We also got more experience using GitHub branches and pull requests to combine our work. Automated testing was helpful because it allowed us to check our code before and after integration.

### What We Could Improve

One thing we need to improve is documenting our progress throughout the sprint.

We used GitHub Projects to keep track of our issues, but we forgot to capture screenshots at the beginning and midpoint of the sprint.

We also want to be more consistent about checking in on our progress instead of leaving documentation and final preparation until the end.

### Changes for Sprint 2

For our next sprint, we plan to make three improvements:

1. **Capture Kanban screenshots throughout the sprint.** We'll take screenshots at the beginning, midpoint, and end so we have the required documentation ready.
2. **Have a mid-sprint progress check.** This will give us a chance to discuss what we've completed, identify any problems, and make adjustments before the deadline.
3. **Continue testing and reviewing code before merging.** We'll use PyTest and GitHub pull requests to make sure our features work correctly and integrate with the rest of the application.

We believe these changes will help us stay more organized and make future sprints run more smoothly.

## Kanban Evidence Note

We want to acknowledge that we forgot to capture screenshots of our Kanban board at the beginning and midpoint of Sprint 1.

We have included our final Kanban board screenshot along with available GitHub activity and pull request history to show our completed work.

We understand that these don't replace the missing screenshots, and we'll make sure to capture the required evidence throughout future sprints.