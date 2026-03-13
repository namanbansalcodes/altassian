import {
  useState,
  useEffect,
  useCallback,
  useRef,
  useLayoutEffect,
} from 'react'
import { type Editor } from '@tiptap/react'
import {
  Heading1, Heading2, Heading3, Type, List, ListOrdered,
  CheckSquare, Quote, CodeSquare, Minus, Image, Table,
  Info, AtSign, FileText,
} from 'lucide-react'

// ─── Slash command definitions ───────────────────────────────
//
// HOW TO EXTEND:
// Add a new entry to the `slashCommands` array below. Each command needs:
//   id        – unique string identifier
//   label     – display name shown in the menu
//   description – short helper text shown below the label
//   icon      – a lucide-react icon component (or any (size: number) => JSX)
//   keywords  – array of search terms for fuzzy filtering (e.g. ['h1', 'title'])
//   execute   – function receiving the TipTap Editor instance; call editor.chain()...
//
// The menu automatically picks up new entries — no registration step needed.
// Commands are displayed in array order; group related items together.

export interface SlashCommand {
  id: string
  label: string
  description: string
  icon: React.ComponentType<{ size: number; className?: string }>
  keywords: string[]
  execute: (editor: Editor) => void
}

export const slashCommands: SlashCommand[] = [
  {
    id: 'heading1', label: 'Heading 1', description: 'Large section heading',
    icon: Heading1, keywords: ['h1', 'heading', 'title', 'large'],
    execute: (e) => e.chain().focus().toggleHeading({ level: 1 }).run(),
  },
  {
    id: 'heading2', label: 'Heading 2', description: 'Medium section heading',
    icon: Heading2, keywords: ['h2', 'heading', 'subtitle'],
    execute: (e) => e.chain().focus().toggleHeading({ level: 2 }).run(),
  },
  {
    id: 'heading3', label: 'Heading 3', description: 'Small section heading',
    icon: Heading3, keywords: ['h3', 'heading', 'small'],
    execute: (e) => e.chain().focus().toggleHeading({ level: 3 }).run(),
  },
  {
    id: 'paragraph', label: 'Paragraph', description: 'Plain text block',
    icon: Type, keywords: ['text', 'paragraph', 'plain', 'body'],
    execute: (e) => e.chain().focus().setParagraph().run(),
  },
  {
    id: 'bulletList', label: 'Bullet List', description: 'Unordered list',
    icon: List, keywords: ['bullet', 'unordered', 'list', 'ul'],
    execute: (e) => e.chain().focus().toggleBulletList().run(),
  },
  {
    id: 'orderedList', label: 'Ordered List', description: 'Numbered list',
    icon: ListOrdered, keywords: ['ordered', 'numbered', 'list', 'ol'],
    execute: (e) => e.chain().focus().toggleOrderedList().run(),
  },
  {
    id: 'taskList', label: 'Task List', description: 'Checklist / todo items',
    icon: CheckSquare, keywords: ['task', 'todo', 'check', 'checkbox'],
    execute: (e) => e.chain().focus().toggleTaskList().run(),
  },
  {
    id: 'blockquote', label: 'Quote', description: 'Block quotation',
    icon: Quote, keywords: ['quote', 'blockquote', 'callout'],
    execute: (e) => e.chain().focus().toggleBlockquote().run(),
  },
  {
    id: 'codeBlock', label: 'Code Block', description: 'Fenced code snippet',
    icon: CodeSquare, keywords: ['code', 'codeblock', 'snippet', 'pre'],
    execute: (e) => e.chain().focus().toggleCodeBlock().run(),
  },
  {
    id: 'divider', label: 'Divider', description: 'Horizontal rule',
    icon: Minus, keywords: ['divider', 'hr', 'line', 'separator', 'horizontal'],
    execute: (e) => e.chain().focus().setHorizontalRule().run(),
  },
  {
    id: 'image', label: 'Image', description: 'Upload or embed an image',
    icon: Image, keywords: ['image', 'img', 'picture', 'photo', 'upload'],
    execute: (e) => {
      const input = document.createElement('input')
      input.type = 'file'
      input.accept = 'image/*'
      input.onchange = () => {
        const file = input.files?.[0]
        if (file) {
          e.chain().focus().insertContent(`[Image: ${file.name}]`).run()
        }
      }
      input.click()
    },
  },
  {
    id: 'table', label: 'Table', description: 'Insert a 3×3 table',
    icon: Table, keywords: ['table', 'grid', 'spreadsheet'],
    execute: (e) => e.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run(),
  },
  {
    id: 'pageLink', label: 'Page Link', description: 'Link to another page',
    icon: FileText, keywords: ['page', 'link', 'wiki', 'internal', 'pagelink'],
    execute: (e) => {
      const url = window.prompt('Enter page URL or slug:')
      if (url?.trim()) {
        e.chain().focus().setLink({ href: url.trim() }).run()
      }
    },
  },
  {
    id: 'callout', label: 'Callout', description: 'Info callout block',
    icon: Info, keywords: ['callout', 'info', 'note', 'tip', 'warning'],
    execute: (e) => e.chain().focus().toggleBlockquote().run(),
  },
  {
    id: 'mention', label: 'Mention', description: 'Mention a user',
    icon: AtSign, keywords: ['mention', 'user', 'at', 'person'],
    execute: (e) => e.chain().focus().insertContent('@').run(),
  },
]

