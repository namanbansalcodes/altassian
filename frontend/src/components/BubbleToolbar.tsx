import { useState, useEffect, useCallback, useRef } from 'react'
import { BubbleMenuPlugin } from '@tiptap/extension-bubble-menu'
import type { Editor } from '@tiptap/react'
import {
  Bold, Italic, Underline, Strikethrough, Code, Link, Link2Off,
  Heading1, Heading2, Heading3,
  List, ListOrdered, Quote, CodeSquare,
  AlignLeft, AlignCenter, AlignRight,
  RemoveFormatting, Undo, Redo,
} from 'lucide-react'

interface BubbleToolbarProps {
  editor: Editor
}

interface ToolbarAction {
  icon: React.ComponentType<{ size: number }>
  label: string
  shortcut?: string
  isActive: () => boolean
  run: () => void
}

function ToolbarButton({
  action,
  index,
  focused,
  onFocus,
}: {
  action: ToolbarAction
  index: number
  focused: boolean
  onFocus: (i: number) => void
}) {
  const Icon = action.icon
  const active = action.isActive()
  const title = action.shortcut
    ? `${action.label} (${action.shortcut})`
    : action.label
  const ref = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    if (focused) ref.current?.focus()
  }, [focused])

  return (
    <button
      ref={ref}
      type="button"
      role="menuitem"
      tabIndex={focused ? 0 : -1}
      onClick={action.run}
      onFocus={() => onFocus(index)}
      title={title}
      aria-label={action.label}
      aria-pressed={active}
      className={`p-1.5 rounded transition-colors ${
        active
          ? 'bg-blue-600 text-white'
          : 'text-gray-200 hover:bg-white/10 hover:text-white'
      }`}
    >
      <Icon size={15} />
    </button>
  )
}

function Divider() {
  return <div className="w-px h-5 bg-white/20 mx-0.5" aria-hidden="true" />
}

