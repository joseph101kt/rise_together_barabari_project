# seed_data.json — Format Reference

The seed script (`app/scripts/seed.py`) reads a single file called `seed_data.json`
from the same directory. Copy `seed_data.example.json` to `seed_data.json` and edit it,
or give this document to an LLM and ask it to generate the JSON for you.

Running the seed:

```
python -m app.scripts.seed
```

The script is safe to run multiple times — it uses get-or-create so it will never
duplicate an existing row. Every link has Open Graph metadata fetched at seed time.

---

## Project Context

Rise Together is a learning platform for students at government engineering colleges
in India. The platform organises learning content into a tree of modules. Students
(learners) track their progress through modules by submitting links (GitHub repos,
YouTube demos, etc.) for designated submission slots inside each module.

---

## Top-level shape

```json
{
  "skills":  [ ...SkillEntry ],
  "users":   [ ...UserEntry ],
  "modules": [ ...ModuleEntry ]
}
```

All three arrays are required. Order matters only within `modules` (tree order).

---

## SkillEntry

```json
{
  "name": "Python",
  "slug": "python"
}
```

| Field  | Type   | Required | Notes                                  |
|--------|--------|----------|----------------------------------------|
| `name` | string | yes      | Display name shown in the UI           |
| `slug` | string | yes      | Unique URL-safe identifier, kebab-case |

Skills are referenced by slug in `UserEntry.skills` and `ModuleEntry.skills`.

---

## UserEntry

```json
{
  "email":    "priya@example.com",
  "name":     "Priya Sharma",
  "password": "password123",
  "role":     "learner",

  "profile": {
    "headline": "CS student at Govt Engineering College, Nagpur",
    "bio":      "First-gen tech student trying to break into the industry."
  },

  "education": [
    {
      "institution":    "Government Engineering College, Nagpur",
      "degree":         "B.E.",
      "field_of_study": "Computer Science",
      "start_date":     "2021-07-01",
      "end_date":       null,
      "description":    null
    }
  ],

  "skills": ["python", "git", "html-css"],

  "profile_links": [
    {
      "title":     "GitHub",
      "url":       "https://github.com/priya",
      "link_type": "github"
    }
  ]
}
```

| Field           | Type            | Required | Notes                                                |
|-----------------|-----------------|----------|------------------------------------------------------|
| `email`         | string          | yes      | Must be unique. Used as the key in module `created_by` |
| `name`          | string          | yes      |                                                      |
| `password`      | string          | yes      | Stored as bcrypt hash                                |
| `role`          | enum            | yes      | `"learner"`, `"mentor"`, or `"admin"`                |
| `profile`       | object          | no       | `headline` and `bio`, both optional strings          |
| `education`     | array           | no       | All fields except `institution` are optional         |
| `skills`        | array of slugs  | no       | Must match slugs defined in the `skills` array       |
| `profile_links` | array           | no       | See LinkType enum below for valid `link_type` values |

You always need at least one `admin` user because modules reference a `created_by` email
and that user must exist in this file.

---

## ModuleEntry

Modules are a tree. Root modules sit directly in the top-level `"modules"` array.
Children go inside a `"children"` array on their parent.

```json
{
  "title":                      "Build Your Online Presence",
  "module_type":                "module",
  "description":                "Set up your GitHub and LinkedIn so recruiters can find you.",
  "estimated_completion_time":  "3 days",
  "created_by":                 "admin@risetogether.in",
  "order_index":                0,
  "skills":                     ["git", "linkedin"],
  "links":                      [ ...LinkEntry ],
  "children":                   [ ...ModuleEntry ]
}
```

