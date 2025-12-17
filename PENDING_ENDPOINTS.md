# Pending API Endpoints

This file tracks all unimplemented endpoints from the OpenAPI specification for the 11 core entities.
As endpoints are implemented, they should be removed from this list.

**Last Updated:** 2025-12-17

---

## 1. Workspaces

### Currently Implemented (4)
- ✅ GET `/workspaces`
- ✅ GET `/workspaces/{workspace_gid}`
- ✅ PUT `/workspaces/{workspace_gid}`
- ✅ GET `/workspaces/{workspace_gid}/users`

### Pending (9)
- [x] POST `/workspaces/{workspace_gid}/addUser` - Add user to workspace
- [x] POST `/workspaces/{workspace_gid}/removeUser` - Remove user from workspace
- [x] GET `/workspaces/{workspace_gid}/events` - Get workspace events
- [ ] GET `/workspaces/{workspace_gid}/audit_log_events` - Get audit log events
- [ ] GET `/workspaces/{workspace_gid}/custom_fields` - Get workspace custom fields
- [ ] GET `/workspaces/{workspace_gid}/projects` - Get workspace projects
- [ ] GET `/workspaces/{workspace_gid}/tags` - Get workspace tags
- [ ] GET `/workspaces/{workspace_gid}/teams` - Get workspace teams
- [ ] GET `/workspaces/{workspace_gid}/tasks/custom_id/{custom_id}` - Get task by custom ID
- [ ] GET `/workspaces/{workspace_gid}/tasks/search` - Search tasks
- [ ] GET `/workspaces/{workspace_gid}/typeahead` - Typeahead search
- [ ] GET `/workspaces/{workspace_gid}/workspace_memberships` - Get workspace memberships

---

## 2. Users

### Currently Implemented (3)
- ✅ GET `/users`
- ✅ GET `/users/{user_gid}`
- ✅ PUT `/users/{user_gid}`

### Pending (5)
- [ ] GET `/users/{user_gid}/favorites` - Get user favorites
- [ ] GET `/users/{user_gid}/team_memberships` - Get user team memberships
- [ ] GET `/users/{user_gid}/teams` - Get user teams
- [ ] GET `/users/{user_gid}/user_task_list` - Get user task list
- [ ] GET `/users/{user_gid}/workspace_memberships` - Get user workspace memberships

---

## 3. Projects

### Currently Implemented (5)
- ✅ GET `/projects`
- ✅ GET `/projects/{project_gid}`
- ✅ POST `/projects`
- ✅ PUT `/projects/{project_gid}`
- ✅ DELETE `/projects/{project_gid}`

### Pending (10)
- [x] POST `/projects/{project_gid}/duplicate` - Duplicate project
- [ ] GET `/projects/{project_gid}/custom_field_settings` - Get custom field settings
- [ ] GET `/projects/{project_gid}/project_briefs` - Get project briefs
- [ ] GET `/projects/{project_gid}/project_memberships` - Get project memberships
- [ ] GET `/projects/{project_gid}/project_statuses` - Get project statuses
- [ ] GET `/projects/{project_gid}/sections` - Get project sections
- [ ] POST `/projects/{project_gid}/sections/insert` - Insert section
- [ ] GET `/projects/{project_gid}/tasks` - Get project tasks
- [ ] GET `/projects/{project_gid}/task_counts` - Get task counts
- [ ] POST `/projects/{project_gid}/addCustomFieldSetting` - Add custom field setting
- [ ] POST `/projects/{project_gid}/removeCustomFieldSetting` - Remove custom field setting
- [x] POST `/projects/{project_gid}/addMembers` - Add members
- [x] POST `/projects/{project_gid}/removeMembers` - Remove members
- [x] POST `/projects/{project_gid}/addFollowers` - Add followers
- [x] POST `/projects/{project_gid}/removeFollowers` - Remove followers
- [ ] POST `/projects/{project_gid}/saveAsTemplate` - Save as template

---

## 4. Tasks

### Currently Implemented (5)
- ✅ GET `/tasks`
- ✅ GET `/tasks/{task_gid}`
- ✅ POST `/tasks`
- ✅ PUT `/tasks/{task_gid}`
- ✅ DELETE `/tasks/{task_gid}`

