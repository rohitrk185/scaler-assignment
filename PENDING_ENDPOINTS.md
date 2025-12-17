# Pending API Endpoints

This file tracks all unimplemented endpoints from the OpenAPI specification for the 11 core entities.
As endpoints are implemented, they should be removed from this list.

**Last Updated:** 2025-12-17

---

## 1. Workspaces

### Currently Implemented (10)
- ✅ GET `/workspaces`
- ✅ GET `/workspaces/{workspace_gid}`
- ✅ PUT `/workspaces/{workspace_gid}`
- ✅ GET `/workspaces/{workspace_gid}/users`
- ✅ POST `/workspaces/{workspace_gid}/addUser`
- ✅ POST `/workspaces/{workspace_gid}/removeUser`
- ✅ GET `/workspaces/{workspace_gid}/events`
- ✅ GET `/workspaces/{workspace_gid}/custom_fields`
- ✅ GET `/workspaces/{workspace_gid}/projects`
- ✅ GET `/workspaces/{workspace_gid}/tags`
- ✅ GET `/workspaces/{workspace_gid}/teams`
- ✅ GET `/workspaces/{workspace_gid}/workspace_memberships`
- ✅ GET `/workspaces/{workspace_gid}/audit_log_events`

### Pending (6)
- [x] POST `/workspaces/{workspace_gid}/addUser` - Add user to workspace
- [x] POST `/workspaces/{workspace_gid}/removeUser` - Remove user from workspace
- [x] GET `/workspaces/{workspace_gid}/events` - Get workspace events
- [x] GET `/workspaces/{workspace_gid}/audit_log_events` - Get audit log events
- [x] GET `/workspaces/{workspace_gid}/custom_fields` - Get workspace custom fields
- [x] GET `/workspaces/{workspace_gid}/projects` - Get workspace projects
- [x] GET `/workspaces/{workspace_gid}/tags` - Get workspace tags
- [x] GET `/workspaces/{workspace_gid}/teams` - Get workspace teams
- [x] GET `/workspaces/{workspace_gid}/workspace_memberships` - Get workspace memberships
- [ ] GET `/workspaces/{workspace_gid}/tasks/custom_id/{custom_id}` - Get task by custom ID
- [ ] GET `/workspaces/{workspace_gid}/tasks/search` - Search tasks
- [ ] GET `/workspaces/{workspace_gid}/typeahead` - Typeahead search

---

## 2. Users

### Currently Implemented (8)
- ✅ GET `/users`
- ✅ GET `/users/{user_gid}`
- ✅ PUT `/users/{user_gid}`
- ✅ GET `/users/{user_gid}/favorites`
- ✅ GET `/users/{user_gid}/team_memberships`
- ✅ GET `/users/{user_gid}/teams`
- ✅ GET `/users/{user_gid}/user_task_list`
- ✅ GET `/users/{user_gid}/workspace_memberships`

### Pending (0)
- [x] GET `/users/{user_gid}/favorites` - Get user favorites
- [x] GET `/users/{user_gid}/team_memberships` - Get user team memberships
- [x] GET `/users/{user_gid}/teams` - Get user teams
- [x] GET `/users/{user_gid}/user_task_list` - Get user task list
- [x] GET `/users/{user_gid}/workspace_memberships` - Get user workspace memberships

---

## 3. Projects

### Currently Implemented (21)
- ✅ GET `/projects`
- ✅ GET `/projects/{project_gid}`
- ✅ POST `/projects`
- ✅ PUT `/projects/{project_gid}`
- ✅ DELETE `/projects/{project_gid}`
- ✅ POST `/projects/{project_gid}/duplicate`
- ✅ POST `/projects/{project_gid}/addMembers`
- ✅ POST `/projects/{project_gid}/removeMembers`
- ✅ POST `/projects/{project_gid}/addFollowers`
- ✅ POST `/projects/{project_gid}/removeFollowers`
- ✅ GET `/projects/{project_gid}/sections`
- ✅ GET `/projects/{project_gid}/tasks`
- ✅ GET `/projects/{project_gid}/custom_field_settings`
- ✅ GET `/projects/{project_gid}/project_memberships`
- ✅ GET `/projects/{project_gid}/project_statuses`
- ✅ GET `/projects/{project_gid}/task_counts`
- ✅ POST `/projects/{project_gid}/sections/insert`
- ✅ POST `/projects/{project_gid}/addCustomFieldSetting`
- ✅ POST `/projects/{project_gid}/removeCustomFieldSetting`
- ✅ POST `/projects/{project_gid}/project_briefs`
- ✅ POST `/projects/{project_gid}/saveAsTemplate`