// ─── Fuzzy filter ────────────────────────────────────────────

export function filterCommands(query: string): SlashCommand[] {
  if (!query) return slashCommands
  const q = query.toLowerCase()
  return slashCommands.filter((cmd) => {
    if (cmd.label.toLowerCase().includes(q)) return true
    if (cmd.description.toLowerCase().includes(q)) return true
    return cmd.keywords.some((kw) => kw.includes(q))
  })
}

// ─── Viewport clamping helper ────────────────────────────────

function clampToViewport(
  el: HTMLElement,
  desired: { top: number; left: number },
  container: HTMLElement,
): { top: number; left: number } {
  const rect = el.getBoundingClientRect()
  const containerRect = container.getBoundingClientRect()
  const menuWidth = rect.width || 288 // fallback to w-72
  const menuHeight = rect.height || 320

  let { top, left } = desired

  // Clamp right edge
  const maxLeft = containerRect.width - menuWidth - 8
  if (left > maxLeft) left = Math.max(0, maxLeft)

  // Clamp bottom edge — flip above cursor if no room below
  const absoluteBottom = containerRect.top + top + menuHeight
  if (absoluteBottom > window.innerHeight - 8) {
    // Try positioning above: subtract menu height + some offset
    top = Math.max(0, top - menuHeight - 32)
  }

  // Clamp left edge
  if (left < 0) left = 0

  return { top, left }
}

// ─── SlashMenu overlay component ─────────────────────────────

interface SlashMenuProps {
  editor: Editor
}

