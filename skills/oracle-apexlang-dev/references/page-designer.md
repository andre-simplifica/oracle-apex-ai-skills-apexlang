# Page Designer

Use Page Designer when the task explicitly requests it or a supported operation is unavailable through APEXlang/public APIs. Coordinate with the canonical source workflow.

## Before Changing

- Confirm application, page, environment, and session.
- Read the project profile.
- Identify sibling/example pages when there is a visual pattern to follow.
- Confirm the request is small enough for Page Designer.

## Implementation

- Locate the correct region, item, button, column, process, or Dynamic Action.
- Inspect the source and fresh metadata; preserve concurrent Builder/source edits.
- Apply the change in Page Designer UI.
- Save the page.
- Avoid technical names in user-visible text.
- Prefer native APEX components when they solve the problem cleanly.
- Actively consider a package-backed Dynamic Content region when a branded or non-standard layout, coordinated filters, clickable dashboard actions, custom grouping, or print/export behavior would otherwise become rigid or duplicated. Follow [dynamic-content-regions.md](dynamic-content-regions.md).

## Before Closing

- Confirm the property was saved.
- Run the application.
- Validate runtime behavior.
- Test success and known failure cases when applicable.

After saving an authorized Builder change, export to a fresh APEXlang candidate, validate and reconcile the canonical tree before later source imports.