### Pending (0)
- ✅ POST `/projects/{project_gid}/project_briefs` - Create project brief
- ✅ POST `/projects/{project_gid}/sections/insert` - Insert section
- ✅ POST `/projects/{project_gid}/addCustomFieldSetting` - Add custom field setting
- ✅ POST `/projects/{project_gid}/removeCustomFieldSetting` - Remove custom field setting
- ✅ POST `/projects/{project_gid}/saveAsTemplate` - Save as template

---

## 4. Tasks

### Currently Implemented (24)
- ✅ GET `/tasks`
- ✅ GET `/tasks/{task_gid}`
- ✅ POST `/tasks`
- ✅ PUT `/tasks/{task_gid}`
- ✅ DELETE `/tasks/{task_gid}`
- ✅ POST `/tasks/{task_gid}/duplicate`
- ✅ GET `/tasks/{task_gid}/projects`
- ✅ GET `/tasks/{task_gid}/subtasks`
- ✅ GET `/tasks/{task_gid}/dependencies`
- ✅ GET `/tasks/{task_gid}/dependents`
- ✅ GET `/tasks/{task_gid}/stories`
- ✅ GET `/tasks/{task_gid}/tags`
- ✅ GET `/tasks/{task_gid}/time_tracking_entries`
- ✅ POST `/tasks/{task_gid}/addProject`
- ✅ POST `/tasks/{task_gid}/removeProject`
- ✅ POST `/tasks/{task_gid}/addTag`
- ✅ POST `/tasks/{task_gid}/removeTag`
- ✅ POST `/tasks/{task_gid}/addFollowers`
- ✅ POST `/tasks/{task_gid}/removeFollowers`
- ✅ POST `/tasks/{task_gid}/setParent`
- ✅ POST `/tasks/{task_gid}/addDependencies`
- ✅ POST `/tasks/{task_gid}/removeDependencies`
- ✅ POST `/tasks/{task_gid}/addDependents`
- ✅ POST `/tasks/{task_gid}/removeDependents`

### Pending (0)
- All high-priority and medium-priority endpoints implemented.

---

## 5. Teams

### Currently Implemented (12)
- ✅ GET `/teams`
- ✅ GET `/teams/{team_gid}`
- ✅ POST `/teams`
- ✅ PUT `/teams/{team_gid}`
- ✅ DELETE `/teams/{team_gid}`
- ✅ POST `/teams/{team_gid}/addUser`
- ✅ POST `/teams/{team_gid}/removeUser`
- ✅ GET `/teams/{team_gid}/users`
- ✅ GET `/teams/{team_gid}/projects`
- ✅ GET `/teams/{team_gid}/team_memberships`
- ✅ GET `/teams/{team_gid}/custom_field_settings`
- ✅ GET `/teams/{team_gid}/project_templates`

### Pending (0)
- All high-priority and medium-priority endpoints implemented.

---

## 6. Sections

### Currently Implemented (6)
- ✅ GET `/sections`
- ✅ GET `/sections/{section_gid}`
- ✅ POST `/sections`
- ✅ PUT `/sections/{section_gid}`
- ✅ DELETE `/sections/{section_gid}`
- ✅ POST `/sections/{section_gid}/addTask`
- ✅ GET `/sections/{section_gid}/tasks`

### Pending (0)
- All high-priority and medium-priority endpoints implemented.

---

## 7. Attachments

