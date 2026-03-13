# Toast Notifications

Altassian uses [sonner](https://sonner.emilkowal.dev/) for lightweight, accessible toast notifications.

## Setup

The `<Toaster />` component is mounted in `src/main.tsx` at the app root. No additional provider is needed.

## Usage

```ts
import { toast } from '../lib/toast'

// Success
toast.success('Page saved')

// Error
toast.error('Failed to delete page')

// Info
toast.info('Comment deleted')

// With options
toast.success('Space created', { duration: 5000, description: 'You can start adding pages.' })
```

## Error helper

```ts
import { getErrorMessage } from '../lib/toast'

try {
  await api.createSpace(data)
} catch (err) {
  toast.error(getErrorMessage(err))
}
```

`getErrorMessage` extracts human-readable messages from Axios errors (field validation, detail strings) or falls back to `Error.message`.

## Where toasts are wired

| Flow | Type | File |
|------|------|------|
| Page create/update | success | `PageEditor.tsx` |
| Page delete | success | `PageView.tsx` |
| Comment add | success | `PageView.tsx` |
| Comment delete | info | `PageView.tsx` |
| File upload | success | `PageView.tsx` |
| Space create | success | `CreateSpace.tsx` |
| Space settings save | success | `SpaceSettings.tsx` |
| Space delete | success | `SpaceSettings.tsx` |
| Login success | success | `LoginPage.tsx` |
| Login failure | error | `LoginPage.tsx` |
| Registration success | success | `RegisterPage.tsx` |
| Registration failure | error | `RegisterPage.tsx` |
| Network error (no response) | error | `api/client.ts` |
| Server error (5xx) | error | `api/client.ts` |

## Configuration

Toaster options are set in `src/main.tsx`:

- **Position**: bottom-right
- **Auto-dismiss**: 3.5 seconds
- **Close button**: yes
- **Rich colors**: yes (green for success, red for error)
- **Theme**: follows system (light/dark)

## Accessibility

- Sonner renders an ARIA live region (`role="status"`, `aria-live="polite"`) so screen readers announce toasts.
- Hover/focus pauses the auto-dismiss timer.
- Close button is keyboard accessible.