### Pending (10)
- [x] POST `/tasks/{task_gid}/duplicate` - Duplicate task
- [ ] GET `/tasks/{task_gid}/projects` - Get task projects
- [x] GET `/tasks/{task_gid}/subtasks` - Get subtasks
- [ ] POST `/tasks/{task_gid}/setParent` - Set parent task
- [x] GET `/tasks/{task_gid}/dependencies` - Get dependencies
- [ ] POST `/tasks/{task_gid}/addDependencies` - Add dependencies
- [ ] POST `/tasks/{task_gid}/removeDependencies` - Remove dependencies
- [x] GET `/tasks/{task_gid}/dependents` - Get dependents
- [ ] POST `/tasks/{task_gid}/addDependents` - Add dependents
- [ ] POST `/tasks/{task_gid}/removeDependents` - Remove dependents
- [ ] GET `/tasks/{task_gid}/stories` - Get task stories
- [ ] GET `/tasks/{task_gid}/tags` - Get task tags
- [x] POST `/tasks/{task_gid}/addProject` - Add task to project
- [x] POST `/tasks/{task_gid}/removeProject` - Remove task from project
- [x] POST `/tasks/{task_gid}/addTag` - Add tag to task
- [x] POST `/tasks/{task_gid}/removeTag` - Remove tag from task
- [x] POST `/tasks/{task_gid}/addFollowers` - Add followers
- [x] POST `/tasks/{task_gid}/removeFollowers` - Remove followers
- [ ] GET `/tasks/{task_gid}/time_tracking_entries` - Get time tracking entries

---

## 5. Teams

### Currently Implemented (5)
- ✅ GET `/teams`
- ✅ GET `/teams/{team_gid}`
- ✅ POST `/teams`
- ✅ PUT `/teams/{team_gid}`
- ✅ DELETE `/teams/{team_gid}`

### Pending (5)
- [ ] GET `/teams/{team_gid}/custom_field_settings` - Get custom field settings
- [ ] GET `/teams/{team_gid}/project_templates` - Get project templates
- [ ] GET `/teams/{team_gid}/projects` - Get team projects
- [ ] GET `/teams/{team_gid}/team_memberships` - Get team memberships
- [ ] GET `/teams/{team_gid}/users` - Get team users
- [x] POST `/teams/{team_gid}/addUser` - Add user to team
- [x] POST `/teams/{team_gid}/removeUser` - Remove user from team

---

## 6. Sections

### Currently Implemented (5)
- ✅ GET `/sections`
- ✅ GET `/sections/{section_gid}`
- ✅ POST `/sections`
- ✅ PUT `/sections/{section_gid}`
- ✅ DELETE `/sections/{section_gid}`

### Pending (1)
- [ ] GET `/sections/{section_gid}/tasks` - Get section tasks
- [x] POST `/sections/{section_gid}/addTask` - Add task to section

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

- **Total Implemented:** 77 endpoints (52 core + 25 high-priority)
- **Total Pending:** 39 endpoints
- **Total in Spec:** ~116 endpoints

### Priority Breakdown

**High Priority (Core Relationships - 25 endpoints):** ✅ COMPLETED
- Workspaces: `addUser`, `removeUser`, `events` (3) ✅
- Projects: `duplicate`, `addMembers`, `removeMembers`, `addFollowers`, `removeFollowers` (5) ✅
- Tasks: `duplicate`, `addProject`, `removeProject`, `addTag`, `removeTag`, `addFollowers`, `removeFollowers`, `subtasks`, `dependencies`, `dependents` (10) ✅
- Teams: `addUser`, `removeUser` (2) ✅
- Sections: `addTask` (1) ✅
- Tags: `tasks` (1) ✅
- Custom Fields: `enum_options` (3) ✅

**Medium Priority (List Endpoints - 15 endpoints):**
- Relationship GET endpoints for listing related resources

**Lower Priority (Advanced Features - 24 endpoints):**
- Search endpoints
- Custom field settings management
- Project briefs, statuses, memberships
- Time tracking entries
- User favorites, memberships
- Audit logs, typeahead, etc.

---

## Notes

- All endpoints must follow OpenAPI specification format
- Request bodies must use `{"data": {...}}` wrapper
- Response bodies must use `{"data": {...}}` wrapper
- All endpoints should include proper error handling
- All endpoints should support `opt_fields` and `opt_pretty` query parameters where applicable

