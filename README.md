# Cluster C Assistant

A local course-logistics starter for Columbia Business School Cluster C, Fall 2026. Open the unzipped folder as a project in Codex desktop and start a new conversation there. Requires your own Codex access, Python 3 and network access. Uploading this folder into regular ChatGPT does not install a live local connection.

## Connection and Canvas requirements
No account or credentials are included. Canvas documentation says applications used by multiple users must use OAuth and may not ask other users to manually generate and enter tokens. This package includes the existing personal-development token setup for local testing; it is not an OAuth-enabled, approved multi-user product. Before deploying it to classmates as a live integration, obtain Columbia's Canvas administrator approval and implement OAuth. Documentation: https://courseworks2.columbia.edu/doc/api/file.oauth.html

For authorized personal testing, run `outputs/Connect CourseWorks.command` on macOS. It saves your own token locally using a hidden Terminal prompt. Nothing appears while typing or pasting; press Return once. Never paste credentials into chat. If Python is missing, install Python 3 from python.org. If Finder will not run the launcher, open Terminal in this folder and run `python3 work/courseworks.py setup`; do not disable system security protections. On Windows/Linux use that command with your installed Python 3 interpreter.

Once connected, ask: "Check my active courses, then tell me what is due this week, including required readings and individual versus group work."

## What you can ask
- What's due this week? Include required readings.
- What should I prepare for tomorrow?
- Which readings are optional?
- What announcements have changed?
- Where are my classes and review sessions?

The helper performs approved GET requests only. It blocks grade/submission/message/roster endpoints and unapproved query parameters, and removes grade-related response fields. It does not determine whether you submitted an assignment. A personal Canvas token itself may have broader permissions than this helper; this is an application restriction, not a guarantee about the token's scope. Teaching text may discuss grading policies; no student marks are bundled.

## Included information and limits
The Cluster C schedule is static and dated; announcements must be checked for changes, holidays and makeup classes. The helper does not download attachments. Each user's deadlines may differ. Google Calendar is a separate optional connection, not bundled. Public club feeds are incomplete. No background refresh or monitoring is configured.

## Keep credentials private
Setup creates `work/.secrets/canvas-token` with restrictive local file permissions. Do not share your configured folder, zip it, or commit that folder. Hidden files are included in ordinary copies and ZIPs; .gitignore does not exclude them from ZIPs. Only redistribute the original clean ZIP. To disconnect, remove your local saved token and revoke it in CourseWorks.