export default function SlashMenu({ editor }: SlashMenuProps) {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const [position, setPosition] = useState<{ top: number; left: number } | null>(null)
  const menuRef = useRef<HTMLDivElement>(null)
  const slashPosRef = useRef<number | null>(null)

  const filtered = filterCommands(query)

  const close = useCallback(() => {
    setOpen(false)
    setQuery('')
    setSelectedIndex(0)
    slashPosRef.current = null
  }, [])

  const executeCommand = useCallback(
    (cmd: SlashCommand) => {
      if (slashPosRef.current !== null) {
        const from = slashPosRef.current
        const to = editor.state.selection.from
        editor.chain().focus().deleteRange({ from, to }).run()
      }
      cmd.execute(editor)
      close()
    },
    [editor, close],
  )

  // Listen to editor transactions to detect "/" input
  useEffect(() => {
    const handleUpdate = () => {
      const { state } = editor
      const { from } = state.selection
      const $from = state.doc.resolve(from)
      const textBefore = $from.parent.textContent.slice(0, $from.parentOffset)

      const slashMatch = textBefore.match(/(^|\s)\/([\w]*)$/)
      if (slashMatch) {
        const slashOffset = $from.parentOffset - slashMatch[0].length + slashMatch[1].length
        const absoluteSlashPos = from - $from.parentOffset + slashOffset
        slashPosRef.current = absoluteSlashPos
        setQuery(slashMatch[2])
        setSelectedIndex(0)

        const coords = editor.view.coordsAtPos(from)
        const editorRect = editor.view.dom.getBoundingClientRect()
        setPosition({
          top: coords.bottom - editorRect.top + 4,
          left: coords.left - editorRect.left,
        })
        setOpen(true)
      } else if (open) {
        close()
      }
    }

    editor.on('update', handleUpdate)
    editor.on('selectionUpdate', handleUpdate)
    return () => {
      editor.off('update', handleUpdate)
      editor.off('selectionUpdate', handleUpdate)
    }
  }, [editor, open, close])

  // Handle keyboard navigation
  useEffect(() => {
    if (!open) return

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'ArrowDown') {
        event.preventDefault()
        setSelectedIndex((prev) => (prev + 1) % filtered.length)
      } else if (event.key === 'ArrowUp') {
        event.preventDefault()
        setSelectedIndex((prev) => (prev - 1 + filtered.length) % filtered.length)
      } else if (event.key === 'Enter') {
        event.preventDefault()
        if (filtered[selectedIndex]) {
          executeCommand(filtered[selectedIndex])
        }
      } else if (event.key === 'Escape') {
        event.preventDefault()
        close()
      }
    }

    document.addEventListener('keydown', handleKeyDown, true)
    return () => document.removeEventListener('keydown', handleKeyDown, true)
  }, [open, filtered, selectedIndex, executeCommand, close])

  // Scroll selected item into view
  useEffect(() => {
    if (!open || !menuRef.current) return
    const item = menuRef.current.querySelector(`[data-index="${selectedIndex}"]`)
    item?.scrollIntoView({ block: 'nearest' })
  }, [selectedIndex, open])

  // Clamp menu position to viewport after render
  useLayoutEffect(() => {
    if (!open || !position || !menuRef.current) return
    const el = menuRef.current
    const container = el.offsetParent as HTMLElement | null
    if (!container) return

    const clamped = clampToViewport(el, position, container)
    if (clamped.top !== position.top || clamped.left !== position.left) {
      el.style.top = `${clamped.top}px`
      el.style.left = `${clamped.left}px`
    }
  }, [open, position, filtered.length])

  if (!open || !position || filtered.length === 0) return null

  return (
    <div
      ref={menuRef}
      role="listbox"
      aria-label="Slash commands"
      className="absolute z-50 w-64 sm:w-72 max-w-[calc(100vw-1rem)] max-h-[min(80vh,20rem)] overflow-y-auto bg-white dark:bg-gray-900 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 py-1"
      style={{ top: position.top, left: position.left }}
    >
      {filtered.map((cmd, index) => {
        const Icon = cmd.icon
        const selected = index === selectedIndex
        return (
          <button
            key={cmd.id}
            type="button"
            role="option"
            aria-selected={selected}
            data-index={index}
            onClick={() => executeCommand(cmd)}
            onMouseEnter={() => setSelectedIndex(index)}
            className={`w-full flex items-center gap-3 px-3 py-2 text-left transition-colors ${
              selected
                ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800'
            }`}
          >
            <span
              className={`flex-shrink-0 p-1.5 rounded ${
                selected
                  ? 'bg-blue-100 dark:bg-blue-800 text-blue-600 dark:text-blue-300'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400'
              }`}
            >
              <Icon size={16} />
            </span>
            <span className="min-w-0">
              <span className="block text-sm font-medium truncate">{cmd.label}</span>
              <span className="block text-xs text-gray-500 dark:text-gray-400 truncate">
                {cmd.description}
              </span>
            </span>
          </button>
        )
      })}
    </div>
  )
}