export default function BubbleToolbar({ editor }: BubbleToolbarProps) {
  const [linkInput, setLinkInput] = useState('')
  const [showLinkForm, setShowLinkForm] = useState(false)
  const [focusedIndex, setFocusedIndex] = useState(-1)
  const menuRef = useRef<HTMLDivElement>(null)

  const chain = useCallback(
    () => editor.chain().focus(),
    [editor],
  )

  // Register the BubbleMenuPlugin to show/hide/position the menu element
  useEffect(() => {
    const el = menuRef.current
    if (!el) return

    const plugin = BubbleMenuPlugin({
      pluginKey: 'bubbleToolbar',
      editor,
      element: el,
      shouldShow: ({ state, from, to }) => {
        if (from === to) return false
        const { $from } = state.selection
        if ($from.parent.type.name === 'codeBlock') return false
        return true
      },
      options: {
        placement: 'top',
        offset: { mainAxis: 8, crossAxis: 0 },
      },
    })

    editor.registerPlugin(plugin)
    return () => {
      editor.unregisterPlugin('bubbleToolbar')
    }
  }, [editor])

  const openLinkForm = useCallback(() => {
    const existing = editor.getAttributes('link').href as string | undefined
    setLinkInput(existing ?? '')
    setShowLinkForm(true)
  }, [editor])

  const applyLink = useCallback(() => {
    if (linkInput.trim()) {
      chain().setLink({ href: linkInput.trim() }).run()
    } else {
      chain().unsetLink().run()
    }
    setShowLinkForm(false)
    setLinkInput('')
  }, [chain, linkInput])

  const cancelLink = useCallback(() => {
    setShowLinkForm(false)
    setLinkInput('')
  }, [])

  const actions: (ToolbarAction | 'divider')[] = [
    {
      icon: Bold, label: 'Bold', shortcut: 'Ctrl+B',
      isActive: () => editor.isActive('bold'),
      run: () => chain().toggleBold().run(),
    },
    {
      icon: Italic, label: 'Italic', shortcut: 'Ctrl+I',
      isActive: () => editor.isActive('italic'),
      run: () => chain().toggleItalic().run(),
    },
    {
      icon: Underline, label: 'Underline', shortcut: 'Ctrl+U',
      isActive: () => editor.isActive('underline'),
      run: () => chain().toggleUnderline().run(),
    },
    {
      icon: Strikethrough, label: 'Strikethrough', shortcut: 'Ctrl+Shift+S',
      isActive: () => editor.isActive('strike'),
      run: () => chain().toggleStrike().run(),
    },
    {
      icon: Code, label: 'Inline Code', shortcut: 'Ctrl+E',
      isActive: () => editor.isActive('code'),
      run: () => chain().toggleCode().run(),
    },
    {
      icon: editor.isActive('link') ? Link2Off : Link,
      label: editor.isActive('link') ? 'Remove Link' : 'Add Link',
      shortcut: 'Ctrl+K',
      isActive: () => editor.isActive('link'),
      run: editor.isActive('link')
        ? () => chain().unsetLink().run()
        : openLinkForm,
    },
    'divider',
    {
      icon: Heading1, label: 'Heading 1',
      isActive: () => editor.isActive('heading', { level: 1 }),
      run: () => chain().toggleHeading({ level: 1 }).run(),
    },
    {
      icon: Heading2, label: 'Heading 2',
      isActive: () => editor.isActive('heading', { level: 2 }),
      run: () => chain().toggleHeading({ level: 2 }).run(),
    },
    {
      icon: Heading3, label: 'Heading 3',
      isActive: () => editor.isActive('heading', { level: 3 }),
      run: () => chain().toggleHeading({ level: 3 }).run(),
    },
    'divider',
    {
      icon: List, label: 'Bullet List',
      isActive: () => editor.isActive('bulletList'),
      run: () => chain().toggleBulletList().run(),
    },
    {
      icon: ListOrdered, label: 'Ordered List',
      isActive: () => editor.isActive('orderedList'),
      run: () => chain().toggleOrderedList().run(),
    },
    {
      icon: Quote, label: 'Blockquote',
      isActive: () => editor.isActive('blockquote'),
      run: () => chain().toggleBlockquote().run(),
    },
    {
      icon: CodeSquare, label: 'Code Block',
      isActive: () => editor.isActive('codeBlock'),
      run: () => chain().toggleCodeBlock().run(),
    },
    'divider',
    {
      icon: AlignLeft, label: 'Align Left',
      isActive: () => editor.isActive({ textAlign: 'left' }),
      run: () => chain().setTextAlign('left').run(),
    },
    {
      icon: AlignCenter, label: 'Align Center',
      isActive: () => editor.isActive({ textAlign: 'center' }),
      run: () => chain().setTextAlign('center').run(),
    },
    {
      icon: AlignRight, label: 'Align Right',
      isActive: () => editor.isActive({ textAlign: 'right' }),
      run: () => chain().setTextAlign('right').run(),
    },
    'divider',
    {
      icon: Undo, label: 'Undo', shortcut: 'Ctrl+Z',
      isActive: () => false,
      run: () => chain().undo().run(),
    },
    {
      icon: Redo, label: 'Redo', shortcut: 'Ctrl+Shift+Z',
      isActive: () => false,
      run: () => chain().redo().run(),
    },
    'divider',
    {
      icon: RemoveFormatting, label: 'Clear Formatting',
      isActive: () => false,
      run: () => chain().clearNodes().unsetAllMarks().run(),
    },
  ]

  // Build a flat list of button indices (skipping dividers) for arrow key nav
  const buttonActions = actions.filter((a): a is ToolbarAction => a !== 'divider')
  const buttonCount = buttonActions.length

  const handleToolbarKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault()
        editor.commands.focus()
        setFocusedIndex(-1)
        return
      }
      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
        e.preventDefault()
        setFocusedIndex((prev) => {
          const next = prev < 0 ? 0 : (prev + 1) % buttonCount
          return next
        })
      }
      if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
        e.preventDefault()
        setFocusedIndex((prev) => {
          const next = prev <= 0 ? buttonCount - 1 : prev - 1
          return next
        })
      }
    },
    [editor, buttonCount],
  )

  // Track the button index separately from the flat action index
  let buttonIdx = -1

  return (
    <div
      ref={menuRef}
      role="toolbar"
      aria-label="Text formatting"
      style={{ visibility: 'hidden', opacity: 0 }}
      className="flex items-center gap-0.5 px-1.5 py-1 bg-gray-900 rounded-lg shadow-xl border border-white/10 transition-opacity max-w-[calc(100vw-2rem)] overflow-x-auto scrollbar-thin"
      onKeyDown={handleToolbarKeyDown}
    >
      {showLinkForm ? (
        <div className="flex items-center gap-1 px-1">
          <input
            type="url"
            value={linkInput}
            onChange={(e) => setLinkInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') { e.preventDefault(); applyLink() }
              if (e.key === 'Escape') { e.preventDefault(); cancelLink() }
            }}
            placeholder="https://…"
            aria-label="Link URL"
            autoFocus
            className="w-44 sm:w-48 px-2 py-1 text-xs bg-white/10 text-white rounded border border-white/20 outline-none focus:border-blue-400 placeholder-gray-400"
          />
          <button
            type="button"
            onClick={applyLink}
            className="px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Apply
          </button>
          <button
            type="button"
            onClick={cancelLink}
            className="px-2 py-1 text-xs text-gray-300 hover:text-white"
          >
            Cancel
          </button>
        </div>
      ) : (
        actions.map((action, i) => {
          if (action === 'divider') {
            return <Divider key={`d-${i}`} />
          }
          buttonIdx++
          return (
            <ToolbarButton
              key={action.label}
              action={action}
              index={buttonIdx}
              focused={focusedIndex === buttonIdx}
              onFocus={setFocusedIndex}
            />
          )
        })
      )}
    </div>
  )
}