### Currently Implemented (5)
- ✅ GET `/attachments`
- ✅ GET `/attachments/{attachment_gid}`
- ✅ POST `/attachments`
- ✅ PUT `/attachments/{attachment_gid}`
- ✅ DELETE `/attachments/{attachment_gid}`

### Pending (0)
- ✅ All core endpoints implemented

---

## 8. Stories

### Currently Implemented (5)
- ✅ GET `/stories`
- ✅ GET `/stories/{story_gid}`
- ✅ POST `/stories`
- ✅ PUT `/stories/{story_gid}`
- ✅ DELETE `/stories/{story_gid}`

### Pending (0)
- ✅ All core endpoints implemented

---

## 9. Tags

### Currently Implemented (5)
- ✅ GET `/tags`
- ✅ GET `/tags/{tag_gid}`
- ✅ POST `/tags`
- ✅ PUT `/tags/{tag_gid}`
- ✅ DELETE `/tags/{tag_gid}`

### Pending (0)
- [x] GET `/tags/{tag_gid}/tasks` - Get tag tasks

---

## 10. Webhooks

### Currently Implemented (5)
- ✅ GET `/webhooks`
- ✅ GET `/webhooks/{webhook_gid}`
- ✅ POST `/webhooks`
- ✅ PUT `/webhooks/{webhook_gid}`
- ✅ DELETE `/webhooks/{webhook_gid}`

### Pending (0)
- ✅ All core endpoints implemented

---

## 11. Custom Fields

### Currently Implemented (5)
- ✅ GET `/custom_fields`
- ✅ GET `/custom_fields/{custom_field_gid}`
- ✅ POST `/custom_fields`
- ✅ PUT `/custom_fields/{custom_field_gid}`
- ✅ DELETE `/custom_fields/{custom_field_gid}`

### Pending (0)
- [x] GET `/custom_fields/{custom_field_gid}/enum_options` - Get enum options
- [x] POST `/custom_fields/{custom_field_gid}/enum_options` - Create enum option
- [x] POST `/custom_fields/{custom_field_gid}/enum_options/insert` - Insert enum option

---

## Summary

- **Total Implemented:** 115 endpoints (52 core + 25 high-priority + 15 medium-priority + 13 easy GET + 10 medium POST endpoints)
- **Total Pending:** 3 endpoints (3 search endpoints)
- **Total in Spec:** ~118 endpoints

### Priority Breakdown

**High Priority (Core Relationships - 25 endpoints):** ✅ COMPLETED
- Workspaces: `addUser`, `removeUser`, `events` (3) ✅
- Projects: `duplicate`, `addMembers`, `removeMembers`, `addFollowers`, `removeFollowers` (5) ✅
- Tasks: `duplicate`, `addProject`, `removeProject`, `addTag`, `removeTag`, `addFollowers`, `removeFollowers`, `subtasks`, `dependencies`, `dependents` (10) ✅
- Teams: `addUser`, `removeUser` (2) ✅
- Sections: `addTask` (1) ✅
- Tags: `tasks` (1) ✅
- Custom Fields: `enum_options` (3) ✅

**Medium Priority (List Endpoints - 15 endpoints):** ✅ COMPLETED
- Workspaces: `custom_fields`, `projects`, `tags`, `teams`, `workspace_memberships`, `audit_log_events` (6) ✅
- Users: `favorites`, `team_memberships`, `teams`, `user_task_list`, `workspace_memberships` (5) ✅
- Projects: `sections`, `tasks`, `custom_field_settings` (3) ✅
- Teams: `users` (1) ✅

**Lower Priority (Advanced Features - 24 endpoints):**
- Search endpoints
- Custom field settings management
- Project briefs, statuses, memberships
- Time tracking entries
- Task dependencies/dependents management
- Audit logs, typeahead, etc.

---

## Notes

- All endpoints must follow OpenAPI specification format
- Request bodies must use `{"data": {...}}` wrapper
- Response bodies must use `{"data": {...}}` wrapper
- All endpoints should include proper error handling
- All endpoints should support `opt_fields` and `opt_pretty` query parameters where applicable