| Field                        | Type           | Required | Notes                                                       |
|------------------------------|----------------|----------|-------------------------------------------------------------|
| `title`                      | string         | yes      | Unique within its parent                                    |
| `module_type`                | enum           | yes      | See ModuleType enum below                                   |
| `description`                | string         | no       |                                                             |
| `estimated_completion_time`  | string         | no       | Free text, e.g. `"3 days"`, `"2 weeks"`                     |
| `created_by`                 | string (email) | yes      | Must match an email in the `users` array                    |
| `order_index`                | integer        | yes      | Position among siblings. Must be unique per parent.         |
| `skills`                     | array of slugs | no       | Tags this module as teaching these skills                   |
| `links`                      | array          | no       | See LinkEntry below                                         |
| `children`                   | array          | no       | Nested ModuleEntry objects                                  |

### ModuleType enum

| Value          | Use case                                                    |
|----------------|-------------------------------------------------------------|
| `"path"`       | Top-level grouping (e.g. "Getting Job-Ready")               |
| `"module"`     | A themed unit of content with resources and submissions     |
| `"lesson"`     | A single focused topic, usually no submission               |
| `"assignment"` | Task-focused, usually has one or more submission slots      |
| `"project"`    | Larger build task, typically multiple submission slots      |
| `"milestone"`  | A checkpoint with no content, marks completion of a stage  |

---

## LinkEntry (inside a module)

Each link in a module is either a **resource** (something to read/watch) or a
**submission slot** (something the learner must submit a URL for).

```json
{
  "title":         "Submit your GitHub profile link",
  "url":           "https://github.com",
  "link_type":     "submission",
  "sub_link_type": "github",
  "order_index":   2
}
```

| Field           | Type    | Required | Notes                                                                 |
|-----------------|---------|----------|-----------------------------------------------------------------------|
| `title`         | string  | yes      | Shown to the learner                                                  |
| `url`           | string  | yes      | For resources: the actual URL. For submissions: a placeholder domain is fine (e.g. `https://github.com`) because the learner supplies their own URL at runtime |
| `link_type`     | enum    | yes      | See LinkType enum below                                               |
| `sub_link_type` | enum    | no       | Only set when `link_type` is `"submission"`. Constrains what kind of URL the learner must submit. Omit or set to `null` to allow any URL. |
| `order_index`   | integer | yes      | Position of this link within the module. Must be unique per module.   |

### LinkType enum

| Value          | Use case                                              |
|----------------|-------------------------------------------------------|
| `"resources"`  | Reading material, tutorials, docs — no submission     |
| `"submission"` | A slot the learner fills in with their own URL        |
| `"github"`     | A GitHub link on a user profile (profile links only)  |
| `"portfolio"`  | A portfolio link on a user profile                    |
| `"projects"`   | A projects link on a user profile                     |
| `"other"`      | Anything else                                         |

### SubLinkType enum

Only relevant when `link_type` is `"submission"`.

| Value           | What the learner must submit           |
|-----------------|----------------------------------------|
| `"github"`      | A github.com URL                       |
| `"youtube"`     | A youtube.com URL                      |
| `"google_drive"`| A drive.google.com URL                 |
| `"figma"`       | A figma.com URL                        |
| `"other"`       | Any URL (but signals an expected type) |

Omit `sub_link_type` entirely (or set it to `null`) if any URL is acceptable.

---

## Completion logic

A learner's module status flips to `completed` automatically when they have submitted
a URL for **every** link in that module whose `link_type` is `"submission"`.
Resource links are ignored for completion tracking.
A module with no submission slots can never be marked completed by the learner.

---

## Tips for LLM generation

When asking an LLM to generate `seed_data.json`:

- Tell it the target audience: government engineering college students in India trying
  to get their first tech job.
- Specify the learning path topic (e.g. "web development", "data science", "backend").
- Ask for at least one `path` at the root, with 3–5 `module` children each containing
  1–3 resource links and 1–2 submission slots.
- Remind it that `order_index` must be unique per parent (0, 1, 2 … not repeated).
- Remind it that every `created_by` value must match an email in the `users` array.
- Remind it that submission slot URLs can just be the root domain (e.g. `https://github.com`)
  since the learner's real URL is submitted at runtime.